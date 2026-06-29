import os
from torchvision.datasets import ImageFolder
from torchvision import transforms
from torch.utils.data import DataLoader

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models

# ======================
# Dataset Path
# ======================

path = r"C:\Users\nour\Downloads\archive\chest_xray\train"

print("Checking dataset path...")
print("Exists:", os.path.exists(path))

if not os.path.exists(path):
    print("ERROR: Dataset path is wrong!")
    exit()

# ======================
# Data Preparation
# ======================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

train_dataset = ImageFolder(
    root=path,
    transform=transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
)

print("Classes:", train_dataset.classes)
print("عدد الصور:", len(train_dataset))

# ======================
# Device
# ======================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using:", device)

# ======================
# Model
# ======================

model = models.densenet121(weights="DEFAULT")
model.classifier = nn.Linear(
    model.classifier.in_features,
    2
)

model = model.to(device)

# ======================
# Loss Function
# ======================

criterion = nn.CrossEntropyLoss()

# ======================
# Optimizer
# ======================

optimizer = optim.Adam(
    model.parameters(),
    lr=0.0001
)

# ======================
# Training
# ======================

epochs = 1

print("Starting Training...")

for epoch in range(epochs):

    model.train()

    running_loss = 0.0

    for batch_idx, (images, labels) in enumerate(train_loader):

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        if batch_idx % 50 == 0:
            print(
                f"Epoch {epoch+1}/{epochs} | "
                f"Batch {batch_idx}/{len(train_loader)} | "
                f"Loss: {loss.item():.4f}"
            )

    print(
        f"Epoch {epoch+1}/{epochs} Finished | "
        f"Total Loss: {running_loss:.4f}"
    )

# ======================
# Save Model
# ======================

torch.save(
    model.state_dict(),
    "model.pth"
)

print("Model saved successfully!")