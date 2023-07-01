import socket
import time

def gps_send_test(SERVER_ADDRESS,SERVER_PORT,msg):

    # 创建一个TCP套接字，并绑定到服务器地址和端口号
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_ADDRESS, SERVER_PORT))

    # 开始监听客户端连接请求
    sock.listen(1)

    tt = 0

    while True:
        # 等待客户端连接请求
        print('waiting for a connection')
        connection, client_address = sock.accept()

        try:
            print('connection from', client_address)

            while True:
                # 发送响应数据给客户端
                tt = tt + 1 # 下面四行仅测试用
                v = str(tt%3)
                message = msg[:6]+str(v)+msg[7:]
                connection.sendall(message.encode())
                time.sleep(1)

        finally:
            # 关闭连接
            connection.close()

def gps_send(SERVER_ADDRESS,SERVER_PORT,msg):
    # 创建一个TCP套接字，并绑定到服务器地址和端口号
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_ADDRESS, SERVER_PORT))

    # 开始监听客户端连接请求
    sock.listen(1)

    while True:
        # 等待客户端连接请求
        print('waiting for a connection')
        connection, client_address = sock.accept()

        try:
            print('connection from', client_address)

            while True:
                # 发送响应数据给客户端
                connection.sendall(msg.encode())
                time.sleep(1)
        finally:
            # 关闭连接
            connection.close()


if __name__ == '__main__':
    # 服务器地址和端口号
    SERVER_ADDRESS = '172.28.191.47'
    SERVER_PORT = 8001

    # gps_send_test(SERVER_ADDRESS,SERVER_PORT,'118.80019307726839,32.074971594853006')
    gps_send(SERVER_ADDRESS,SERVER_PORT,"$GPGGA,035636.00,2233.80296265,N,11355.85250268,E,1,24,0.8,70.7596,M,-3.7580,M,,*48")