import os
import json
import sqlite3
from datetime import datetime
from functools import wraps
from contextlib import contextmanager

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
import torch
import torch.nn.functional as F
import numpy as np
import skimage.transform
import torchxrayvision as xrv
import matplotlib.cm as cm

import dashboard
from result_filter import apply_clinical_filtering
from dashboard import get_top_findings

# ======================================================
# ? Environment Variables — كل الـ secrets من .env
# ======================================================
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
HEATMAP_FOLDER = os.environ.get('HEATMAP_FOLDER', 'static/heatmaps')
DATABASE = os.environ.get('DATABASE', 'respai.db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['HEATMAP_FOLDER'] = HEATMAP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HEATMAP_FOLDER, exist_ok=True)

# ======================================================
# ? AI Model
# ======================================================
model = xrv.models.DenseNet(weights="densenet121-res224-chex")
model.eval()

DOCTOR_DIAGNOSES = [
    "Normal", "Atelectasis", "Cardiomegaly", "Effusion",
    "Infiltration", "Mass", "Nodule", "Pneumonia",
    "Pneumothorax", "Consolidation", "Edema", "Emphysema",
    "Fibrosis", "Pleural_Thickening", "Hernia", "Other"
]

# ======================================================
# ? SQLite Database
# ======================================================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'patient',
                doctor_username TEXT,
                full_name TEXT,
                age TEXT,
                gender TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_username TEXT NOT NULL,
                filename TEXT NOT NULL,
                heatmap_filename TEXT,
                diagnosis TEXT,
                clinical_summary TEXT,
                analysis_time TEXT,
                flagged_count INTEGER DEFAULT 0,
                top_finding TEXT,
                results_json TEXT,
                approved INTEGER DEFAULT 0,
                approved_by TEXT,
                approved_at TEXT,
                doctor_note TEXT,
                doctor_final_diagnosis TEXT,
                medications TEXT,
                status TEXT DEFAULT 'pending',
                reject_reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()

        # Migration: add columns if the DB already existed without them
        existing_cols = {row['name'] for row in conn.execute('PRAGMA table_info(users)').fetchall()}
        for col in ('full_name', 'age', 'gender'):
            if col not in existing_cols:
                conn.execute(f'ALTER TABLE users ADD COLUMN {col} TEXT')
        conn.commit()

        # Migration: add new scan columns if the DB already existed without them
        existing_scan_cols = {row['name'] for row in conn.execute('PRAGMA table_info(scans)').fetchall()}
        if 'medications' not in existing_scan_cols:
            conn.execute('ALTER TABLE scans ADD COLUMN medications TEXT')
        if 'status' not in existing_scan_cols:
            conn.execute("ALTER TABLE scans ADD COLUMN status TEXT DEFAULT 'pending'")
            # Backfill status from the legacy 'approved' flag so existing approved
            # scans don't suddenly look 'pending' after upgrading.
            conn.execute("UPDATE scans SET status='approved' WHERE approved=1 AND (status IS NULL OR status='pending')")
            conn.execute("UPDATE scans SET status='pending' WHERE status IS NULL")
        if 'reject_reason' not in existing_scan_cols:
            conn.execute('ALTER TABLE scans ADD COLUMN reject_reason TEXT')
        conn.commit()

# ======================================================
# ? User DB helpers
# ======================================================
def db_get_user(username):
    with get_db() as conn:
        row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        return dict(row) if row else None

def db_create_user(username, password, role,
                   doctor_username=None,
                   full_name=None,
                   age=None,
                   gender=None):
    with get_db() as conn:
        conn.execute(
            '''INSERT INTO users
               (username, password, role, doctor_username, full_name, age, gender)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (username, password, role, doctor_username, full_name, age, gender)
        )
        conn.commit()

def db_get_doctor_patients(doctor_username):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT username FROM users WHERE doctor_username = ? AND role = "patient"',
            (doctor_username,)
        ).fetchall()
        return [r['username'] for r in rows]

def db_doctor_exists(doctor_username):
    with get_db() as conn:
        row = conn.execute(
            'SELECT id FROM users WHERE username = ? AND role = "doctor"',
            (doctor_username,)
        ).fetchone()
        return row is not None

# ======================================================
# ? Scan DB helpers
# ======================================================
def db_save_scan(patient_username, filename, heatmap_filename, diagnosis,
                 clinical_summary, analysis_time, flagged_count, top_finding, results):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO scans
            (patient_username, filename, heatmap_filename, diagnosis, clinical_summary,
             analysis_time, flagged_count, top_finding, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_username, filename, heatmap_filename, diagnosis,
              clinical_summary, analysis_time, flagged_count, top_finding,
              json.dumps(results)))
        conn.commit()

def db_get_patient_scans(patient_username):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM scans WHERE patient_username = ? ORDER BY id ASC',
            (patient_username,)
        ).fetchall()
        scans = []
        for r in rows:
            s = dict(r)
            s['results'] = json.loads(s['results_json']) if s['results_json'] else []
            scans.append(s)
        return scans

def db_get_scan(scan_id):
    with get_db() as conn:
        row = conn.execute('SELECT * FROM scans WHERE id = ?', (scan_id,)).fetchone()
        if row:
            s = dict(row)
            s['results'] = json.loads(s['results_json']) if s['results_json'] else []
            return s
        return None

def db_approve_scan(scan_id, approved_by, doctor_note, doctor_final_diagnosis, medications=None):
    with get_db() as conn:
        conn.execute('''
            UPDATE scans SET approved=1, status='approved', approved_by=?, approved_at=?,
            doctor_note=?, doctor_final_diagnosis=?, medications=?, reject_reason=NULL WHERE id=?
        ''', (approved_by, datetime.now().strftime('%Y-%m-%d %H:%M'),
              doctor_note or None, doctor_final_diagnosis or None, medications or None, scan_id))
        conn.commit()

def db_reject_scan(scan_id, reviewed_by, reject_reason=None):
    with get_db() as conn:
        conn.execute('''
            UPDATE scans SET approved=0, status='rejected', approved_by=?, approved_at=?,
            doctor_note=NULL, doctor_final_diagnosis=NULL, medications=NULL, reject_reason=? WHERE id=?
        ''', (reviewed_by, datetime.now().strftime('%Y-%m-%d %H:%M'), reject_reason or None, scan_id))
        conn.commit()

def db_revoke_scan(scan_id):
    with get_db() as conn:
        conn.execute('''
            UPDATE scans SET approved=0, status='pending', approved_by=NULL, approved_at=NULL,
            doctor_note=NULL, doctor_final_diagnosis=NULL, medications=NULL, reject_reason=NULL WHERE id=?
        ''', (scan_id,))
        conn.commit()

# ======================================================
# ? Init DB on startup
# ======================================================
with app.app_context():
    init_db()

# ======================================================
# Decorators & Helpers
# ======================================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def check_image_quality(image_path):
    try:
        img = Image.open(image_path).convert('L')
        arr = np.array(img).astype(np.float32)
        if arr.std() < 10:
            return False, "Image contrast is too low."
        if arr.shape[0] < 224 or arr.shape[1] < 224:
            return False, "Image resolution is too low."
        if arr.mean() < 20:
            return False, "Image is too dark."
        if arr.mean() > 235:
            return False, "Image is overexposed."
        return True, None
    except Exception:
        return False, "Invalid image."

def generate_clinical_summary(top_findings):
    if not top_findings:
        return (
            "No significant radiological findings detected. "
            "The chest X-ray appears within normal limits based on AI analysis. "
            "RespAI is an AI assistant and not a substitute for professional medical diagnosis."
        )
    names = [f["disease"] for f in top_findings]
    ar_names = [f["ar_name"] for f in top_findings]
    findings_en = names[0] if len(names) == 1 else ", ".join(names[:-1]) + f" and {names[-1]}"
    findings_ar = ar_names[0] if len(ar_names) == 1 else "، ".join(ar_names[:-1]) + f" و{ar_names[-1]}"
    top_prob = top_findings[0]["probability"]
    confidence = "with elevated confidence" if top_prob >= 70 else "with moderate confidence" if top_prob >= 55 else "with low-to-moderate confidence"
    return (
        f"Imaging findings suggest possible {findings_en} {confidence}. "
        f"الموديل رصد احتمالية وجود: {findings_ar}. "
        f"Clinical correlation and radiologist review are strongly recommended. "
        f"RespAI is an AI assistant and not a substitute for professional medical diagnosis."
    )

def generate_gradcam(img_tensor, target_index):
    activations = {}
    gradients = {}
    target_layer = model.features.norm5

    def forward_hook(module, input, output):
        activations['value'] = output

    def tensor_hook(grad):
        gradients['value'] = grad.clone()

    handle_fwd = target_layer.register_forward_hook(forward_hook)
    img_tensor = img_tensor.clone().requires_grad_(True)
    output = model(img_tensor)
    feat = activations['value']
    feat.register_hook(tensor_hook)
    model.zero_grad()
    output[0, target_index].backward()
    handle_fwd.remove()

    weights = gradients['value'].detach().mean(dim=(2, 3), keepdim=True)
    cam = F.relu((weights * feat.detach()).sum(dim=1, keepdim=True))
    cam = cam.squeeze().cpu().numpy()
    if cam.max() > 0:
        cam = cam / cam.max()
    return skimage.transform.resize(cam, (224, 224))

def save_heatmap_overlay(original_img_array, cam, save_path):
    base = original_img_array.copy()
    base = (base - base.min()) / (base.max() - base.min() + 1e-8)
    heatmap_colored = cm.jet(cam)[:, :, :3]
    overlay = np.clip(0.55 * np.stack([base] * 3, axis=-1) + 0.45 * heatmap_colored, 0, 1)
    Image.fromarray((overlay * 255).astype(np.uint8)).save(save_path)

def analyze_xray(image_path, filename):
    img = Image.open(image_path).convert("L")
    img_array = xrv.datasets.normalize(np.array(img).astype(np.float32), 255)
    img_array_resized = skimage.transform.resize(img_array, (224, 224))
    img_tensor = torch.from_numpy(img_array_resized).unsqueeze(0).unsqueeze(0).float()

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = dict(zip(model.pathologies, outputs[0].numpy()))

    name_map = {k: k for k in [
        "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass",
        "Nodule", "Pneumonia", "Pneumothorax", "Consolidation", "Edema",
        "Emphysema", "Fibrosis", "Pleural_Thickening", "Hernia"
    ]}
    mapped = {name_map[k]: float(v) for k, v in probs.items() if k in name_map}
    analyzed_results = dashboard.analyze_results(mapped)
    analyzed_results = apply_clinical_filtering(analyzed_results)
    top = get_top_findings(analyzed_results)

    diagnosis = ("? No major findings detected" if not top
                 else f"?? {len(top)} finding(s) — clinical review recommended")
    clinical_summary = generate_clinical_summary(top)

    heatmap_filename = None
    if top:
        top_disease = top[0]["disease"]
        if top_disease in model.pathologies:
            try:
                cam = generate_gradcam(img_tensor, model.pathologies.index(top_disease))
                heatmap_filename = f"heatmap_{filename}"
                save_heatmap_overlay(img_array_resized, cam,
                                     os.path.join(app.config['HEATMAP_FOLDER'], heatmap_filename))
            except Exception as e:
                print(f"Grad-CAM failed: {e}")

    return diagnosis, analyzed_results, heatmap_filename, clinical_summary

def db_get_landing_stats():
    with get_db() as conn:
        doctors = conn.execute("SELECT COUNT(*) as c FROM users WHERE role='doctor'").fetchone()['c']
        patients = conn.execute("SELECT COUNT(*) as c FROM users WHERE role='patient'").fetchone()['c']
        scans = conn.execute("SELECT COUNT(*) as c FROM scans").fetchone()['c']
        return {'doctors': doctors, 'patients': patients, 'scans': scans}
# ======================================================
# Routes
# ======================================================
@app.route('/')
def index():
    stats = db_get_landing_stats()
    return render_template('landing.html', stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password'].strip()
        role = request.form.get('role', 'patient')
        full_name = request.form.get('full_name', '').strip()
        age = request.form.get('age', '').strip()
        gender = request.form.get('gender', '').strip()

        if db_get_user(u):
            flash('Username already exists!')
            return redirect(url_for('register'))

        hashed = generate_password_hash(p)

        if role == 'doctor':
            db_create_user(u, hashed, 'doctor',
                           full_name=full_name, age=age, gender=gender)
        else:
            doctor_name = request.form.get('doctor_name', '').strip()
            if not doctor_name:
                flash('Please enter your doctor\'s username.')
                return redirect(url_for('register'))
            if not db_doctor_exists(doctor_name):
                flash('Doctor not found. Please check the doctor\'s username.')
                return redirect(url_for('register'))
            db_create_user(u, hashed, 'patient', doctor_name,
                           full_name=full_name, age=age, gender=gender)

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = db_get_user(u)
        if user and check_password_hash(user['password'], p):
            session['user'] = u
            session['role'] = user['role']
            return redirect(url_for('doctor_dashboard') if user['role'] == 'doctor' else url_for('upload_xray'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_xray():
    if request.method == 'GET':
        force_new = request.args.get('new') == '1'
        user = db_get_user(session['user'])
        if user and user['role'] == 'patient' and not force_new:
            scans = db_get_patient_scans(session['user'])
            if scans:
                last = scans[-1]
                # Keep session in sync so /download_report works even after
                # a fresh login (no POST happened in this session yet).
                session['latest_result'] = last['results']
                session['latest_diagnosis'] = last['diagnosis']
                session['image_name'] = last['filename']
                return render_template('dashboard.html',
                                       filename=last['filename'],
                                       heatmap_filename=last['heatmap_filename'],
                                       results=last['results'],
                                       diagnosis=last['diagnosis'],
                                       clinical_summary=last['clinical_summary'],
                                       analysis_time=last['analysis_time'],
                                       status=last.get('status', 'pending'),
                                       approved=bool(last.get('approved')),
                                       approved_by=last.get('approved_by'),
                                       approved_at=last.get('approved_at'),
                                       doctor_note=last.get('doctor_note'),
                                       doctor_diagnosis=last.get('doctor_final_diagnosis'),
                                       medications=last.get('medications'),
                                       reject_reason=last.get('reject_reason'))
        return render_template('upload_xray.html')

    if request.method == 'POST':

        if 'xray' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['xray']
        if file.filename == '':
            flash("Choose a valid file")
            return redirect(request.url)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            Image.open(filepath).verify()
        except Exception:
            flash("الملف المرفوع تالف أو ليس صورة صالحة")
            return redirect(request.url)

        is_valid, reason = check_image_quality(filepath)
        if not is_valid:
            flash(f"?? Image quality insufficient: {reason}")
            return redirect(request.url)

        diagnosis, results, heatmap_filename, clinical_summary = analyze_xray(filepath, file.filename)
        analysis_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        session['latest_result'] = [{**r, "probability": float(r["probability"])} for r in results]
        session['latest_diagnosis'] = diagnosis
        session['image_name'] = file.filename

        user = db_get_user(session['user'])
        if user and user['role'] == 'patient':
            db_save_scan(
                patient_username=session['user'],
                filename=file.filename,
                heatmap_filename=heatmap_filename,
                diagnosis=diagnosis,
                clinical_summary=clinical_summary,
                analysis_time=analysis_time,
                flagged_count=len([r for r in results if r['flagged']]),
                top_finding=results[0]['disease'] if results else 'N/A',
                results=[{**r, "probability": float(r["probability"])} for r in results]
            )

        # Get latest scan approval info
        scans = db_get_patient_scans(session['user'])
        last = scans[-1] if scans else {}

        return render_template('dashboard.html',
                               filename=file.filename,
                               heatmap_filename=heatmap_filename,
                               results=results,
                               diagnosis=diagnosis,
                               clinical_summary=clinical_summary,
                               analysis_time=analysis_time,
                               status=last.get('status', 'pending'),
                               approved=bool(last.get('approved')),
                               approved_by=last.get('approved_by'),
                               approved_at=last.get('approved_at'),
                               doctor_note=last.get('doctor_note'),
                               doctor_diagnosis=last.get('doctor_final_diagnosis'),
                               medications=last.get('medications'),
                               reject_reason=last.get('reject_reason'))

    return render_template('upload_xray.html')

# -------- Doctor Dashboard -------- #
@app.route('/doctor')
@login_required
def doctor_dashboard():
    user = db_get_user(session['user'])
    if not user or user['role'] != 'doctor':
        flash('Access denied')
        return redirect(url_for('upload_xray'))

    patient_usernames = db_get_doctor_patients(session['user'])
    patients_data = []
    for p in patient_usernames:
        scans = db_get_patient_scans(p)
        last = scans[-1] if scans else {}
        patients_data.append({
            'username': p,
            'scan_count': len(scans),
            'last_scan': last.get('analysis_time', 'No scans yet'),
            'last_diagnosis': last.get('diagnosis', '-'),
            'last_finding': last.get('top_finding', '-'),
        })

    return render_template('doctor_dashboard.html',
                           doctor_name=user.get('full_name') or session['user'],
                           doctor_id=session['user'],
                           patients=patients_data)

@app.route('/doctor/patient/<patient_name>')
@login_required
def patient_detail(patient_name):
    user = db_get_user(session['user'])
    if not user or user['role'] != 'doctor':
        flash('Access denied')
        return redirect(url_for('upload_xray'))

    if patient_name not in db_get_doctor_patients(session['user']):
        flash('Patient not found')
        return redirect(url_for('doctor_dashboard'))

    scans = db_get_patient_scans(patient_name)
    return render_template('patient_detail.html',
                           patient_name=patient_name,
                           scans=scans,
                           doctor_diagnoses=DOCTOR_DIAGNOSES)

# -------- Approve Scan -------- #
@app.route('/doctor/patient/<patient_name>/approve/<int:scan_id>', methods=['POST'])
@login_required
def approve_scan(patient_name, scan_id):
    user = db_get_user(session['user'])
    if not user or user['role'] != 'doctor':
        flash('Access denied')
        return redirect(url_for('upload_xray'))

    doctor_note = request.form.get('doctor_note', '').strip()
    doctor_final_diagnosis = request.form.get('doctor_final_diagnosis', '').strip()
    medications = request.form.get('medications', '').strip()
    db_approve_scan(scan_id, session['user'], doctor_note, doctor_final_diagnosis, medications)
    flash('Scan approved successfully!')
    return redirect(url_for('patient_detail', patient_name=patient_name))

# -------- Reject Scan -------- #
@app.route('/doctor/patient/<patient_name>/reject/<int:scan_id>', methods=['POST'])
@login_required
def reject_scan(patient_name, scan_id):
    user = db_get_user(session['user'])
    if not user or user['role'] != 'doctor':
        flash('Access denied')
        return redirect(url_for('upload_xray'))

    reject_reason = request.form.get('reject_reason', '').strip()
    db_reject_scan(scan_id, session['user'], reject_reason)
    flash('Scan marked as rejected. The patient has been notified to seek further review.')
    return redirect(url_for('patient_detail', patient_name=patient_name))

# -------- Revoke / Reset to Pending -------- #
@app.route('/doctor/patient/<patient_name>/revoke/<int:scan_id>', methods=['POST'])
@login_required
def revoke_scan(patient_name, scan_id):
    user = db_get_user(session['user'])
    if not user or user['role'] != 'doctor':
        flash('Access denied')
        return redirect(url_for('upload_xray'))

    db_revoke_scan(scan_id)
    flash('Scan reset to pending review.')
    return redirect(url_for('patient_detail', patient_name=patient_name))

@app.route('/download_report')
@login_required
def download_report():
    current_user = db_get_user(session['user']) or {}

    # The formal PDF report is only released once a doctor has approved the
    # scan. The on-screen preliminary AI result is still shown to the patient
    # immediately (see dashboard.html); this only affects the downloadable PDF.
    last_scan = None
    if current_user.get('role') == 'patient':
        patient_scans = db_get_patient_scans(session['user'])
        last_scan = patient_scans[-1] if patient_scans else None

    # Pull results from the DB record instead of relying solely on the
    # session, since the session may be empty after a fresh login/GET
    # even though an approved scan already exists.
    results = (last_scan or {}).get('results') or session.get('latest_result')
    if not results:
        flash('No results available')
        return redirect(url_for('upload_xray'))

    if current_user.get('role') == 'patient':
        status = (last_scan or {}).get('status', 'pending')
        if status != 'approved':
            if status == 'rejected':
                flash('This case requires further medical review. A PDF report is not available yet.')
            else:
                flash('This result is still pending doctor approval. The PDF report will be available once approved.')
            return redirect(url_for('upload_xray'))
    doctor_name = None
    if current_user.get('role') == 'patient' and current_user.get('doctor_username'):
        doctor = db_get_user(current_user['doctor_username'])
        if doctor:
            doctor_name = doctor.get('full_name') or doctor.get('username')

    patient_info = {
        "name": current_user.get('full_name') or session['user'],
        "age": current_user.get('age') or '',
        "gender": current_user.get('gender') or '',
        "medical_id": f"PID-{session['user']}"
    }

    pdf_buffer = dashboard.generate_pdf_report(
        results,
        patient_info=patient_info,
        doctor_name=doctor_name
    )
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"RespAI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )

# ======================================================
# ? Force UTF-8 charset on all HTML responses
# ======================================================
@app.after_request
def add_charset(response):
    if response.mimetype == 'text/html':
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')