import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt

# تحميل نموذج ResNet18
model = models.resnet18(pretrained=True)
model.eval()

# تحميل صورة أشعة
image_path = "xray_sample.jpg"  # لازم تكون في نفس المجلد
image = Image.open(image_path).convert('RGB')

# تجهيز الصورة
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])
img_tensor = transform(image).unsqueeze(0)

# تمرير الصورة للنموذج
with torch.no_grad():
    outputs = model(img_tensor)
    prediction = torch.argmax(outputs, 1).item()

# عرض النتيجة
plt.imshow(image)
plt.title(f"Predicted Class ID: {prediction}")
plt.axis("off")
plt.show()