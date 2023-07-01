# plant_seg_demo

1.根据requirement.txt配置环境，注意modbus协议版本，注意mmsegmentation版本和安装位置，mmsegmentation安装需要cpp编译。


2.启动rtsp，modbus，tcp/ip三个协议分别接收视频，透明度，gps数据。


3.启动ui.py，先获得地图，之后校准地图。


4.开始或结束接收数据，实时分割。


5.统计植物分布。


6.接收数据的同时可以实时查看当前位置植物及其分割图。


