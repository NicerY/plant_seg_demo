from dataset import SegmentationDataset
from torch.utils.data import DataLoader
from pspnet import PSPNet
from tqdm import tqdm
from random import random



if __name__ == '__main__':

    # 网络参数配置
    epochs = 1000

    net = PSPNet().cuda()

    # 加载训练数据和验证数据
    train_dataset = SegmentationDataset(mode='train')
    val_dataset = SegmentationDataset(mode='val')

    # 使用DataLoader封装训练数据和验证数据
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=0)

    # 训练过程
    for i in range(epochs):
        pbar = tqdm(train_loader)
        for _,(images, masks) in enumerate(pbar): # BCHW
            images = images.cuda()
            masks = masks.cuda()
            print(images.size())
            # print(masks.size())
            results = net(images)
            print(type(results))
            # Description will be displayed on the left
            pbar.set_description(f'Epoch {i}')
            # Postfix will be displayed on the right, formatted automatically based on argument's datatype
            pbar.set_postfix(loss=random(),acc=random())