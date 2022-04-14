#coding=UTF-8
import asyncio
import sys
import ssl
import json
import os
from datetime import datetime
import threading
import subprocess
import time
from subprocess import Popen, PIPE
import urllib.request
import urllib.parse
from pathlib import Path
from socket import *
import datetime
import shutil
class QinServer:
    def __init__(self, host: str = '', port: int = 10005):
        self._host = host
        self._port = port
        self._tool_package = "yt-dlp"#"youtube-dl"
        self._crt = '/mycert.crt'
        self._key = '/rsa_private.key'
        self._password = 'lukseun1'
        self._exclude_files=['ssl_cert','tcp_dl_client.py','tcp_dl_server.py','.DS_Store']
        self._cache_folder = '/download/deliveried'
        self._root_folder = '/download'
        self._storage_server_ip = 'cq.qinyupeng.com'
        self._storage_server_port = 10022
        self._request_server_port = '10015'
        if not os.path.exists(self._root_folder):os.makedirs(self._root_folder)
        if not os.path.exists(self._cache_folder):os.makedirs(self._cache_folder)
        self.__downloading_list = []
        config_file = open('./Config_YoutubeList/config.json')
        data = json.load(config_file)
        self.mapping_table = data
        self._video_list_monitor_thread()

    async def __echo(self,reader, writer):
        address = writer.get_extra_info('peername')
        data = await reader.readuntil(b'\r\n')
        resp = data.decode().strip()
        message,msg_type,proxy =self.__parse_message(resp)
        await self.__mission_manager(message,msg_type,proxy)
        writer.write(b'start downloading'+"->".encode('utf-8')+message.encode('utf-8')+b'\r\n')
        await writer.drain()

    def __isServerOpening(self,ip,port):
        # if datetime.datetime.now().hour>15 and datetime.datetime.now().hour<23:
        # 	print("__isServerOpening hour = false, datetime.datetime.now().hour="+str(datetime.datetime.now().hour))
        # 	return False
        # else:
        # 	isConnected = False
        # 	print("__isServerOpening hour = true,datetime.datetime.now().hour="+str(datetime.datetime.now().hour))
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.settimeout(5)
            s.connect((ip, port))
            isConnected = True
        except Exception as error:
            time.sleep(1)
            # print(error)
            isConnected = False
        finally:
            s.close()
            return isConnected

    def start_server(self):
        SERVER_ADDRESS = (self._host, self._port)
        event_loop = asyncio.get_event_loop()
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain(self._crt, self._key,password = self._password)
        factory = asyncio.start_server(self.__echo, *SERVER_ADDRESS, ssl=ssl_context)
        server = event_loop.run_until_complete(factory)
        # print('starting up on {} port {}'.format(*SERVER_ADDRESS))
        try:
            event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            event_loop.run_until_complete(server.wait_closed())
            # print('closing event loop')
            event_loop.close()

    def _video_list_monitor_thread(self):
        thread1 = threading.Thread(target=self._loop_message, name="t1",args=())
        thread1.start()

    def _loop_message(self):
        while True:
            time.sleep(10)
            for key in self.mapping_table.keys():
                # print("---key="+key)
                # self._youtube_sync_command(f"https://www.youtube.com/playlist?list={key}")
                self.__thread_youtube_sync(f"https://www.youtube.com/playlist?list={key}")
                time.sleep(10)
            time.sleep(600)
            # os.system(f"rm -rf {self._root_folder}")

    def __parse_message(self,msg):
        my_json = json.loads(msg)
        return my_json["message"],my_json["type"],my_json["proxy"]

    def __command(self,command,args):
        #and then check the response...
        if self.__isServerOpening(self._storage_server_ip,self._storage_server_port):
            # print("Chongqing server is opening")
            #download files
            os.chdir("/")
            if not os.path.exists(self._root_folder):os.makedirs(self._root_folder)
            if not os.path.exists(self._cache_folder):os.makedirs(self._cache_folder)
            current_milli_time = lambda: int(round(time.time() * 1000))
            task_id = str(current_milli_time())
            os.mkdir(f'{self._root_folder}/{task_id}')
            if os.path.exists(f'{self._root_folder}/{task_id}'):
                os.chdir(f'{self._root_folder}/{task_id}')
            # print("command:"+command)
            path_to_output_file_downloading = f'{self._root_folder}/{task_id}/downloading_log.txt'
            path_to_output_file_syncing = f'{self._root_folder}/{task_id}/sync_log.txt'
            myoutput_downloading = open(path_to_output_file_downloading,'w+')
            myoutput_syncing = open(path_to_output_file_syncing,'w+')
            p = subprocess.Popen(command, stdout=myoutput_downloading, stderr= myoutput_downloading, universal_newlines=True, shell=True)
            p.wait()
            # print("downloaded all files, start sync files")

            p = subprocess.Popen(f'rsync -avz --progress -e "ssh -p {self._storage_server_port}" {self._root_folder}/{task_id} root@{self._storage_server_ip}:{self._root_folder}/ --delete', stdout=myoutput_syncing, stderr= myoutput_syncing, universal_newlines=True, shell=True)
            p.wait()
            # print("synced files, start delete cache")
            if not os.path.exists(f"{self._cache_folder}/{task_id}"):os.makedirs(f"{self._cache_folder}/{task_id}")
            os.system(f"mv {self._root_folder}/{task_id}/downloading_log.txt {self._cache_folder}/{task_id}")
            os.system(f"mv {self._root_folder}/{task_id}/sync_log.txt {self._cache_folder}/{task_id}")
            os.system(f"rm -rf {self._root_folder}/{task_id}")
            print("deleted cache, done")
        else:
            print("Chongqing server is closed")
            os.system(f"rm -rf {self._root_folder}/*")

    def __thread_download(self,command):
        thread1 = threading.Thread(target=self.__command, name="t1",args=(command,''))
        thread1.start()

    def __thread_youtube_sync(self,url):
        thread1 = threading.Thread(target=self._youtube_sync_command, name="t1",args=(url,''))
        thread1.start()

    def _youtube_sync_command(self, url,args):
        if self.__isServerOpening(self._storage_server_ip,self._storage_server_port):
            # print("1")
            current_milli_time = lambda: int(round(time.time() * 1000))
            task_id = str(current_milli_time())
            video_list_id = url[url.find("list=")+len("list="):]
            # print("video_list_id:"+video_list_id)
            if video_list_id in self.__downloading_list:
                # print(video_list_id + " is undering proccessing")
                return
            else:
                self.__downloading_list.append(video_list_id)
            # print("1.1")
            # f = urllib.request.urlopen('http://'+self._request_server_ip+":"+self._request_server_port+'/get_video_list?list_id='+video_list_id)
            # video_list_server = json.loads(f.read().decode('utf-8'))
            # print("video_list_server['data']['video_list']="+str(video_list_server['data']['video_list']))
            # print("folder_list['data'][folder_list]="+str(video_list_server['data']['folder_list']))
            # print("---self.mapping_table="+str(self.mapping_table))
            # print("---self.mapping_table[video_list_id]="+str(self.mapping_table[video_list_id]))
            string_list = list(self.mapping_table[video_list_id])
            # print("string_list="+str(string_list))
            folder_name = string_list[0][string_list[0].rfind("/")+1:]
            # print("1folder_name="+folder_name)
            task_id = folder_name
            Path(f'{self._root_folder}/{task_id}').mkdir(parents=True, exist_ok=True)
            # print("1.2")
            video_list = open(f'{self._root_folder}/{task_id}/video_list.txt','w+')
            download_log = open(f'{self._root_folder}/{task_id}/download_log.txt','w+')
            sync_log = open(f'{self._root_folder}/{task_id}/sync_log.txt','w+')
            sync_log_error = open(f'{self._root_folder}/{task_id}/sync_log_error.txt','w+')
            remote_video_list = open(f'{self._root_folder}/{task_id}/remote_video_list.txt','w+')
            if os.path.exists(f'{self._root_folder}/{task_id}')==False:os.mkdir(f'{self._root_folder}/{task_id}')
            if os.path.exists(f'{self._root_folder}/{task_id}'):
                os.chdir(f'{self._root_folder}/{task_id}')
            # print("2")
            p = subprocess.Popen("ssh -p 10022 root@"+self._storage_server_ip+" ls -l "+string_list[0], stdout=remote_video_list, stderr= remote_video_list, universal_newlines=True, shell=True)
            p.wait()
            p = subprocess.Popen(self._tool_package+" -j --flat-playlis "+url, stdout=video_list, stderr= video_list, universal_newlines=True, shell=True)
            p.wait()
            lines = {}
            youtube_video_list = []
            new_video_id_list = []
            youtube_video_id_list = []
            with open(f'{self._root_folder}/{task_id}/video_list.txt') as f:
                lines = f.readlines()
            for line in lines:
                if self.__is_json(line):
                    line_to_json = json.loads(line)
                    youtube_video_list.append(line_to_json["id"])
                    youtube_video_id_list.append(line_to_json["id"])
            new_video_id_list = youtube_video_list
            with open(f'{self._root_folder}/{task_id}/remote_video_list.txt') as f:
                remote_video_list = f.readlines()
            # print("4")
            for remote_video_id in remote_video_list:
                for youtube_video_id in youtube_video_list:
                    if remote_video_id.find(youtube_video_id)!=-1 and len(youtube_video_id)>=5:
                        new_video_id_list.remove(youtube_video_id)
                        # print("removed "+youtube_video_id)
                        # print("["+remote_video_id+"]contained")
            # print("downloading list totall:"+str(len(youtube_video_id_list)))
            # print("downloading list remaining:"+str(len(new_video_id_list)))
            # print("3")
            for video_id in new_video_id_list:
                if os.path.exists(f'{self._root_folder}/{task_id}'):
                    os.chdir(f'{self._root_folder}/{task_id}')
                # print(f"{self._tool_package} -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio' --merge-output-format mp4 https://www.youtube.com/watch?v={video_id}")
                p = subprocess.Popen(f"{self._tool_package} -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio' --merge-output-format mp4 https://www.youtube.com/watch?v={video_id}", stdout=download_log, stderr=download_log, universal_newlines=True, shell=True)
                p.wait()
                is_found_vdeio = False
                while True:
                    if os.path.exists(f'{self._root_folder}/{task_id}'):
                        cache_video = os.listdir(f'{self._root_folder}/{task_id}')
                    for item in cache_video:
                        if item.endswith(".mp4"):
                            # print(self._root_folder+"/"+task_id+" downloaded")
                            is_found_vdeio = True
                    if is_found_vdeio:
                        break
                    time.sleep(5)
                for index, i in enumerate(range(len(string_list))):
                    destination_folder = string_list[index].replace(task_id,"")
                    if os.path.exists(f'{self._root_folder}/{task_id}'):
                        cache_video = os.listdir(f'{self._root_folder}/{task_id}')
                    for item in cache_video:
                        if item.endswith(".mp4"):
                            for file_index, line in enumerate(youtube_video_id_list):
                                if video_id in line:
                                    if os.path.exists(f'{self._root_folder}/{task_id}/{item}'):
                                        os.rename(f'{self._root_folder}/{task_id}/{item}',f'{self._root_folder}/{task_id}/[{len(youtube_video_id_list)-file_index}]{item}')
                                    # print("[files in folder]"+str(os.listdir(f'{self._root_folder}/{task_id}')))
                                    if os.path.exists(f'{self._root_folder}/{task_id}/[{len(youtube_video_id_list)-file_index}]{item}'):
                                        sync_failed = True
                                        while sync_failed:
                                            p = subprocess.Popen(f'rsync -avz -I --progress -e "ssh -p {self._storage_server_port}" {self._root_folder}/{task_id} root@{self._storage_server_ip}:{destination_folder}', stdout=sync_log, stderr= sync_log_error, universal_newlines=True, shell=True);p.wait()
                                            if os.stat(f'{self._root_folder}/{task_id}/sync_log_error.txt').st_size != 0:
                                                # print("sync failed: will retry 1 mins later")
                                                shutil.move(f'{self._root_folder}/{task_id}/sync_log_error.txt',f'{self._root_folder}/{task_id}/sync_log_error_{file_index}.txt')
                                                sync_log_error = open(f'{self._root_folder}/{task_id}/sync_log_error.txt','w+')
                                                time.sleep(60)
                                            else:
                                                sync_failed = False
                                                if os.path.exists(f'{self._root_folder}/{task_id}/sync_log.txt'):
                                                    os.remove(f'{self._root_folder}/{task_id}/sync_log.txt')
                                                sync_log_error = open(f'{self._root_folder}/{task_id}/sync_log.txt','w+')
                                                # print(f'sync successed: rsync -avz -I --progress -e "ssh -p {self._storage_server_port}" {self._root_folder}/{task_id} root@{self._storage_server_ip}:{destination_folder}')
                                    else:
                                        pass
                                        # print(f'sync failed:{self._root_folder}/{task_id}/[{len(youtube_video_id_list)-file_index}]{item} doesnt exist')
                                    sync_failed = True

                if os.path.exists(f'{self._root_folder}/{task_id}'):
                    cache_video = os.listdir(f'{self._root_folder}/{task_id}')
                for item in cache_video:
                    if item.endswith(".mp4") and os.path.exists(os.path.join(f'{self._root_folder}/{task_id}', item)):
                        os.remove(os.path.join(f'{self._root_folder}/{task_id}', item))
                        # print("deleted "+item)
            if os.path.exists(f"{self._root_folder}"):
                self.__downloading_list.remove(video_list_id)
        else:
            # print("5")
            self.__downloading_list.clear()
            if os.path.exists(f"{self._root_folder}"):
                os.system(f"rm -rf {self._root_folder}/*")

    def __is_json(self,myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    async def __mission_manager(self,message,type,proxy):
        p = subprocess.Popen("python3 -m pip install --upgrade pip",universal_newlines=True, shell=True);p.wait()
        p = subprocess.Popen("pip3 install "+self._tool_package+" --upgrade",universal_newlines=True, shell=True);p.wait()
        if proxy!='': proxy = 'proxychains'
        if   type == self._tool_package: self.__thread_download(f"{proxy} {type} -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio' --merge-output-format mp4 {message}")
        elif type == "wget": self.__thread_download(f'{proxy} {type} {message}')
        elif type == "instagram-scraper": self.__thread_download(f'{proxy} {type} {message}')
        elif type == "aria2c": self.__thread_download(f'{proxy} {type} {message}')
        elif type == "command": self.__thread_download(f'{proxy} {message}')
        elif type == "youtube": self.__thread_download(f'{proxy} {message}')
        elif type == "sync_youtube": self.__thread_youtube_sync(f'{proxy} {message}')

if __name__ == "__main__":
    os.system("cat  ~/.ssh/id_rsa.pub")
    os.system(f"rm -rf /download/*")
    os.system('rsync -avz --progress -e "ssh -o stricthostkeychecking=no -p 10022" /download root@cq.qinyupeng.com:~/')
    os.system("pwd")
    os.system("git clone git@github.com:qinbatista/Config_YoutubeList.git")
    qs = QinServer()
    p = subprocess.Popen("python3 -m pip install --upgrade pip",universal_newlines=True, shell=True);p.wait()
    p = subprocess.Popen("pip3 install "+qs._tool_package+" --upgrade",universal_newlines=True, shell=True);p.wait()
    qs.start_server()



