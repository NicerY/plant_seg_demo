import cv2 
import yaml

yaml_path = './config.yaml'

def rtsp_client_init():
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        rtsp_IP = cfg['video']['IP']
        rtsp_port = cfg['video']['port']
        rtsp_stream_name = cfg['video']['stream_name']

    rtsp_client = cv2.VideoCapture(f"rtsp://admin:123456@192.168.1.109:554/streaml")

    return rtsp_client

def get_plant_imgs(client,num):
    
    ret,frame = client.read()
    # frame = cv2.resize(frame,(1000,750))
    # cv2.imshow("frame",frame)
    # if (num)%30==0: # 如果是30帧的视频
    #     cv2.imwrite(f"./test0629/imgs/{num}.jpg",frame)
    cv2.imwrite(f"./test0629/imgs/{num}.jpg",frame)
    if cv2.waitKey(1) & 0xFF == ord('z'):
        print('get_plant_imgs ERROR!')
        cv2.destroyAllWindows()
        client.release()

    # return f"./plant_imgs/{num+1}.jpg"

if __name__ == '__main__':
    client = rtsp_client_init()
    num = 0
    while True:
        num = num + 1
        get_plant_imgs(client,num)