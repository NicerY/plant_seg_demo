from pymodbus.client.sync import ModbusTcpClient
# 注意pymodbus版本必须为2.5.3
import yaml

yaml_path = './config.yaml'

def transparency_client_init():
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        transparency_IP = cfg['transparency']['IP']
        transparency_port = cfg['transparency']['port']
        
    # 创建一个Modbus TCP客户端
    client = ModbusTcpClient(transparency_IP, port=transparency_port)

    return client,cfg

def transparency_receive(client, cfg):
    transparency_unit = cfg['transparency']['unit']
    transparency_address = cfg['transparency']['address']
    transparency_count = cfg['transparency']['count']

    # 从从站地址为11的设备读取寄存器值
    # 寄存器起始地址是35，寄存器数量是1
    result = client.read_holding_registers(address=transparency_address, count=transparency_count, unit=transparency_unit)
    if not result.isError():
        # with open('./transparency/transparency_data.txt', 'a') as f:
        #     # 获取当前时间的时间戳
        #     timestamp = time.time()

        #     # 将时间戳转换为本地时间
        #     local_time = time.localtime(timestamp)

        #     # 输出当前时间
        #     t = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        #     f.write(str(result.registers[0])+','+str(t))
        #     f.write('\n')
        return result.registers[0]

    else:
        print("读取寄存器失败")