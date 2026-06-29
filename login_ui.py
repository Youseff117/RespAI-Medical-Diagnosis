import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from PIL import Image, ImageTk
import torch
import torchvision.transforms as transforms
from torchvision import models

# ملف المستخدمين
USERS_FILE = "users.json"

# تحميل المستخدمين
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

# حفظ المستخدمين
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

# تحليل الأشعة
def analyze_image(image_path, result_label, image_label):
    # تحميل النموذج
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()

    # تحميل الصورة وتحويلها
    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    img_tensor = transform(image).unsqueeze(0)

    # التحليل (عشوائي كمثال)
    with torch.no_grad():
        outputs = model(img_tensor)
        prediction = torch.argmax(outputs, 1).item()

    # النتيجة كمثال
    result = "🚨 احتمال وجود مشكلة" if prediction % 2 == 0 else "✅ الأشعة تبدو سليمة"

    # عرض الصورة
    img_resized = image.resize((150, 150))
    img_tk = ImageTk.PhotoImage(img_resized)
    image_label.config(image=img_tk)
    image_label.image = img_tk

    # عرض النتيجة
    result_label.config(text="النتيجة: " + result)

# نافذة تحليل الأشعة
def open_analysis_window():
    analysis_window = tk.Toplevel()
    analysis_window.title("تحليل الأشعة")
    analysis_window.geometry("350x400")

    tk.Label(analysis_window, text="أهلاً بك في وحدة التحليل", font=("Arial", 14)).pack(pady=10)

    image_label = tk.Label(analysis_window)
    image_label.pack()

    result_label = tk.Label(analysis_window, text="", font=("Arial", 12))
    result_label.pack(pady=10)

    def choose_image():
        filepath = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if filepath:
            analyze_image(filepath, result_label, image_label)

    tk.Button(analysis_window, text="اختر صورة أشعة", command=choose_image).pack(pady=20)

# تسجيل الدخول
def login():
    username = entry_username.get()
    password = entry_password.get()
    users = load_users()

    if username in users and users[username] == password:
        messagebox.showinfo("تم الدخول", f"أهلًا {username} 👋")
        window.destroy()
        open_analysis_window()
    else:
        messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة!")

# إنشاء حساب
def register():
    username = entry_username.get()
    password = entry_password.get()
    users = load_users()

    if not username or not password:
        messagebox.showwarning("تحذير", "املأ جميع البيانات!")
        return

    if username in users:
        messagebox.showerror("خطأ", "اسم المستخدم موجود بالفعل!")
    else:
        users[username] = password
        save_users(users)
        messagebox.showinfo("تم التسجيل", "تم إنشاء الحساب بنجاح!")

# واجهة التسجيل
window = tk.Tk()
window.title("تسجيل المستخدم - RespAI")
window.geometry("300x250")
window.resizable(False, False)

tk.Label(window, text="مرحبا بك في RespAI", font=("Arial", 14)).pack(pady=10)

tk.Label(window, text="اسم المستخدم:").pack()
entry_username = tk.Entry(window)
entry_username.pack()

tk.Label(window, text="كلمة المرور:").pack()
entry_password = tk.Entry(window, show="*")
entry_password.pack()

tk.Button(window, text="تسجيل دخول", command=login).pack(pady=5)
tk.Button(window, text="إنشاء حساب جديد", command=register).pack(pady=5)

window.mainloop()