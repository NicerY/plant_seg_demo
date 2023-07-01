import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet50,ResNet50_Weights
from torchsummary import summary

class Bottleneck_1(nn.Module):
    def __init__(self, in_channels, out_channels, mid_channels, stride) -> None:
        super().__init__()

        self.left = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=mid_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.Conv2d(in_channels=mid_channels, out_channels=mid_channels, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.Conv2d(in_channels=mid_channels, out_channels=out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels)
        )

        self.right = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride, padding=0, bias=False),
            nn.BatchNorm2d(out_channels)
        )

        self.relu = nn.ReLU(inplace=True)

    def forward(self,x):
        out = self.left(x) + self.right(x)
        out = self.relu(out)
        return out

class Bottleneck_2(nn.Module):
    def __init__(self, in_channels, mid_channels) -> None:
        super().__init__()

        self.left = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=mid_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.Conv2d(in_channels=mid_channels, out_channels=mid_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.Conv2d(in_channels=mid_channels, out_channels=in_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(in_channels)
        )

        self.relu = nn.ReLU(inplace=True)
    
    def forward(self,x):
        out = self.left(x) + x
        out = self.relu(out)
        return out

class Resnet50(nn.Module): # 没有contract_dilation (1, 1, 2, 4)
    def __init__(self) -> None:
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)

        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = nn.Sequential(
            Bottleneck_1(in_channels=64, out_channels=256, mid_channels=64, stride=1),
            Bottleneck_2(in_channels=256, mid_channels=64),
            Bottleneck_2(in_channels=256, mid_channels=64)
        )
        
        self.layer2 = nn.Sequential(
            Bottleneck_1(in_channels=256, out_channels=512, mid_channels=128, stride=2),
            Bottleneck_2(in_channels=512, mid_channels=128),
            Bottleneck_2(in_channels=512, mid_channels=128),
            Bottleneck_2(in_channels=512, mid_channels=128)
        )

        self.layer3 = nn.Sequential(
            Bottleneck_1(in_channels=512, out_channels=1024, mid_channels=256, stride=1),
            Bottleneck_2(in_channels=1024, mid_channels=256),
            Bottleneck_2(in_channels=1024, mid_channels=256),
            Bottleneck_2(in_channels=1024, mid_channels=256),
            Bottleneck_2(in_channels=1024, mid_channels=256),
            Bottleneck_2(in_channels=1024, mid_channels=256)
        )

        self.layer4 = nn.Sequential(
            Bottleneck_1(in_channels=1024, out_channels=2048, mid_channels=512, stride=1),
            Bottleneck_2(in_channels=2048, mid_channels=512),
            Bottleneck_2(in_channels=2048, mid_channels=512)
        )

    def forward(self, x):
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.maxpool(out)
        layer1_out = self.layer1(out)
        layer2_out = self.layer2(layer1_out)
        layer3_out = self.layer3(layer2_out)
        layer4_out = self.layer4(layer3_out)

        return [out, layer1_out, layer2_out, layer3_out, layer4_out]

class FCN(nn.Module):
    def __init__(self, in_channels, out_channels, mid_channels) -> None:
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Dropout2d(p=0.1),
            nn.Conv2d(mid_channels, out_channels, kernel_size=1)
        )

    def forward(self, x):
        out = self.net(x)

        return out


class PSPModule(nn.Module):
    def __init__(self, in_channels, pool_sizes):
        super(PSPModule, self).__init__()
        self.pool_sizes = pool_sizes
        self.stages = nn.ModuleList([
            nn.Sequential(
                nn.AdaptiveAvgPool2d(output_size=(pool_size, pool_size)),
                nn.Conv2d(in_channels, in_channels // len(pool_sizes), kernel_size=1),
                nn.BatchNorm2d(in_channels // len(pool_sizes)),
                nn.ReLU(inplace=True)
            ) for pool_size in pool_sizes
        ])
        self.conv = nn.Conv2d(in_channels * 2, in_channels, kernel_size=1)
        self.relu = nn.ReLU(inplace=True) 

    def forward(self, x):
        h, w = x.shape[2], x.shape[3] # NCHW
        
        pool_outs = [F.interpolate(stage(x), size=(h, w), mode='bilinear', align_corners=False) for stage in self.stages]
        out = torch.cat([x] + pool_outs, dim=1)
        out = self.conv(out)
        out = self.relu(out)
        return out

class PSPNet(nn.Module):
    def __init__(self, num_classes=21):
        super(PSPNet, self).__init__()
        self.resnet = Resnet50()
        self.pyramid_pooling = PSPModule(2048, [1,2,3,6])
        self.final_conv = FCN(2048,num_classes,512)
        self.auxiliary = FCN(1024,num_classes,256)

    def forward(self, x):
        resnet_out = self.resnet(x)
        auxiliary = self.auxiliary(resnet_out[3])
        auxiliary = F.interpolate(auxiliary, size=(1000, 750), mode='bilinear', align_corners=False)
        out = self.pyramid_pooling(resnet_out[4])
        out = self.final_conv(out)
        out = F.interpolate(out, size=(1000, 750), mode='bilinear', align_corners=False)
        return auxiliary,out

# imgs=torch.randn([2,3,1000,750])
# net = PSPNet()
# # print(net)
# print(net(imgs)[0].size())
# print(net(imgs)[1].size())