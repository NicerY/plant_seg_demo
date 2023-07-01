from map.map_get import map_get
import cv2
import numpy as np
import yaml

yaml_path = './config.yaml'
current_map_path = './original_map/current_map.png'

def count_pixels(pixel_color):
    num = 0
    img = cv2.imread(current_map_path)
    height,width = img.shape[0],img.shape[1]
    # print(height,width)
    for i in range(height):
        for j in range(width):
            if np.array_equal(img[i,j,:],pixel_color):
                num = num + 1
    return num

def get_icon_height(pixel_color):
    icon_height = 0
    img = cv2.imread(current_map_path)
    height,width = img.shape[0],img.shape[1]
    for i in range(height):
        for j in range(width):
            if np.array_equal(img[i,j,:],pixel_color):
                icon_height = icon_height + 1
                break
    return icon_height

def get_icon_width(pixel_color):
    icon_width = 0
    img = cv2.imread(current_map_path)
    height,width = img.shape[0],img.shape[1]
    for j in range(width):
        for i in range(height):
            if np.array_equal(img[i,j,:],pixel_color):
                icon_width = icon_width + 1
                break
    return icon_width

def get_delta(int_bit, index):
    if index<int_bit:
        power_str = '+' + str(int_bit-index-1)
    else:
        power_str = '-' + str(index-int_bit)

    delta_str = '1' + 'e' + power_str
    delta = float(delta_str)
    return delta

# def get_latitude_gap(icon_height, gap_height, pixel_color):
    # latitude_gap = 0
    # img = cv2.imread(current_map_path)
    # height,width = img.shape[0],img.shape[1]
    # i_num = 0
    # i_index = 0
    # flag = True
    # for i in range(height):
    #     if not flag:
    #         break
    #     for j in range(width):
    #         if np.array_equal(img[i,j,:],pixel_color):
    #             i_num = i_num + 1
    #             if (icon_height-i_num)==gap_height:
    #                 i_index = i
    #                 flag = False
    #                 break
    #             break
    # for i in range(i_index+1,i_index+1+gap_height):
    #     for j in range(width):
    #         if np.array_equal(img[i,j,:],pixel_color):
    #             latitude_gap = latitude_gap + 1

    # return latitude_gap

def get_latitude_gap(pixel_color):
    latitude_gap = 0
    img = cv2.imread(current_map_path)
    height,width = img.shape[0],img.shape[1]
    for i in range(int(height/2),height):
        for j in range(width):
            if np.array_equal(img[i,j,:],pixel_color):
                latitude_gap = latitude_gap + 1
    return latitude_gap



