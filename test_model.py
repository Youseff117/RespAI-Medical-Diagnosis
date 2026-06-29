import torch
from model import CheXNet  # تأكد أن الملف model.py موجود وفيه الكلاس ده

try:
    model = CheXNet()
    model.load_chexnet_weights("CheXNet-master/model.pth.tar")
    print("✅ تم تحميل النموذج بنجاح!")
except Exception as e:
    print("❌ حصل خطأ أثناء تحميل النموذج:")
    print(e)