from map.map_get import map_get
import cv2
import numpy as np

# center_lon = '118.80019307726839'
# center_lat = '32.074971594853006'
# longitude_left = '118.79616307726836'
# longitude_right = '118.8042130772684'
# latitude_up = '32.071561594852994'
# latitude_down = '32.07838159485301'

# import yaml
# # 读取YAML文件
# with open("./config.yaml", "r") as f:
#     cfg = yaml.safe_load(f)

# print(cfg['map']['center_lon']+','+cfg['map']['center_lat'])
# print(type(cfg['map']['center_lon']))
# # 修改键值
# cfg['map']['center_lon'] = center_lon
# cfg['map']['center_lat'] = center_lat
# cfg['map']['longitude_left'] = longitude_left
# cfg['map']['longitude_right'] = longitude_right
# cfg['map']['latitude_up'] = latitude_up
# cfg['map']['latitude_down'] = latitude_down

# map_get(center_lon+','+center_lat)

# # 将修改后的数据写入YAML文件
# with open("./config.yaml", "w") as f:
#     yaml.safe_dump(cfg, f)

# from mmsegmentation.demo.seg_plant_img import network_init,plant_img_seg

# img = './plant_imgs/29.jpg'
# model = network_init()
# plant_img_seg(model,img,29)

from video.video_get import rtsp_client_init,get_plant_imgs
import time

# video_client = rtsp_client_init()
# num = 0
# while True:
#     num = num+1
#     current_plant_img_path = get_plant_imgs(video_client,num)
#     time.sleep(0.01)

# print(32.07838159485301-32.071561594852994)
a = np.load(f'./plant_imgs_seg/256/30.npy')
count = np.count_nonzero(a == 4)
print(sum([4397445, 1678431, 1941893, 0, 902376, 829855, 0])/13)