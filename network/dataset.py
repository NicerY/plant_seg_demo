import cv2
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import functional as F
import numpy as np
import random
import os

class SegmentationDataset(Dataset):
    def __init__(self, mode):
        self.image_path = f'./plant_data/img_dir/{mode}'
        self.mask_path = f'./plant_data/ann_dir/{mode}'
        self.image_list = sorted(os.listdir(self.image_path))
        self.mask_list = sorted(os.listdir(self.mask_path))
        self.mean = np.array([123.675, 116.28, 103.53])/255
        self.std = np.array([58.395, 57.12, 57.375])/255

    def augmentate(self, image, mask):

        # 归一化,F.to_tensor会自动缩放到0-1
        image = F.to_tensor(image) # ndarray为HWC,tensor为CHW
        mask = F.to_tensor(mask)
        image = F.normalize(image, self.mean, self.std)

        # 随机水平翻转
        image_mask = torch.cat([image, mask], dim=0)
        if random.uniform(0, 1) > 0.5:
            image_mask = F.hflip(image_mask)
        image = image_mask[:3,:,:] # [3, 750, 1000]
        mask = image_mask[3,:,:] # [750, 1000]

        return image,mask

    def __getitem__(self, index):
        image = cv2.imread(os.path.join(self.image_path, self.image_list[index]))
        mask = cv2.imread(os.path.join(self.mask_path, self.mask_list[index]), cv2.IMREAD_GRAYSCALE)
        image,mask = self.augmentate(image, mask)

        return image, mask

    def __len__(self):
        return len(self.image_list)


if __name__ == '__main__':
    # 加载训练数据和验证数据
    train_dataset = SegmentationDataset(mode='train')
    val_dataset = SegmentationDataset(mode='val')

    # 使用DataLoader封装训练数据和验证数据
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=2)

    # 获取第一个batch的数据
    for images, masks in train_loader:
        print(len(images))
        print(images[0].shape)


    # 获取第一个样本的数据
    # image, mask = train_dataset[0]
    # print(images[0].shape)
    # print(mask.shape)