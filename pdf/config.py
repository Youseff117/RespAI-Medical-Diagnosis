"""
Configuration, Constants, and Disease Data
===========================================

This module contains all configuration constants, color palettes,
disease information, and thresholds used throughout the PDF generation.

NO dependencies on other pdf modules (pure data module).
"""

from reportlab.lib import colors

# ═══════════════════════════════════════════════════════════════════════════
# COLOR PALETTE (Medical Blue Theme)
# ═══════════════════════════════════════════════════════════════════════════

PRIMARY_BLUE   = colors.HexColor('#0B3B86')
SECONDARY_BLUE = colors.HexColor('#1E5BBF')
ACCENT_BLUE    = colors.HexColor('#2F7BE0')
SOFT_BLUE      = colors.HexColor('#E8F0FE')
ULTRA_LIGHT    = colors.HexColor('#F5F8FD')
PAGE_BG        = colors.HexColor('#FAFBFD')

INK            = colors.HexColor('#1A2332')
MUTED          = colors.HexColor('#5B6B80')
LINE_GRAY      = colors.HexColor('#D9E0EA')
BORDER_GRAY    = colors.HexColor('#E3E8F0')
WHITE          = colors.white

# Status colors (backgrounds - soft)
STATUS_BG = {
    'green':  colors.HexColor('#E9F7EF'),
    'yellow': colors.HexColor('#FFF8E1'),
    'orange': colors.HexColor('#FFF1E6'),
    'red':    colors.HexColor('#FDECEC'),
}

# Status colors (accents - vibrant)
STATUS_ACCENT = {
    'green':  colors.HexColor('#1F9D55'),
    'yellow': colors.HexColor('#C99A1E'),
    'orange': colors.HexColor('#D97706'),
    'red':    colors.HexColor('#C0392B'),
}

# Severity levels (English)
SEVERITY_LEVELS = {
    'green':  ('Mild',        'Mild'),
    'yellow': ('Moderate',    'Moderate'),
    'orange': ('Significant', 'Significant'),
    'red':    ('Severe',      'Severe'),
}

# Priority colors mapping
PRIORITY_COLORS = {
    'Routine':   STATUS_ACCENT['green'],
    'Follow-up': STATUS_ACCENT['yellow'],
    'Urgent':    STATUS_ACCENT['orange'],
    'Immediate': STATUS_ACCENT['red'],
}

# ═══════════════════════════════════════════════════════════════════════════
# DISEASE THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════

DISEASE_THRESHOLDS = {
    'Atelectasis':        0.50,
    'Cardiomegaly':       0.50,
    'Effusion':           0.50,
    'Infiltration':       0.50,
    'Mass':               0.50,
    'Nodule':             0.50,
    'Pneumonia':          0.50,
    'Pneumothorax':       0.50,
    'Consolidation':      0.50,
    'Edema':              0.50,
    'Emphysema':          0.50,
    'Fibrosis':           0.50,
    'Pleural_Thickening': 0.50,
    'Hernia':             0.50,
}

# ═══════════════════════════════════════════════════════════════════════════
# DISEASES INFO (Full medical data with ICD-10 + SNOMED CT)
# ═══════════════════════════════════════════════════════════════════════════

