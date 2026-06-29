import torch
import torch.nn as nn
import torchvision.models as models

class CheXNet(nn.Module):
    def __init__(self, num_classes=14):
        super(CheXNet, self).__init__()
        self.densenet = models.densenet121(pretrained=False)
        num_features = self.densenet.classifier.in_features
        self.densenet.classifier = nn.Linear(num_features, num_classes)

    def forward(self, x):
        return self.densenet(x)

    def load_chexnet_weights(self, path):
        checkpoint = torch.load(path, map_location=torch.device('cpu'))
        state_dict = checkpoint['state_dict']
        from collections import OrderedDict
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] if k.startswith('module.') else k
            new_state_dict[name] = v
        self.load_state_dict(new_state_dict)