import sys, os
from socket import *
import threading
import time
import uuid
host  = 'qinbatista.com' # 这是客户端的电脑的ip
serial_number = "us"
port = 12345 #接口选择大于10000的，避免冲突
bufsize = 1024  #定义缓冲大小


def main():
	global host
	while host=="":
		host = input('Input your ddns server domain name or IP adrress:')
	thread1 = threading.Thread(target=run,name="线程1",args=("123","123"))
	thread1.start()
def get_mac_address(): 
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
def get_host_ip():
    try:
        s = socket(AF_INET,SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
def run(param1,param2):
	global serial_number,host
	addr = (host,port) # 元祖形式
	while True:
		try:
			udpClient = socket(AF_INET,SOCK_DGRAM) #创建客户端
			data = get_mac_address()
			while serial_number=="":
				print("input your serial number:")
				serial_number = input()
			data =data+"|"+serial_number
			# print("mac:"+data+" host:"+host)
			data = data.encode(encoding="utf-8") 
			udpClient.sendto(data,addr) # 发送数据
			time.sleep(10)
		except Exception as e:
			print("e="+str(e))
	udpClient.close()

if __name__ == '__main__':
    main()