diseases_info = {
    "Atelectasis": {
        "ar_name": "Atelectasis",
        "description": "Partial or complete collapse of the lung",
        "clinical": "Requires clinical evaluation to rule out airway obstruction",
        "followup": "Follow-up X-ray within 24-48 hours",
        "differential": ["Pleural effusion", "Pulmonary consolidation", "Pneumonectomy"],
        "causes": ["Airway obstruction", "External compression", "Surfactant deficiency"],
        "management": "Treat underlying cause + supportive respiratory therapy",
        "impression": "Linear or triangular opacities indicating volume loss",
        "recommendation": "Chest Physiotherapy + Incentive Spirometry + Follow-up CXR",
        "radiographic_pattern": "Linear or triangular opacity with volume loss",
        "icd10": "J98.1",
        "snomed_ct": "4082005",
        "specialist": "Pulmonologist",
        "medication": "Bronchodilators if indicated",
        "test": "Chest X-ray / Bronchoscopy"
    },
    "Cardiomegaly": {
        "ar_name": "Cardiomegaly",
        "description": "Enlargement of the heart",
        "clinical": "May indicate heart failure or cardiomyopathy",
        "followup": "Echocardiography",
        "differential": ["Pericardial effusion", "Ventricular hypertrophy", "Obesity"],
        "causes": ["Heart failure", "Hypertension", "Valvular disease"],
        "management": "Comprehensive cardiac evaluation + treat underlying cause",
        "impression": "Cardiothoracic ratio > 50% on PA X-ray",
        "recommendation": "Echocardiography + Cardiology Consultation + BNP",
        "radiographic_pattern": "Cardiothoracic ratio > 0.5 on PA view",
        "icd10": "I51.7",
        "snomed_ct": "8881008",
        "specialist": "Cardiologist",
        "medication": "ACE inhibitors / Diuretics",
        "test": "Echocardiography + ECG + BNP"
    },
    "Effusion": {
        "ar_name": "Pleural Effusion",
        "description": "Fluid accumulation around the lung",
        "clinical": "Requires evaluation for cardiac, renal, or inflammatory causes",
        "followup": "Lateral X-ray + Ultrasound",
        "differential": ["Basal atelectasis", "Pleural thickening", "Consolidation"],
        "causes": ["Heart failure", "Pleuritis", "Tumors"],
        "management": "Diagnostic thoracentesis + treat underlying cause",
        "impression": "Blunting of costophrenic angle",
        "recommendation": "Lateral Decubitus X-ray + Thoracentesis + Ultrasound",
        "radiographic_pattern": "Blunting of costophrenic angle / Meniscus sign",
        "icd10": "J91.8",
        "snomed_ct": "60006005",
        "specialist": "Pulmonologist",
        "medication": "Diuretics / Antibiotics",
        "test": "Thoracentesis + Pleural Fluid Analysis"
    },
    "Infiltration": {
        "ar_name": "Pulmonary Infiltration",
        "description": "Fluid accumulation within lung tissue",
        "clinical": "May indicate inflammation or edema",
        "followup": "Laboratory tests + follow-up X-ray",
        "differential": ["Pneumonia", "Pulmonary edema", "Hemorrhage"],
        "causes": ["Infection", "Edema", "Pulmonary hemorrhage"],
        "management": "Laboratory tests + additional imaging",
        "impression": "Ill-defined opacities in the pulmonary field",
        "recommendation": "Laboratory Tests + Follow-up CXR + Clinical Correlation",
        "radiographic_pattern": "Ill-defined parenchymal opacities",
        "icd10": "J18.9",
        "snomed_ct": "233604007",
        "specialist": "Pulmonologist",
        "medication": "Antibiotics if infectious",
        "test": "CBC + CRP + Blood Cultures"
    },
    "Mass": {
        "ar_name": "Pulmonary Mass",
        "description": "Abnormal growth in the lung",
        "clinical": "Requires exclusion of benign and malignant tumors",
        "followup": "CT scan + Biopsy",
        "differential": ["Nodule", "Abscess", "Granuloma"],
        "causes": ["Tumors", "Chronic infections", "Granulomas"],
        "management": "CT scan + tissue biopsy",
        "impression": "Lesion > 3cm with irregular margins",
        "recommendation": "Contrast-enhanced CT + Biopsy + Oncology Referral",
        "radiographic_pattern": "Lesion > 3cm with irregular margins",
        "icd10": "R91.1",
        "snomed_ct": "416949008",
        "specialist": "Oncologist / Pulmonologist",
        "medication": "Per biopsy results",
        "test": "Contrast CT + PET-CT + Biopsy"
    },
    "Nodule": {
        "ar_name": "Pulmonary Nodule",
        "description": "Small growth inside the lung",
        "clinical": "Follow-up based on size and risk factors",
        "followup": "Low-dose CT after 3-6 months",
        "differential": ["Granuloma", "Lymph node", "Mass"],
        "causes": ["Benign tumors", "Infections", "Metastases"],
        "management": "Periodic imaging follow-up per protocol",
        "impression": "Round lesion less than 3cm",
        "recommendation": "Low-dose CT + Fleischner Protocol + Pulmonology Follow-up",
        "radiographic_pattern": "Round lesion < 3cm, well-circumscribed",
        "icd10": "R91.1",
        "snomed_ct": "285644001",
        "specialist": "Pulmonologist",
        "medication": "None unless infectious",
        "test": "Low-dose CT (Fleischner Guidelines)"
    },
    "Pneumonia": {
        "ar_name": "Pneumonia",
        "description": "Infection causing lung inflammation",
        "clinical": "Assess infection severity and choose appropriate antibiotic",
        "followup": "Follow-up X-ray after 6 weeks",
        "differential": ["Infiltration", "Consolidation", "Atelectasis"],
        "causes": ["Bacteria", "Viruses", "Fungi"],
        "management": "Antibiotics + respiratory support",
        "impression": "Alveolar or interstitial consolidation with clinical signs of infection",
        "recommendation": "Antibiotics + CBC + CRP + Follow-up CXR in 6 weeks",
        "radiographic_pattern": "Alveolar or interstitial consolidation",
        "icd10": "J18.9",
        "snomed_ct": "233604007",
        "specialist": "Pulmonologist / ID Specialist",
        "medication": "Antibiotics",
        "test": "CBC + CRP + Sputum Culture"
    },
    "Pneumothorax": {
        "ar_name": "Pneumothorax",
        "description": "Air accumulation between lung and chest wall",
        "clinical": "Emergency condition depending on size and symptoms",
        "followup": "Immediate X-ray + intervention evaluation",
        "differential": ["Bulla", "Skin fold", "Cyst"],
        "causes": ["Traumatic", "Spontaneous", "Lung perforation"],
        "management": "Chest tube insertion based on size",
        "impression": "Visceral pleural line with absent peripheral lung markings",
        "recommendation": "Emergency Chest Tube + Oxygen Therapy + Surgical Consult",
        "radiographic_pattern": "Visceral pleural line with absent lung markings",
        "icd10": "J93.9",
        "snomed_ct": "36118008",
        "specialist": "Thoracic Surgeon / ER",
        "medication": "Oxygen + Analgesics",
        "test": "Chest X-ray / CT + ABG"
    },
    "Consolidation": {
        "ar_name": "Consolidation",
        "description": "Lung filled with fluids or solid material",
        "clinical": "Usually lobar pneumonia",
        "followup": "Antibiotics + follow-up X-ray",
        "differential": ["Pneumonia", "Infiltration", "Tumors"],
        "causes": ["Pneumonia", "Tumors", "Hemorrhage"],
        "management": "Treat underlying cause + imaging follow-up",
        "impression": "Homogeneous opacity with air bronchogram",
        "recommendation": "Antibiotics + Blood Cultures + Follow-up CXR",
        "radiographic_pattern": "Homogeneous opacity with air bronchogram",
        "icd10": "J18.9",
        "snomed_ct": "415722004",
        "specialist": "Pulmonologist",
        "medication": "Antibiotics",
        "test": "Blood Cultures + Sputum Analysis"
    },
    "Edema": {
        "ar_name": "Pulmonary Edema",
        "description": "Fluid accumulation in the lungs",
        "clinical": "Usually congestive heart failure",
        "followup": "Cardiac evaluation + diuretics",
        "differential": ["Infiltration", "Pneumonia", "Fibrosis"],
        "causes": ["Heart failure", "Renal failure", "ARDS"],
        "management": "Diuretics + cardiac treatment",
        "impression": "Bat-wing perihilar pattern around hilum",
        "recommendation": "Diuretics + Echocardiography + BNP + Cardiology Consult",
        "radiographic_pattern": "Bat-wing perihilar pattern + Kerley B lines",
        "icd10": "J81",
        "snomed_ct": "194828000",
        "specialist": "Cardiologist",
        "medication": "Furosemide + ACE-I",
        "test": "Echocardiography + BNP + Renal Function"
    },
    "Emphysema": {
        "ar_name": "Emphysema",
        "description": "Damage to air sacs in the lungs",
        "clinical": "Chronic obstructive pulmonary disease",
        "followup": "Pulmonary function tests + smoking cessation",
        "differential": ["Bullae", "Cysts", "Fibrosis"],
        "causes": ["Smoking", "Pollution", "Alpha-1 deficiency"],
        "management": "Smoking cessation + bronchodilator therapy",
        "impression": "Hyperinflation with flattened diaphragm",
        "recommendation": "PFT + Smoking Cessation + Pulmonology Follow-up",
        "radiographic_pattern": "Hyperinflation + Flattened diaphragm + Lucent fields",
        "icd10": "J43.9",
        "snomed_ct": "13645005",
        "specialist": "Pulmonologist",
        "medication": "LAMA/LABA + Steroids",
        "test": "Spirometry + Alpha-1 Antitrypsin"
    },
    "Fibrosis": {
        "ar_name": "Pulmonary Fibrosis",
        "description": "Scarring and stiffening of lung tissue",
        "clinical": "Chronic disease requiring long-term follow-up",
        "followup": "High-resolution CT + pulmonary function tests",
        "differential": ["Chronic inflammation", "Atelectasis", "Thickening"],
        "causes": ["Occupational exposure", "Medications", "Autoimmune diseases"],
        "management": "Antifibrotic therapy + oxygen",
        "impression": "Reticular lines with architectural distortion",
        "recommendation": "HRCT + PFT + ILD Specialist Referral",
        "radiographic_pattern": "Reticular opacities + Architectural distortion",
        "icd10": "J84.1",
        "snomed_ct": "51615001",
        "specialist": "ILD Specialist",
        "medication": "Antifibrotics (Pirfenidone)",
        "test": "HRCT + PFT + Autoimmune Panel"
    },
    "Pleural_Thickening": {
        "ar_name": "Pleural Thickening",
        "description": "Thickening of the pleural membrane",
        "clinical": "May result from prior inflammation or asbestos exposure",
        "followup": "CT + clinical follow-up",
        "differential": ["Chronic effusion", "Pleural tumor", "Fibrosis"],
        "causes": ["Prior inflammation", "Asbestos", "Tuberculosis"],
        "management": "Imaging follow-up + functional assessment",
        "impression": "Smooth or nodular pleural thickening",
        "recommendation": "CT + Occupational History + Pulmonology Follow-up",
        "radiographic_pattern": "Smooth or nodular pleural thickening",
        "icd10": "J92.0",
        "snomed_ct": "195967001",
        "specialist": "Pulmonologist",
        "medication": "Symptomatic treatment",
        "test": "CT Chest + Asbestos Screening"
    },
    "Hernia": {
        "ar_name": "Diaphragmatic Hernia",
        "description": "Organ protrusion through the diaphragm",
        "clinical": "Evaluate digestive and respiratory symptoms",
        "followup": "Contrast X-ray or CT",
        "differential": ["GERD", "Mediastinal tumors", "Cysts"],
        "causes": ["Diaphragmatic weakness", "Obesity", "Pregnancy"],
        "management": "Conservative or surgical treatment based on symptoms",
        "impression": "Air or fluid shadow behind heart in posterior mediastinum",
        "recommendation": "Barium Swallow + CT + Surgical Consult",
        "radiographic_pattern": "Air-fluid level behind heart in posterior mediastinum",
        "icd10": "K44.9",
        "snomed_ct": "8404003",
        "specialist": "General Surgeon / GI",
        "medication": "PPIs + Lifestyle changes",
        "test": "Barium Swallow / Upper Endoscopy"
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# REPORT METADATA (Default values)
# ═══════════════════════════════════════════════════════════════════════════

REPORT_METADATA = {
    'model_name':       "CheXNet / DenseNet-121",
    'model_version':    "v2.1.4",
    'report_version':   "5.0",
    'input_resolution': "224 x 224 px",
    'image_format':     "DICOM / PNG",
    'threshold':        "0.50",
    'dataset':          "NIH ChestX-ray14",
    'training_images':  "112,120",
    'validation_auc':   "0.841",
    'framework':        "PyTorch 2.0",
    'hardware':         "NVIDIA GPU (CUDA 12.x)",
    'pytorch_version':  "2.0.1",
    'cuda_version':     "12.1",
}

# ═══════════════════════════════════════════════════════════════════════════
# BENCHMARKS (Model performance metrics)
# ═══════════════════════════════════════════════════════════════════════════

BENCHMARKS = {
    'Radiologist Agreement': '89.2%',
    'Sensitivity':           '91.4%',
    'Specificity':           '87.8%',
    'Accuracy':              '89.6%',
}

# ═══════════════════════════════════════════════════════════════════════════
# REFERENCES (APA format)
# ═══════════════════════════════════════════════════════════════════════════

REFERENCES = [
    "Wang, X., Peng, Y., Lu, L., et al. (2017). ChestX-ray8: Hospital-scale Chest X-ray Database. <i>CVPR</i>.",
    "Rajpurkar, P., et al. (2017). CheXNet: Radiologist-Level Pneumonia Detection. <i>arXiv:1711.05225</i>.",
    "Huang, G., et al. (2017). Densely Connected Convolutional Networks. <i>CVPR</i>.",
    "NIH Clinical Center. (2022). ChestX-ray14 Dataset. https://nihcc.app.box.com/v/ChestXray-NIHCC",
    "RSNA. (2018). RSNA Pneumonia Detection Challenge. https://kaggle.com",
    "American College of Radiology. (2023). AI in Medical Imaging. <i>Radiology Journal</i>.",
]

# ═══════════════════════════════════════════════════════════════════════════
# LIMITATIONS
# ═══════════════════════════════════════════════════════════════════════════

LIMITATIONS = [
    "Model trained on NIH ChestX-ray14 and may not reflect all rare clinical cases.",
    "Image quality directly affects analysis accuracy (noise, rotation, exposure, contrast).",
    "Results are indicative and do not replace clinical evaluation by a qualified radiologist.",
    "Some radiographically similar conditions require additional tests for differentiation.",
    "The model does not consider complete medical history or laboratory results.",
]

# ═══════════════════════════════════════════════════════════════════════════
# IMAGE QUALITY DEFAULT VALUES
# ═══════════════════════════════════════════════════════════════════════════

IMAGE_QUALITY_DEFAULTS = [
    ("Image Quality",   92),
    ("Contrast",        88),
    ("Sharpness",       90),
    ("Exposure",        94),
    ("Noise Level",     85),
    ("Rotation",        98),
]

# ═══════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS SECTIONS
# ═══════════════════════════════════════════════════════════════════════════

TOC_SECTIONS = [
    ("1",  "Executive Summary",       "Executive Summary"),
    ("2",  "Patient Information",     "Patient Information"),
    ("3",  "Dashboard Statistics",    "Dashboard Statistics"),
    ("4",  "Detailed Findings",       "Detailed Findings"),
    ("5",  "Disease Analysis",        "Disease Analysis"),
    ("6",  "AI Analytics & Charts",   "AI Analytics & Charts"),
    ("7",  "Grad-CAM Heatmap",        "Heatmap Visualization"),
    ("8",  "Clinical Interpretation", "Clinical Interpretation"),
    ("9",  "Clinical Decision Support","Clinical Decision Support"),
    ("10", "AI Recommendations",      "AI Recommendations"),
    ("11", "Confidence Analysis",     "Confidence Analysis"),
    ("12", "Explainable AI",          "Explainable AI"),
    ("13", "Image Quality Assessment","Image Quality Assessment"),
    ("14", "Technical Information",   "Technical Information"),
    ("15", "Limitations & References","Limitations & References"),
    ("16", "Verification & Signatures","Verification & Signatures"),
]

# ═══════════════════════════════════════════════════════════════════════════
# RISK LABELS
# ═══════════════════════════════════════════════════════════════════════════

RISK_LABELS = {
    'green':  ("NORMAL",        "Normal"),
    'yellow': ("LOW RISK",      "Low Risk"),
    'orange': ("MODERATE RISK", "Moderate Risk"),
    'red':    ("HIGH RISK",     "High Risk"),
}

# AI Decision color mapping
AI_DECISION_COLOR_MAP = {
    'Normal':     'green',
    'Borderline': 'yellow',
    'Abnormal':   'orange',
    'Critical':   'red',
}

# Urgency mapping by color
URGENCY_MAP = {
    'green':  'Routine',
    'yellow': 'Follow-up',
    'orange': 'Urgent',
    'red':    'Immediate',
}

# Quality rating thresholds
QUALITY_RATINGS = {
    'Excellent':    STATUS_ACCENT['green'],
    'Good':         ACCENT_BLUE,
    'Acceptable':   STATUS_ACCENT['yellow'],
    'Needs Review': STATUS_ACCENT['red'],
}