
import os
import sys
import time
import json
import threading
class GameManager:
	def __init__(self, worlds = []):
		self.__updateverify_file_name = 'updateverify.json'
		self.__root_docker_files = os.path.dirname(os.path.realpath(__file__))
		self.__get_all_update_verify = dict()

	def _message_typesetting(self):
		print("_message_typesetting")

	def _get_all_config(self):
		print("updated thread")
		thread1 = threading.Thread(target=self._config_update)
		thread1.start()

	def _get_docker_name(self, _path):
		if os.path.isfile(_path+"/docker-name"):
			with open(_path+"/docker-name","r",encoding="UTF-8") as file_object:
				docker_name = file_object.readline()
			print(docker_name)
			return docker_name
		else:
			return ""


	def _config_update(self):
		# print("updated _config_update")
		folder_list = os.listdir(self.__root_docker_files)
		# print("folder_list="+str(folder_list))
		for folder_name in folder_list:
			if folder_name.find(".")==-1 and folder_name.find("@")==-1:
				os.system("pwd")
				docker_name = self._get_docker_name(self.__root_docker_files+'/'+folder_name)
				if docker_name !="":
					print("updating docker:"+self.__root_docker_files+'/'+folder_name)
					os.chdir(self.__root_docker_files+'/'+folder_name)
					os.system("docker build -t "+docker_name+" .")
					os.chdir(self.__root_docker_files)
					os.system("docker push "+docker_name)
					print("docker updated")
			# time.sleep(10)
		os.system("docker rmi $(docker images | grep \"<none>\" | awk '{print $3}')")
		os.system("docker rm $(docker ps -aq)")
		os.system("docker rmi $(docker images | awk '{print $3}')")
	async def function_hello(self, world: int, unique_id: str):
		# card_info = await self._execute_statement(world, f'select vip_card_type from player where unique_id="{unique_id}"')
		return self._message_typesetting(200,"this is message",{"status":"200","wtf":"a"})

	async def function_hello_noparam(self):
		# card_info = await self._execute_statement(world, f'select vip_card_type from player where unique_id="{unique_id}"')
		return self._message_typesetting(200,"this is message",{"status":"200","wtf":"a"})

	async def get_update_verify(self, game_name: str):
		if game_name in self.__get_all_update_verify:
			return self._message_typesetting(200,"success",{"status":"200","result":self.__get_all_update_verify[game_name]})
		else:
			return self._message_typesetting(201,"failed",{"status":"200","result":"no such game:"+game_name})


def run():
	gm = GameManager()
	gm._get_all_config()


if __name__ == '__main__':
	run()
