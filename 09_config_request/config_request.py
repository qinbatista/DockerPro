import os
import sys
import time
import json
import random
import aiomysql
from aiohttp import web
import threading
import redis
from redis import ConnectionPool

REDIS_COMFIG = {
    "host": "gamesupport.singmaan.com",
    "password":"!@WEwqqQ123",
    "decode_responses":True
}

class GameManager:
	def __init__(self, worlds = []):
		self.cache = redis.StrictRedis(connection_pool=ConnectionPool(**REDIS_COMFIG))
		self.__iap_list_file = "iap_list.json"
		self.__updateverify_file = "updateverify.json"
		self.__store_file = "store.json"
		self.__ad_file = "ad.json"
		self.__email_file = "mail.json"
		self.__game_list = '/root/operationlives'
		self.__git_list = '/root'
		# self.__game_list = '/data/SingmaanProject/operationlives'
		# self.__git_list = '/data/SingmaanProject'
		self.__rep_link = 'https://qinbatista:qinyupeng1@bitbucket.org/qinbatista/operationlives.git'
		self.__game_names = []
		self.__all_iap_config = {}
		self.__all_updateverify_config = {}
		self.__all_store_config = {}
		self.__all_ad_config = {}
		self.__all_email_config = {}
		self._set_all_config()

	def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
		return {"status": status, "message": message, "data": data}

	def _set_all_config(self):
		thread1 = threading.Thread(target=self._config_update)
		thread1.start()

	def _config_update(self):
		while True:
			self._refresh_config()
			time.sleep(60*60*24)
			print("restart reading config")

	def _config_git(self):
		# print("updated _config_update")
		os.system("pwd")
		os.chdir(self.__git_list)
		os.system("git clone "+self.__rep_link)
		os.chdir(self.__game_list)
		os.system("git pull")
		print("updated repositoriy")

	def _refresh_config(self):
		print("start reading config")
		self._config_git()
		os.chdir(self.__git_list)
		self.__all_iap_config = {}
		self.__all_updateverify_config = {}
		folder_list = os.listdir(self.__game_list)
		for game_name in folder_list:
			if game_name.rfind("")!=-1 and game_name.rfind(".")!=-1:
				continue

			print("updating:"+game_name+"....")
			#add iap_list.json
			if os.path.exists(f"{self.__game_list}/{game_name}/{self.__iap_list_file}"):
				with open(f"{self.__game_list}/{game_name}/{self.__iap_list_file}", 'r') as f:
					print("updated iap_list:"+game_name)
					self.__all_iap_config[game_name] = json.load(f)

			#add updateverify.json
			if os.path.exists(f"{self.__game_list}/{game_name}/{self.__updateverify_file}"):
				with open(f"{self.__game_list}/{game_name}/{self.__updateverify_file}", 'r') as f:
					print("updated updateverify:"+game_name)
					self.__all_updateverify_config[game_name] = json.load(f)

			#add store.json
			if os.path.exists(f"{self.__game_list}/{game_name}/{self.__store_file}"):
				with open(f"{self.__game_list}/{game_name}/{self.__store_file}", 'r') as f:
					print("updated store:"+game_name)
					self.__all_store_config[game_name] = json.load(f)

			#add ad.json
			if os.path.exists(f"{self.__game_list}/{game_name}/{self.__ad_file}"):
				with open(f"{self.__game_list}/{game_name}/{self.__ad_file}", 'r') as f:
					print("updated ad:"+game_name)
					self.__all_ad_config[game_name] = json.load(f)

			# add mail.json
			if os.path.exists(f"{self.__game_list}/{game_name}/{self.__email_file}"):
				with open(f"{self.__game_list}/{game_name}/{self.__email_file}", 'r') as f:
					print("updated mail:"+game_name)
					self.__all_email_config[game_name] = json.load(f)
		print("end reading config")

	async def refresh(self):
		self._refresh_config()
		return self._message_typesetting(200,"refresh config success")


	async def get_iap(self, game_name:str):
		if game_name not in self.__all_iap_config:
			# print("self.__all_iap_config="+str(self.__all_iap_config))
			return self._message_typesetting(400,"error",{"status":"200","message":"don't have such game config:"+game_name})
		else:
			return self._message_typesetting(200,"got config success",{"result":self.__all_iap_config[game_name]})

	async def get_update_verify(self, game_name:str):
		if game_name not in self.__all_updateverify_config:
			return self._message_typesetting(400,"error",{"status":"200","message":"don't have such game config:"+game_name})
		else:
			return self._message_typesetting(200,"got config success",{"result":self.__all_updateverify_config[game_name]})

	async def store(self, game_name:str):
		if game_name not in self.__all_store_config:
			return self._message_typesetting(400,"error",{"status":"200","message":"don't have such game config:"+game_name})
		else:
			return self._message_typesetting(200,"got config success",{"result":self.__all_store_config[game_name]})

	async def get_ad_permition(self, game_name:str):
		#get ad.json
		if game_name in self.__all_ad_config:
			result = self.__all_ad_config[game_name]
			return self._message_typesetting(200,"success",{"result":result})
		return self._message_typesetting(200,"success",{"isAdAccessable":True})

	async def get_email(self, game_name:str):
		# print("self.__all_email_config[game_name]="+str(self.__all_email_config))
		if game_name not in self.__all_email_config:
			return self._message_typesetting(400,"no such game in config",{game_name})
		# print("self.__all_email_config[game_name]="+str(self.__all_email_config[game_name]))
		# if self.cache.hget("email_flag", f"{uid}_{game_name}_{version}"):
		# 	return self._message_typesetting(400, "already get",{})
		# else:
		# 	version = self.__all_email_config[game_name]['version']
		# 	self.cache.hset("email_flag", f"{uid}_{game_name}_{version}", 1)
		return self._message_typesetting(200,"get email success",self.__all_email_config[game_name])