def map_adjustment(center_gps):
    # map_get(center_gps)

    icon_pixel_number = 0

    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        color = cfg['API']['color'][::-1] #RGB to BGR
        # print(color)
    
    icon_pixel_number = count_pixels(np.array(color))
    print('icon_pixel_number',icon_pixel_number)

    # 用类似二分法计算gps经度范围,297/2范围变成(135,148)
    icon_height = get_icon_height(np.array(color))
    print('icon_height',icon_height)
    icon_width = get_icon_width(np.array(color))
    print('icon_width',icon_width)
    longitude_icon_pixel_number_left = int((icon_pixel_number-icon_height)/2)
    longitude_icon_pixel_number_right = longitude_icon_pixel_number_left+icon_height
    print('longitude_icon_pixel_range',longitude_icon_pixel_number_left,longitude_icon_pixel_number_right)


    # center右侧
    longitude,latitude = center_gps.split(',')[0],center_gps.split(',')[1]
    # print(longitude,latitude)
    longitude_char_len = len(longitude)
    longitude_int_bit = len(longitude.split('.')[0])
    # print('longitude_int_bit',longitude_int_bit)
    test_gps = center_gps
    flag = True
    print('开始校准地图右侧经度！')
    for index in range(longitude_char_len):
        if longitude[index] == '.':
            continue
        if not flag:
            break
        delta = get_delta(longitude_int_bit, index)
        
        while True:
            # print(longitude+latitude)
            map_get(center_gps, test_gps)
            # break
            if count_pixels(np.array(color))>(longitude_icon_pixel_number_right):
                longitude = float(longitude)
                longitude = longitude + delta
                longitude = str(longitude)
                test_gps = longitude+','+latitude
                print('test_gps',test_gps)
                continue

            if count_pixels(np.array(color))<(longitude_icon_pixel_number_left):
                longitude = float(longitude)
                longitude = longitude - delta
                longitude = str(longitude)
                test_gps = longitude+','+latitude
                print('test_gps',test_gps)
                break
            
            if count_pixels(np.array(color))>=(longitude_icon_pixel_number_left) and count_pixels(np.array(color))<=(longitude_icon_pixel_number_right):
                flag = False
                print('test_gps',test_gps)
                break
    right_longitude = test_gps.split(',')[0]

    # center左侧
    longitude,latitude = center_gps.split(',')[0],center_gps.split(',')[1]
    # print(longitude,latitude)
    longitude_char_len = len(longitude)
    longitude_int_bit = len(longitude.split('.')[0])
    # print('longitude_int_bit',longitude_int_bit)
    test_gps = center_gps
    flag = True
    print('开始校准地图左侧经度！')
    for index in range(longitude_char_len):
        if longitude[index] == '.':
            continue
        if not flag:
            break
        delta = get_delta(longitude_int_bit, index)
        
        while True:
            # print(longitude+latitude)
            map_get(center_gps, test_gps)
            # break
            if count_pixels(np.array(color))>(longitude_icon_pixel_number_right):
                longitude = float(longitude)
                longitude = longitude - delta
                longitude = str(longitude)
                test_gps = longitude+','+latitude
                print('test_gps',test_gps)
                continue

            if count_pixels(np.array(color))<(longitude_icon_pixel_number_left):
                longitude = float(longitude)
                longitude = longitude + delta
                longitude = str(longitude)
                test_gps = longitude+','+latitude
                print('test_gps',test_gps)
                break
            
            if count_pixels(np.array(color))>=(longitude_icon_pixel_number_left) and count_pixels(np.array(color))<=(longitude_icon_pixel_number_right):
                flag = False
                print('test_gps',test_gps)
                break
    left_longitude = test_gps.split(',')[0]




    # 用类似二分法计算gps纬度范围,取下半张地图中icon的像素数量作为gap
    latitude_gap = get_latitude_gap(np.array(color))
    # center下侧
    latitude_icon_pixel_number_down_left = icon_pixel_number-latitude_gap
    latitude_icon_pixel_number_down_right = icon_pixel_number
    print('latitude_icon_pixel_range_down',latitude_icon_pixel_number_down_left,latitude_icon_pixel_number_down_right)
    longitude,latitude = center_gps.split(',')[0],center_gps.split(',')[1]
    # print(longitude,latitude)
    latitude_str_len = len(latitude)
    latitude_int_bit = len(latitude.split('.')[0])
    # print('latitude_int_bit',latitude_int_bit)
    test_gps = center_gps
    flag = True
    print('开始校准地图下侧纬度！')
    for index in range(latitude_str_len):
        if latitude[index] == '.':
            continue
        if not flag:
            break
        delta = get_delta(latitude_int_bit, index)
        
        while True:
            # print(longitude+latitude)
            map_get(center_gps, test_gps)
            # break
            if count_pixels(np.array(color))>=(latitude_icon_pixel_number_down_right):
                latitude = float(latitude)
                latitude = latitude - delta
                latitude = str(latitude)
                test_gps = longitude+','+latitude
                print('test_gps',test_gps)
                continue

            if count_pixels(np.array(color))<(latitude_icon_pixel_number_down_left):
                latitude = float(latitude)
                latitude = latitude + delta
                latitude = str(latitude)
                test_gps = longitude+','+latitude
                print('test_gps',test_gps)
                break
            
            if count_pixels(np.array(color))>=(latitude_icon_pixel_number_down_left) and count_pixels(np.array(color))<(latitude_icon_pixel_number_down_right):
                flag = False
                print('test_gps',test_gps)
                break
    down_latitude = test_gps.split(',')[1]
    # print(down_latitude)

    # center上侧的纬度范围由于API的原因无法准确测量，且会耗时特别长，因此用下侧的纬度变化范围来近似
    print('开始近似地图上侧纬度！')
    up_latitude = str(float(center_gps.split(',')[1])+float(center_gps.split(',')[1])-float(down_latitude))
    
    print('center longitude:',center_gps.split(',')[0])
    print('longitude range:',left_longitude,right_longitude)
    print('center latitude:',center_gps.split(',')[1])
    print('latitude range:',down_latitude,up_latitude)

    # 读取YAML文件
    with open(yaml_path, "r") as f:
        cfg = yaml.safe_load(f)
    # 修改键值
    cfg['map']['center_lon'] = center_gps.split(',')[0]
    cfg['map']['center_lat'] = center_gps.split(',')[1]
    cfg['map']['longitude_left'] = left_longitude
    cfg['map']['longitude_right'] = right_longitude
    cfg['map']['latitude_up'] = up_latitude
    cfg['map']['latitude_down'] = down_latitude
    # 将修改后的数据写入YAML文件
    with open(yaml_path, "w") as f:
        yaml.safe_dump(cfg, f)

    map_get(center_gps)


if __name__ == "__main__":
    map_get('118.80019307726839,32.074971594853006')
    map_adjustment('118.80019307726839,32.074971594853006')

# center longitude: 118.80019307726839
# longitude range: 118.79616307726836 118.8042130772684
# center latitude: 32.074971594853006
# latitude range: 32.071561594852994 32.07838159485301

