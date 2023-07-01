import cv2 
cap = cv2.VideoCapture("rtsp://172.28.191.47:554/test")
ret,frame = cap.read()
num = 0
while ret:
    num += 1
    print(num)
    ret,frame = cap.read()
    cv2.imshow("frame",frame)
    cv2.imwrite(f"./plant_imgs/{num}.jpg",frame)
    if cv2.waitKey(1) & 0xFF == ord('z'):
        break
cv2.destroyAllWindows()
cap.release()

# ffmpeg -re -stream_loop -1 -i ./oceans.mp4 -vcodec copy -acodec copy -f rtsp rtsp://172.28.191.47:8554/test
# -re 以本地帧频读数据，主要用于模拟捕获设备
# -stream_loop 按照设定的次数推流，需要循环多少次则填多少次即可。若需要无限循环使用-1
# -i 表示输入视频文件，后跟视频文件路径/URL
# -vcodec 指定视频解码器，v是视频video，codec就是解码器，后跟解码器名称，copy表示不作解码
# -acodec 指定音频解码器，同理，a是audio，后跟解码器名称。-an代表acodec none就是去掉音频的意思
# -f 强制ffmpeg采用某种格式，后跟对应的格式
# rtsp://(本机IP):(开放的端口)/(视频流名字)
# 先打开EasyDarwin，再使用这条命令
# 如果8554端口无法正常推流可能是这个端口已经被占用了，使用554端口
# 不支持MOV格式的文件
# 1000分辨率正常，3840只能达到700/1700
# 后台监测 http://localhost:10008/