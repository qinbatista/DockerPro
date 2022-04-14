import sys, os
import os.path
import socket
import threading
from socket import *
from time import ctime
import time
class DDNSServer:
	def __init__(self,port=12345,domain_name=''):
		self.addr = ('',port)
		self.udpServer = socket(AF_INET,SOCK_DGRAM)
		self.udpServer.bind(self.addr) #开始监听
		self.dnsmasq_conf=[]
		self.ip_list = []
		self.mac_list = []
		self.client_require_domain_name = []
		self.domain_name = domain_name
		self.seconds = 10
	def deploy_ddns_server(self):
		os.system("apt-get -y install dnsmasq")
		with open('./dnsmasq.conf','r',encoding="utf8") as file:
			all_the_text = file.readlines()
			for i in all_the_text:
				if(i.find('listen-address=')!=-1):self.dnsmasq_conf.append("listen-address="+self.get_host_ip()+",127.0.0.1"+"\n")
				else:self.dnsmasq_conf.append(i)
		with open('./dnsmasq.conf','w',encoding="utf8") as file:
			file.writelines(self.dnsmasq_conf)
		os.system(f"echo 'conf-dir=/etc/dnsmasq.d/,*.conf' >> /etc/dnsmasq.conf")
		os.system(f'echo "user=root" >> /etc/dnsmasq.conf')
		os.system("cp "+"./dnsmasq.conf /etc/dnsmasq.conf")
		os.system("cp "+"./MyDNSHost /etc/hosts")
	def get_host_ip(self):
		try:
			s = socket(AF_INET, SOCK_DGRAM)
			s.connect(('8.8.8.8', 80))
			ip = s.getsockname()[0]
		finally:
			s.close()
		print("this machine's ip:"+ip)
		return ip
	def sync_ddns_host_config(self):
		while True:
			print('sync_ddns_host_config')
			HostContext=[]
			for index,ip in enumerate(self.ip_list):
				HostContext.append(ip+" "+str(self.client_require_domain_name[index])+"."+self.domain_name+"\n")
			with open("./MyDNSHost",'w',encoding="utf8") as file:
				file.writelines(HostContext)
			os.system("cp "+"./MyDNSHost /etc/hosts")
			os.system("/etc/init.d/dnsmasq restart")
			time.sleep(10)
	def start_sync_ddns_config_thread(self):
		print('Next refresh:'+str(self.seconds)+'s')
		thread1 = threading.Thread(target=self.sync_ddns_host_config)
		thread1.start()
	def recive_udp_message(self,name,args):
		while True:
			data,addr = self.udpServer.recvfrom(1024)
			ReciveIP, _ = addr
			data  = data.decode(encoding='utf-8')
			print("Recive:"+ReciveIP+"->["+data+"]")
			my = data.split("|")
			requir_domain_name = my[0]
			requir_domain_ip = my[1]
			#没有相同ip没有相同mac说明是新机器需要记录
			if self.ip_list.count(ReciveIP)==0 and self.mac_list.count(requir_domain_name)==0:
				self.ip_list.append(ReciveIP)
				self.mac_list.append(requir_domain_name)
				self.client_require_domain_name.append(requir_domain_ip)
			#有相同ip却有不同mac说明同一网段重复提交，更新mac
			elif self.ip_list.count(ReciveIP)!=0 and self.mac_list.count(requir_domain_name)==0:
				self.mac_list[self.ip_list.index(ReciveIP)]= requir_domain_name
			#没有相同ip有相同mac说明ip地址被改变需要重写记录
			elif self.ip_list.count(ReciveIP)==0 and self.mac_list.count(requir_domain_name)!=0:
				self.ip_list[self.mac_list.index(requir_domain_name)]= ReciveIP
			#有相同ip却有相同mac说明重复提交，保持不变
			else:
				self.client_require_domain_name[self.ip_list.index(ReciveIP)]= requir_domain_ip
		self.udpServer.close()
	def start_recive_ddns_config_thread(self):
		thread1 = threading.Thread(target=self.recive_udp_message,name="线程1",args=("123","123"))
		thread1.start()

if __name__ == '__main__':
	domain_name = 'qinbatista.com'
	if domain_name =='': domain_name = input('input your domain name:')
	ddns = DDNSServer(12345,domain_name)
	ddns.get_host_ip()
	ddns.deploy_ddns_server()
	ddns.start_sync_ddns_config_thread()
	ddns.start_recive_ddns_config_thread()