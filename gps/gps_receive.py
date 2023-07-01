import socket
import pynmea2
import yaml
import re
import os

# 接收gps数据

yaml_path = './config.yaml'

def gps_client_init():
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        gps_IP = cfg['GPS']['IP']
        gps_port = cfg['GPS']['port']

    # 创建一个TCP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接到服务器
    sock.connect((gps_IP, gps_port))

    return sock

def gps_receive(sock):
    gps_data = sock.recv(1024)
    gps_data = gps_data.decode()
    message = ''

    # 只接收第一个gps信号
    for i in range(len(gps_data)):
        if gps_data[i]=='$' and i!=0:
            break
        message = message + gps_data[i]

    # # 打开文件，准备写入GPS数据
    # with open('./gps/gps_data.txt', 'a') as f:
    #     f.write(message)
    #     f.write('\n')

    # 解析GPS数据
    message = pynmea2.parse(message)

    # 提取位置、海拔高度和时间等信息
    # if isinstance(message, pynmea2.GGA):
    #     print("Latitude:", msg.latitude)
    #     print("Longitude:", msg.longitude)
    #     print("Altitude:", msg.altitude)
    #     print("Time:", msg.timestamp)

    return str(message.longitude)+','+str(message.latitude)

# def gps_receive(sock):
#     gps_data = sock.recv(1024)
#     gps_data = gps_data.decode()
#     message = ''

#     message = gps_data[:37] # 仅测试用

#     # 打开文件，准备写入GPS数据
#     with open('./gps/gps_data.txt', 'a') as f:
#         f.write(message)
#         f.write('\n')
    
#     return message # 仅测试用
