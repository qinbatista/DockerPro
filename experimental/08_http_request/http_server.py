
import os
import sys
import time
import json
import random
import aiomysql
from aiohttp import web
import threading
class GameManager:
	def __init__(self, worlds = []):
		self.__updateverify_file_name = 'updateverify.json'
		self.__root_OperationLives = '/root/operationlives'
		self.__get_all_update_verify = dict()
		self._get_all_config()
	async def _connect_sql(self):
		self._pool = await aiomysql.create_pool(
				maxsize = 20,
				host = '192.168.1.102',
				user = 'root',
				password = 'lukseun',
				charset = 'utf8',
				autocommit = True)
	async def _execute_statement(self, database_name: int, statement: str) -> tuple:
		"""
		Executes the given statement and returns the result.
		执行给定的语句并返回结果。
		:param statement: Mysql执行的语句
		:return: 返回执行后的二维元组表
		使用例子：data = await self._execute_statement(world, 'SELECT ' + material + ' FROM player WHERE unique_id="' + str(unique_id) + '";')
		"""
		if self._pool is None: await self._connect_sql()
		async with self._pool.acquire() as conn:
			await conn.select_db(database_name)
			async with conn.cursor() as cursor:
				await cursor.execute(statement)
				return await cursor.fetchall()
	async def _execute_statement_update(self, database_name: int, statement: str) -> int:
		"""
		Execute the update or set statement and return the result.
		执行update或set语句并返回结果。
		:param statement: Mysql执行的语句
		:return: 返回update或者是set执行的结果
		使用例子：return await self._execute_statement_update(world, f"UPDATE player SET {material}={value} where unique_id='{unique_id}'")
		"""
		if self._pool is None: await self._connect_sql()
		async with self._pool.acquire() as conn:
			await conn.select_db(database_name)
			async with conn.cursor() as cursor:
				return await cursor.execute(statement)
	def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
		return {"status": status, "message": message, "data": data}

	def _get_all_config(self):
		thread1 = threading.Thread(target=self._config_update)
		thread1.start()

	def _config_update(self):
		while True:
			folder_list = os.listdir(self.__root_OperationLives)
			for folder_name in folder_list:
				if folder_name.find(".")==-1 and folder_name.find("@")==-1:
					os.chdir(self.__root_OperationLives+'/'+folder_name)
					os.system("git pull")
					os.chdir(self.__root_OperationLives)

			for folder_name in folder_list:
				if folder_name.find(".")==-1 and folder_name.find("@")==-1:
					with open(self.__root_OperationLives+'/'+folder_name+'/'+self.__updateverify_file_name, 'r') as f:
						my_json = json.load(f)
						self.__get_all_update_verify[folder_name] = my_json
			print("dic="+str(self.__get_all_update_verify))
			time.sleep(3600*24)

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




ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
	kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
	kwargs['content_type'] = 'text/json'
	return web.Response(**kwargs)

#json param, get OperationLives
#http://localhost:9988/get_update_verify?game_name=ww1
@ROUTES.post('/get_update_verify')
async def _get_update_verify(request: web.Request) -> web.Response:
	query = request.query
	result = await (request.app['MANAGER']).get_update_verify(query['gamename'])
	return _json_response(result)



#json param, get result from request post
#http://localhost:9988/function_hello_json
@ROUTES.post('/function_hello_json')
async def _function_hello_json(request: web.Request) -> web.Response:
	post = await request.post()
	result = await (request.app['MANAGER']).function_hello(int(post['world']), post['unique_id'])
	return _json_response(result)


#json param, get result from request query
#http://localhost:9988/function_hello_query?world=0&unique_id=aabbaaaaaaaaa
@ROUTES.post('/function_hello_query')
async def _function_hello_query(request: web.Request) -> web.Response:
	query =  request.query
	result = await (request.app['MANAGER']).function_hello(int(query['world']), query['unique_id'])
	return _json_response(result)

#no param, get result directly
#http://localhost:9988/function_hello_noparam
@ROUTES.get('/function_hello_noparam')
async def _function_hello_noparam(request: web.Request) -> web.Response:
	post = await request.post()
	result = await (request.app['MANAGER']).function_hello_noparam()
	return _json_response(result)

def run():
	app = web.Application()
	app.add_routes(ROUTES)
	app['MANAGER'] = GameManager()
	web.run_app(app, port = "9988")


if __name__ == '__main__':
	run()
