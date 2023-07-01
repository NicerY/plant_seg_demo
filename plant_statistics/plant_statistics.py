import cv2
import yaml
import numpy as np
import os

yaml_path = './config.yaml'

def img_statistics(img_result_path):
    with open(img_result_path) as f:
        img_result = f.readline().replace('[','').replace(']','').replace(' ','')

    class0_number = int(img_result.split(',')[0])
    class1_number = int(img_result.split(',')[1])
    class2_number = int(img_result.split(',')[2])
    class3_number = int(img_result.split(',')[3])
    class4_number = int(img_result.split(',')[4])
    class5_number = int(img_result.split(',')[5])
    class6_number = int(img_result.split(',')[6])

    img_pixel = [class0_number,class1_number,class2_number,class3_number,class4_number,class5_number,class6_number]

    return img_pixel

def folder_img_statistics(folder_path):
    folder_result = [0]*7
    file_list = os.listdir(folder_path)
    
    for index in range(len(file_list)):
        if file_list[index].split('.')[1] == 'txt':
            img_result = img_statistics(os.path.join(folder_path,file_list[index]))
            for k in range(7):
                folder_result[k] = folder_result[k] + img_result[k]
        
    return folder_result # type(folder_result)==list


if __name__ == '__main__':
    img_path = './30.jpg'
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        palette = cfg['network']['palette']
    # img_result = img_statistics(img_path,palette)
    folder_result = folder_img_statistics('./plant_imgs_seg/-366582')
    print(folder_result)