import json
import requests
# 通过地点名称获取某一地点的gps

ak = 'yCgQn0QMo3fZMRAPUak2D2y1bDk8kpqz'
address = '南京玄武湖菱洲乐园'

url = f'http://api.map.baidu.com/geocoding/v3/?address={address}&output=json&ak={ak}'
response = requests.get(url)
result = json.loads(response.text)

if result['status'] == 0:
    location = result['result']['location']
    print(location)
else:
    print('查询失败')