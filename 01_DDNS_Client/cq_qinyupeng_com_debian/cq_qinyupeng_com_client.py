import os
import time
import requests
import base64
import threading
import uuid
import subprocess
from socket import *
class DDNSClient:
    def __init__(self):
        self._user_name = "kFpbr4qT6tYHCXCv"
        self._password = "q6Ss3kMSfKF5BngQ"
        self._my_domain = "cq.qinyupeng.com"
        self.__target_server = "us.qinyupeng.com"
        self._get_ip_website = "https://checkip.amazonaws.com"#https://domains.google.com/checkip banned by Chinese GFW

    def _start(self):
        while True:
            _fn_stdout = "/root/_get_static_ip_stdout"+str(uuid.uuid4())+".json"
            _fn_tderr = "/root/_get_static_ip_stderr"+str(uuid.uuid4())+".json"
            _get_static_ip_stdout = open(_fn_stdout, 'w+')
            _get_static_ip_stderr = open(_fn_tderr, 'w+')
            process = subprocess.Popen("ssr start", stdout=_get_static_ip_stdout,stderr=_get_static_ip_stderr,universal_newlines=True, shell=True)
            # process = subprocess.Popen("ssr start", universal_newlines=True, shell=True)
            process.wait()
            time.sleep(20)
            self.__post_ip_address()
            time.sleep(20)
            process = subprocess.Popen("ssr stop", stdout=_get_static_ip_stdout,stderr=_get_static_ip_stderr,universal_newlines=True, shell=True)
            # process = subprocess.Popen("ssr stop", universal_newlines=True, shell=True)
            process.wait()
            # os.system("ssr stop")
            os.remove(_fn_stdout)
            os.remove(_fn_tderr)
            

    def _declare_alive(self):
        thread_refresh = threading.Thread(target=self.thread_declare_alive, name="t1", args=())
        thread_refresh.start()

    def thread_declare_alive(self):
        while True:
            try:
                udpClient = socket(AF_INET,SOCK_DGRAM)
                # udpClient.sendto("cq".encode(encoding="utf-8"),("35.167.51.108",7171))
                udpClient.sendto(gethostbyname(self.__target_server).encode(encoding="utf-8"),(self.__target_server,7171))
                data, server = udpClient.recvfrom(4096)
                ip = gethostbyname(self.__target_server)
                # print("thread_declare_alive:"+str(data)+","+str(ip))
                time.sleep(5)
            except Exception as e:
                print("thread_declare_alive"+str(e))

    def __get_host_ip(self):
        _ip = ""
        try:
            _ip = requests.get(self._get_ip_website).text.strip()
        except Exception as e:
            print("error when requesting ip"+str(e))
        return _ip

    def __post_ip_address(self):

        try:
            udpClient = socket(AF_INET,SOCK_DGRAM)
            # udpClient.sendto("cq".encode(encoding="utf-8"),("35.167.51.108",7171))
            udpClient.sendto(gethostbyname(self.__target_server).encode(encoding="utf-8"),(self.__target_server,7171))
            data, server = udpClient.recvfrom(4096)
            ip = gethostbyname(self.__target_server)
            # print("thread_declare_alive:"+str(data)+","+str(ip))
            time.sleep(5)
        except Exception as e:
            print("thread_declare_alive"+str(e))

        try:
            _fn_stdout = "/root/__post_ip_address"+str(uuid.uuid4())+".json"
            _fn_tderr = "/root/__post_ip_address"+str(uuid.uuid4())+".json"
            _get_static_ip_stdout = open(_fn_stdout, 'w+')
            _get_static_ip_stderr = open(_fn_tderr, 'w+')
            command = "proxychains curl -i -H 'Authorization:Basic "+self.__base64()+"' -H 'User-Agent: google-ddns-updater email@yourdomain.com' https://"+self._user_name+":"+self._password+"@domains.google.com/nic/update?hostname="+self._my_domain+" -d 'myip="+self.__get_host_ip()+"' > /dev/null"
            process = subprocess.Popen(command, stdout=_get_static_ip_stdout,stderr=_get_static_ip_stderr,universal_newlines=True, shell=True)
            # process = subprocess.Popen(command,universal_newlines=True, shell=True)
            process.wait()
            os.remove(_fn_stdout)
            os.remove(_fn_tderr)
        except Exception as e:
            print("error when updating ip"+str(e))

    def __base64(self):
        theString = self._user_name+":"+self._password
        encoded_string = base64.b64encode(theString.encode('ascii') )
        return encoded_string.decode('ascii')

if __name__ == '__main__':
    # os.system("ssr start")
    ss = DDNSClient()
    # ss._declare_alive()
    ss._start()