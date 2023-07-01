import requests
import yaml

yaml_path = './config.yaml'

def map_get(center, markers=None):
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        ak = cfg['API']['ak']
        map_get_url = cfg['API']['map_get_url']
        zoom = cfg['API']['zoom']
        width = cfg['API']['width']
        height = cfg['API']['height']
        markerStyles = cfg['API']['markerStyles']
        scale = cfg['API']['scale']
 
    params = { # 参考文档：https://lbsyun.baidu.com/index.php?title=static
        'ak': ak,
        'center': center,
        'zoom': zoom,
        'width': width,
        'height': height,
        'markerStyles': markerStyles,
        'scale': scale,
    }

    params['markers'] = markers if markers else center # 显示中心点位置或者船的位置
    # print(params)

    response = requests.get(map_get_url, params=params)
    # with open('D:/project/original_map/map.html', 'wb') as f:
    #     f.write(response.content)
    with open('./original_map/current_map.png', 'wb') as f:
        f.write(response.content)