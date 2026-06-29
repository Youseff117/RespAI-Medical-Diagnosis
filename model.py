import torch
import torch.nn as nn
import torchvision.models as models
from collections import OrderedDict

class CheXNet(nn.Module):
    def __init__(self, num_classes=14):
        super(CheXNet, self).__init__()
        # الطريقة الحديثة لتعطيل التحميل المسبق
        self.densenet121 = models.densenet121(weights=None)
        num_ftrs = self.densenet121.classifier.in_features
        self.densenet121.classifier = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.densenet121(x)

    def load_chexnet_weights(self, path):
        checkpoint = torch.load(path, map_location=torch.device('cpu'))

        # دعم لتحميل الأوزان سواء كان الملف يحتوي على 'state_dict' أو لا
        state_dict = checkpoint['state_dict'] if 'state_dict' in checkpoint else checkpoint

        # إزالة بادئة "module." إن وجدت
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] if k.startswith('module.') else k
            new_state_dict[name] = v

        # تحميل الأوزان مع السماح بتجاهل القيم الناقصة أو الزائدة
        self.load_state_dict(new_state_dict, strict=False)