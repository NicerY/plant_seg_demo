import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap
import threading
import time
from transparency.transparency_receive import transparency_client_init, transparency_receive
from gps.gps_receive import gps_client_init, gps_receive
from map.map_get import map_get
from map.map_adjustment import map_adjustment
from video.video_get import rtsp_client_init,get_plant_imgs
from PIL import Image
import numpy as np
import yaml
from mmsegmentation.demo.seg_plant_img import network_init,plant_img_seg
from plant_statistics.plant_statistics import folder_img_statistics
import os
import shutil
import cv2
from map.map_patch_index_get import get_map_patch_index


yaml_path = './config.yaml'

class imageview_label(QLabel):
    def __init__(self):
        super(imageview_label, self).__init__()
        # 设置QLabel控件的位置和大小
        self.image_width = 896
        self.image_height = 896
        self.setGeometry(20, 20, self.image_width, self.image_height)

        self.current_map_path = './original_map/current_map.png'
        self.current_map_gridlines_path = './original_map/current_map_gridlines.png'

        # lon = 118.80019307726839
        # lat = 32.074971594853006
        # location = '118.80019307726839,32.074971594853006'
        # self.get_image(location)
        # 113.93087504466666,22.563382710833334


    def get_image(self, center, markers=None):
        map_get(center, markers)
        self.process_image()
        self.show_image()

    def process_image(self):
        with open(yaml_path, 'r') as f:
            cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
            self.gridline_number = cfg['gridline']['number']
            
        # 增加网格
        self.current_map = Image.open(self.current_map_path).convert('RGBA') # 写成RGB而不是RGBA会有warning
        self.current_map = np.array(self.current_map)
        self.patch_size = self.image_width/self.gridline_number
        x, y = 0, 0
        while x<self.gridline_number: # HW(RGBA)
            self.current_map[:,int(x*self.patch_size),0] = 255
            self.current_map[:,int(x*self.patch_size),1:3] = 0
            self.current_map[:,int(x*self.patch_size),3] = 255
            self.current_map[:,int((x+1)*self.patch_size-1),0] = 255
            self.current_map[:,int((x+1)*self.patch_size-1),1:3] = 0
            self.current_map[:,int((x+1)*self.patch_size-1),3] = 255
            x = x + 1
        while y<self.gridline_number:
            self.current_map[int(y*self.patch_size),:,0] = 255
            self.current_map[int(y*self.patch_size),:,1:3] = 0
            self.current_map[int(y*self.patch_size),:,3] = 255
            self.current_map[int((y+1)*self.patch_size-1),:,0] = 255
            self.current_map[int((y+1)*self.patch_size-1),:,1:3] = 0
            self.current_map[int((y+1)*self.patch_size-1),:,3] = 255
            y = y + 1
        
        self.current_map = Image.fromarray(self.current_map, mode='RGBA') 
        self.current_map.save(self.current_map_gridlines_path)
        


    def show_image(self):
        self.pixmap = QPixmap(self.current_map_gridlines_path)  # 加载图像文件
        self.setPixmap(self.pixmap)  # 将缩放后的图像设置为 QLabel 的背景图像



