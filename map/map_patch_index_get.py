import yaml

yaml_path = './config.yaml'


def get_map_patch_index(gps):
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        number = float(cfg['gridline']['number'])
        longitude_left = float(cfg['map']['longitude_left'])
        longitude_right = float(cfg['map']['longitude_right'])
        latitude_up = float(cfg['map']['latitude_up'])
        latitude_down = float(cfg['map']['latitude_down'])
    
    longitude = float(gps.split(',')[0])
    latitude = float(gps.split(',')[1])

    longitude_delta = (longitude_right-longitude_left)/number
    latitude_delta = (latitude_down-latitude_up)/number

    j = ((longitude - longitude_left)//longitude_delta)+1
    i = ((latitude - latitude_up)//latitude_delta)

    return int(i*number+j)