import subprocess
import uuid
import os
import json
import requests
import time
import threading
from socket import *
class LightSail:
    def __init__(self, _region, _server_name):
        self.__region = _region
        self.__server_name = _server_name
        self.__received_count = 0
        # self.__CN_timezone = pytz.timezone('Asia/Shanghai')
        self.__myip = ""
        self.__close_port = False
        self.__udpServer = socket(AF_INET,SOCK_DGRAM)

    def _allocateIP(self):
        cli_command = f"aws lightsail --no-paginate allocate-static-ip --static-ip-name {uuid.uuid4()} --region {self.__region} --no-cli-pager"
        result = self._exec_aws_command(cli_command)
        try:
            if result['operations'][0]['status'] == 'Succeeded':
                # print("_allocateIP a ip")
                return result['operations'][0]['resourceName']
        except Exception as e:
            print(f"[_allocateIP] error:"+str(e))
            return -1

    def _get_static_ip(self):
        # execute aws command
        cli_command = f"aws lightsail get-static-ip --static-ip-name StaticIp-1 --region {self.__region} --no-cli-pager"
        result = self._exec_aws_command(cli_command)
        # print(result)

    def _exec_aws_command(self, command):
        _fn_stdout = f"/root/_get_static_ip_stdout{uuid.uuid4()}.json"
        _fn_tderr = f"/root/_get_static_ip_stderr{uuid.uuid4()}.json"
        _get_static_ip_stdout = open(_fn_stdout, 'w+')
        _get_static_ip_stderr = open(_fn_tderr, 'w+')
        process = subprocess.Popen(command, stdout=_get_static_ip_stdout,
                                   stderr=_get_static_ip_stderr, universal_newlines=True, shell=True)
        process.wait()
        # reuslt
        aws_result = ""
        filesize = os.path.getsize(_fn_tderr)
        if filesize == 0:
            # print("The file is empty: " + str(filesize))
            with open(_fn_stdout) as json_file:
                result = json.load(json_file)
            aws_result = result
        else:
            with open(_fn_tderr) as json_file:
                aws_result = json_file.read()
        # clean cache files
        os.remove(_fn_stdout)
        os.remove(_fn_tderr)
        # print(aws_result)
        return aws_result

    def _release_static_ip(self, _ips):
        for ip in _ips:
            cli_command = f"aws lightsail --no-paginate  release-static-ip --static-ip-name {ip} --region {self.__region} --no-cli-pager"
            self._exec_aws_command(cli_command)
            # print("_release_static_ip released a ip")

    def _get_unattached_static_ips(self):
        try:
            cli_command = f"aws lightsail --no-paginate  get-static-ips --region {self.__region} --no-cli-pager"
            result = self._exec_aws_command(cli_command)
            unattached_ips = []
            for ip in result["staticIps"]:
                if ip["isAttached"] == False:
                    unattached_ips.append(ip["name"])
            return unattached_ips
        except Exception as e:
            print(f"[_get_unattached_static_ips] error:"+str(e)+" result:"+result)
            return -1

    def _check_instance_ip_state(self):
        # print("start ip checking...")
        while True:
            self.__received_count = self.__received_count-1
            if self.__received_count <= -1800:
                self._replace_instance_ip()
                self.__received_count = 0
            time.sleep(1)
            # if int(datetime.now(self.__CN_timezone).strftime('%H'))<1 or int(datetime.now(self.__CN_timezone).strftime('%H'))>14:
                # self.__received_count = self.__received_count + 1

    def _get_message_from_remote(self):
        thread_refresh = threading.Thread(target=self._thread_refresh, name="t1", args=())
        thread_refresh.start()

    def _thread_refresh(self):
        self.__udpServer = socket(AF_INET,SOCK_DGRAM)
        self.__udpServer.bind(('',7171))
        while True:
            data,addr = self.__udpServer.recvfrom(1024)
            ip, port = addr
            # print(f"{data.decode(encoding='utf-8')} {ip} {port}")
            self.__udpServer.sendto(f"{ip}".encode('utf-8'), addr)
            # print(f"Hour:{int(datetime.now(self.__CN_timezone).strftime('%H'))}")
            # if int(datetime.now(self.__CN_timezone).strftime('%H'))>1 and int(datetime.now(self.__CN_timezone).strftime('%H'))<14:
            self.__received_count = 0
            self.__myip = data.decode(encoding='utf-8')

    def _refresh_IP(self):
        thread_refresh = threading.Thread(target=self._refresh_IP_thread, name="t1", args=())
        thread_refresh.start()

    def _refresh_IP_thread(self):
        while True:
            ls._post_ip_address()
            time.sleep(60)

    def _attach_static_ip(self, ip_name, _instance_name):
        cli_command = f"aws lightsail --no-paginate  attach-static-ip --static-ip-name {ip_name} --instance-name {_instance_name} --region {self.__region} --no-cli-pager"
        result = self._exec_aws_command(cli_command)
        try:
            # print(result)
            if result['operations'][0]['status'] == 'Succeeded':
                pass
                # print("_attach_static_ip success")
            else:
                print("_attach_static_ip"+str(result))
        except Exception as e:
                print("_attach_static_ip"+str(e))

    def _replace_instance_ip(self):
        result = self._allocateIP()
        if(result != -1):
            self._attach_static_ip(result, self.__server_name)
        self._release_static_ip(self._get_unattached_static_ips())
        self._post_ip_address()

    def _get_host_ip(self):
        try:
            return requests.get('https://checkip.amazonaws.com').text.strip()
        except Exception as e:
            # print(f"[_get_host_ip]using ip {self.__myip}, error:"+str(e))
            return self.__myip

    def _post_ip_address(self):
        try:
            requests.post("https://:@domains.google.com/nic/update?hostname=us.qinyupeng.com&myip="+self._get_host_ip())
        except Exception as e:
            print(f"_post_ip_address:"+str(e)+" self.__myip="+self.__myip)

if __name__ == '__main__':
    ls = LightSail("us-west-2", "Debian-1")
    ls._post_ip_address()
    ls._get_message_from_remote()
    ls._refresh_IP()
    ls._check_instance_ip_state()