class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        with open(yaml_path, 'r') as f:
            cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
            self.gridline_num = cfg['gridline']['number']

        # shutil.rmtree('./plant_imgs_seg')
        if not os.path.exists('./plant_imgs_seg'):
            os.mkdir('./plant_imgs_seg')
        for n in range(self.gridline_num*self.gridline_num):
            if not os.path.exists(f'./plant_imgs_seg/{n+1}'):
                os.mkdir(f'./plant_imgs_seg/{n+1}')
            # if not os.path.exists(f'./plant_imgs/{n+1}'):
            #     os.mkdir(f'./plant_imgs/{n+1}')
        self.height = 950
        self.width =  1600
        self.setGeometry(120, 70, self.width, self.height) # x,y,w,h
        self.setFixedSize(self.width, self.height) # 禁止拉伸窗口大小  
        self.setWindowTitle('地图显示')
        self.flag = False
        self.transparency_client_init_flag = False
        self.gps_client_init_flag = False
        self.video_client_init_flag = False
        self.seg_flag = False
        self.loop_thread1 = threading.Thread(target=self.loop1, daemon=True)
        self.loop_thread2 = threading.Thread(target=self.loop2, daemon=True)
        self.model, self.palette = network_init()
        self.initUI()

    def initUI(self):
        # 图像显示控件
        self.imageview = imageview_label()
        self.imageview.setParent(self) # 将其添加到QWidget窗口中

        # '输入水域中心点GPS'文本框
        self.input_center_gps = QLineEdit('请输入水域中心点GPS', self)
        self.input_center_gps.setGeometry(955, 60, 605, 55) # xywh
        self.input_center_gps.setFont(QtGui.QFont("Timers", 14)) 
        self.input_center_gps.selectAll()
        self.input_center_gps.setFocus()

        # '开始'按钮
        self.button_begin = QPushButton('开始', self)
        self.button_begin.setGeometry(955, 260, 280, 55)
        self.button_begin.setFont(QtGui.QFont("Timers", 14)) 
        self.button_begin.clicked.connect(self.begin)

        # '当前位置GPS'文本框
        self.current_gps = QLineEdit(self)
        self.current_gps.setGeometry(955, 360, 605, 55)
        self.current_gps.setFont(QtGui.QFont("Timers", 14)) 
        self.current_gps.setText('当前位置GPS:')
        self.current_gps.setReadOnly(1)   #设为只读

        # '当前位置透明度'文本框
        self.current_transparency = QLineEdit(self)
        self.current_transparency.setGeometry(955, 460, 605, 55)
        self.current_transparency.setFont(QtGui.QFont("Timers", 14)) 
        self.current_transparency.setText('当前位置透明度:')
        self.current_transparency.setReadOnly(1)   #设为只读

        # '计算植物分布图'按钮
        self.compute_plant_distribution = QPushButton('计算植物分布图', self)
        self.compute_plant_distribution.setGeometry(955, 560, 605, 55)
        self.compute_plant_distribution.setFont(QtGui.QFont("Timers", 14))
        self.compute_plant_distribution.clicked.connect(self.compute_distribution)


        # '查看植物分布图'按钮
        self.button_view_plant_map = QPushButton('查看植物分布图', self)
        self.button_view_plant_map.setGeometry(955, 660, 280, 55)
        self.button_view_plant_map.setFont(QtGui.QFont("Timers", 14)) 

        # '查看当前位置植物分割图'按钮
        self.button_view_current_seg_map = QPushButton('查看当前位置植物分割图', self)
        self.button_view_current_seg_map.setGeometry(955, 760, 605, 55)
        self.button_view_current_seg_map.setFont(QtGui.QFont("Timers", 14)) 
        self.button_view_current_seg_map.clicked.connect(self.get_current_seg_map)

        # '保存当前水域地图'按钮
        # self.button_save_current_map = QPushButton('保存当前水域地图', self)
        # self.button_save_current_map.setGeometry(955, 860, 280, 55)
        # self.button_save_current_map.setFont(QtGui.QFont("Timers", 14)) 

        # '获得水域地图'按钮
        self.button_get_map = QPushButton('获得水域地图', self)
        self.button_get_map.setGeometry(955, 160, 280, 55)
        self.button_get_map.setFont(QtGui.QFont("Timers", 14)) 
        self.button_get_map.clicked.connect(self.get_current_map)

        # '校准地图'按钮
        self.button_adj_map = QPushButton('校准地图', self)
        self.button_adj_map.setGeometry(1280, 160, 280, 55)
        self.button_adj_map.setFont(QtGui.QFont("Timers", 14)) 
        self.button_adj_map.clicked.connect(self.adjustment_map)

        # '停止'按钮
        self.button_finish = QPushButton('停止', self)
        self.button_finish.setGeometry(1280, 260, 280, 55)
        self.button_finish.setFont(QtGui.QFont("Timers", 14))
        self.button_finish.clicked.connect(self.finish)

        # '查看原地图'按钮
        self.button_finish = QPushButton('查看原地图', self)
        self.button_finish.setGeometry(1280, 660, 280, 55)
        self.button_finish.setFont(QtGui.QFont("Timers", 14))

        # '查看已探测区域'按钮
        # self.button_finish = QPushButton('查看已探测区域', self)
        # self.button_finish.setGeometry(1280, 860, 280, 55)
        # self.button_finish.setFont(QtGui.QFont("Timers", 14))

        # 防止loop线程开始太早，主线程变量未全部初始化
        self.loop_thread1.start()
        self.loop_thread2.start()


    def begin(self):
        self.flag = True
        # print(self.flag)

    def finish(self):
        self.flag = False
        # print(self.flag)
    
    def get_current_map(self):
        with open(yaml_path, 'r') as f:
            cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
            if cfg['map']['center_lon'] != '0':
                self.map_center_gps = cfg['map']['center_lon']+','+cfg['map']['center_lat']
            else:
                self.map_center_gps = str(self.input_center_gps.text())
        
        # print(self.map_center_gps)
        self.imageview.get_image(self.map_center_gps)

    def adjustment_map(self):
        map_adjustment(self.map_center_gps)

    def compute_distribution(self):
        self.plant_imgs_seg_path = './plant_imgs_seg'
        if os.path.exists(self.plant_imgs_seg_path+'/seg_result.txt'):
            os.remove(self.plant_imgs_seg_path+'/seg_result.txt')

        print('开始计算!')
        for n in range(self.gridline_num*self.gridline_num):
            result = folder_img_statistics(self.plant_imgs_seg_path+f'/{n+1}')
            with open(self.plant_imgs_seg_path+'/seg_result.txt','a') as f:
                f.write(str(n+1)+','+str(result))
                f.write('\n')
        print('计算完成！')

    def get_current_seg_map(self):
        self.view_image_num = self.seg_number
        self.view_map_patch_index = self.seg_index
        plant_img = cv2.imread(f"./plant_imgs/{self.view_map_patch_index}/{self.view_image_num}.jpg")
        plant_img = cv2.resize(plant_img,[800,600])
        plant_seg_img = cv2.imread(f"./plant_imgs_seg/{self.view_map_patch_index}/{self.view_image_num}.jpg")
        plant_seg_img = cv2.resize(plant_seg_img,[800,600])
        concat_img = cv2.hconcat([plant_img,plant_seg_img])

        cv2.imshow('current seg map',concat_img)


    def loop1(self):
        num = 0
        while True:
            if self.flag:
                # 如果可以的话尽量把三个客户端的初始化也放到MainWindow初始化那里，不然每次循环都要进行三次判断！！！！！
                if not self.transparency_client_init_flag:
                    # 初始化透明度数据接收客户端
                    self.transparency_client, self.transparency_cfg = transparency_client_init()
                    self.transparency_client_init_flag = True

                if not self.gps_client_init_flag:
                    # 初始化GPS数据接收客户端
                    self.gps_client = gps_client_init()
                    self.gps_client_init_flag = True

                if not self.video_client_init_flag:
                    # 初始化视频接收客户端
                    self.video_client = rtsp_client_init()
                    self.video_client_init_flag = True

                self.current_frame = get_plant_imgs(self.video_client)
                num = num + 1

                # if num%30 != 0: # frame读取速度远快于透明度和gps，而且有很多frame冗余，所以每一秒只把所有数据接收一次，视频应该是30fps
                #     continue
                
                if self.seg_flag == True:
                    continue
                else:
                    self.plant_img_for_seg = self.current_frame
                    self.num = num
                    self.seg_flag = True
                    self.transparency_flag = True
                    self.gps_flag = True

                # 共享内存

                # print("Receiving data...")
            else:
                if self.transparency_client_init_flag:
                    # 透明度数据接收客户端
                    self.transparency_client.close()
                    self.transparency_cfg = None
                    self.transparency_client_init_flag = False

                # 自己测试时候这三行要注释掉，实地接收时候要看服务器端是不是一直在等待连接
                # if self.gps_client_init_flag:
                #     self.gps_client.close()
                #     self.gps_client_init_flag = False

                if self.video_client_init_flag:
                    # 视频接收客户端
                    self.video_client.release()
                    self.video_client_init_flag = False

                self.current_transparency.setText('当前位置透明度: ')
                self.current_gps.setText('当前位置GPS: ')
                # print("Not receiving data...")
                
            time.sleep(0.01)
    
    def loop2(self):
        while True:
            if self.seg_flag == False:
                continue
            else:
                self.transparency = transparency_receive(self.transparency_client, self.transparency_cfg)
                
                self.gps = gps_receive(self.gps_client)
                
                # 先更新地图再更新gps和透明度，不然看起来会有点卡顿
                # 而且似乎这样弄不会再出现QLineEdit显示字有重叠或者不显示的情况
                self.imageview.get_image(self.map_center_gps, self.gps) 
                self.current_gps.setText('当前位置GPS: '+str(self.gps))
                # self.current_gps.setText(str(self.gps))
                self.current_transparency.setText('当前位置透明度: '+ str(self.transparency))
                # self.current_transparency.setText(str(self.transparency))

                self.patch_index = get_map_patch_index(self.gps)
                self.plant_img_path_for_seg = f"./plant_imgs/{self.patch_index}/{self.num}.jpg"
                cv2.imwrite(self.plant_img_path_for_seg,self.plant_img_for_seg)
                plant_img_seg(self.model,self.plant_img_path_for_seg,self.num,self.palette,self.patch_index)
                self.seg_number = self.num
                self.seg_index = self.patch_index # 这两个参数为了传递给显示当前位置植物分割图，要完成分割并且保存下来才能显示
                self.seg_flag = False

            time.sleep(0.0001)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # 显示窗口
    sys.exit(app.exec_())