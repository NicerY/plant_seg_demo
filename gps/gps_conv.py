import requests

# 坐标系变换，将其他坐标系变成百度自己的坐标系

ak = 'yCgQn0QMo3fZMRAPUak2D2y1bDk8kpqz'
url = 'http://api.map.baidu.com/geoconv/v1/'

lon = 118.83038471414375
lat = 32.078667187994
params = {
    'coords': f'{lon},{lat}',
    'from': 1,  # WGS84坐标系
    'to': 5,  # 百度坐标系
    'ak': ak,
}

response = requests.get(url, params=params)
result = response.json()
if result.get('status') == 0:
    lon = result['result'][0]['x']
    lat = result['result'][0]['y']

location = str(lon) + ',' + str(lat)
print(location)