ROUTES = web.RouteTableDef()
def _json_response(body: dict = "", **kwargs) -> web.Response:
	kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
	kwargs['content_type'] = 'text/json'
	return web.Response(**kwargs)

#json param, get result from request post
#http://localhost:10001/get_iap?gamename=ww1
@ROUTES.post('/get_iap')
async def _get_iap(request: web.Request) -> web.Response:
	query = request.query
	result = await (request.app['MANAGER']).get_iap(query['gamename'])
	return _json_response(result)

#json param, get OperationLives
#http://localhost:10001/get_update_verify?game_name=ww1
@ROUTES.post('/get_update_verify')
async def _get_update_verify(request: web.Request) -> web.Response:
	query = request.query
	result = await (request.app['MANAGER']).get_update_verify(query['gamename'])
	return _json_response(result)

#json param, get OperationLives
#http://office.singmaan.com:10001/store?gamename=TerraGenesis
@ROUTES.post('/store')
async def _store(request: web.Request) -> web.Response:
	query = request.query
	result = await (request.app['MANAGER']).store(query['gamename'])
	return _json_response(result)

#no param, get result directly
#http://office.singmaan.com:10001/refresh
@ROUTES.get('/refresh')
async def _refresh(request: web.Request) -> web.Response:
	post = await request.post()
	result = await (request.app['MANAGER']).refresh()
	return _json_response(result)


#no param, get result directly
#http://office.singmaan.com:10001/refresh
@ROUTES.get('/getemail')
async def _refresh(request: web.Request) -> web.Response:
	query = request.query
	result = await (request.app['MANAGER']).get_email(query['gamename'])
	return _json_response(result)


@ROUTES.get('/healthcheck')
async def healthcheck(request: web.Request) -> web.Response:
	return  _json_response(
		{
			"status": 200,
			"message": "health",
			"data": True
		}
    )

@ROUTES.get('/isadaccessable')
async def _is_ad_accessable(request: web.Request) -> web.Response:
	query = request.query
	result = await (request.app['MANAGER']).get_ad_permition(query["game_name"])
	return _json_response(result)

def run():
	print("version:1.0")
	app = web.Application()
	app.add_routes(ROUTES)
	app['MANAGER'] = GameManager()
	web.run_app(app, port = "8080")


if __name__ == '__main__':
	run()
