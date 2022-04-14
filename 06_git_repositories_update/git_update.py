
import os
import sys
import time
import json
import threading
class GameManager:
	def __init__(self, worlds = []):
		self.__updateverify_file_name = 'updateverify.json'
		self.__root_OperationLives = "/root/repositories"#'/root/repositories'#/Users/batista/SingmaanProject
		self.__get_all_update_verify = dict()

	def _message_typesetting(self):
		print("_message_typesetting")

	def _get_all_config(self):
		print("updated thread")
		thread1 = threading.Thread(target=self._config_update)
		thread1.start()

	def _config_update(self):
		while True:
			# print("updated _config_update")
			folder_list = os.listdir(self.__root_OperationLives)
			# print("folder_list="+str(folder_list))
			for folder_name in folder_list:
				if folder_name.find(".")==-1 and folder_name.find("@")==-1:
					os.system("pwd")
					print("updating:"+self.__root_OperationLives+'/'+folder_name)
					os.chdir(self.__root_OperationLives+'/'+folder_name)
					os.system("git pull")
					os.chdir(self.__root_OperationLives)
					os.system("pwd")
			print("updated repositoriy")
			time.sleep(10)
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
