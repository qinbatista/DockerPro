import os
import sys
import time
import json
import random
from aiohttp import web
import threading
from boto3.dynamodb.conditions import Key
import boto3
import redis
import traceback

class CacheManager:
	def __init__(self):
		self.connection = redis.StrictRedis(connection_pool=redis.ConnectionPool(host="gamesupport.singmaan.com", password="aws@@#!#!@#@111:", port=6400))
	
	async def set_login_time(self,username,time):
		result = {"status": 500, "message": "record user original login time failed", "data": {}}
		d1 = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
		d2 = datetime.strptime((datetime.utcnow()+timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')
		timer_sceonds = (d2-d1).total_seconds()
		remaining_time = self.connection.ttl("origin_login_time_"+username)
		print("remaining_time="+str(remaining_time))
		time_to_next_day = int(timer_sceonds-8*60*60)
	
		try:
			self.connection.setex(name="origin_login_time_"+username, time=time_to_next_day, value=time)
			result = {"status": 200, "message": "record user original login time success", "data": {"refresh_time":remaining_time}}
		except:
			print(traceback.format_exc())
		return result
	
	async def get_login_time(self,username):
		result = self.connection.get(name="origin_login_time_"+username)
		if result:
			return {"status": 200, "message": "get user original login time", "data": result.decode()}
		return {"status": 200, "message": "user original login time is dismissed or none", "data": ""}

	
	async def set_authentication(self,username,code):
		result = {"status": 500, "message": "record user authentication failed", "data": {}}
		try:
			self.connection.set(name="authentication_info"+username,value=code)
			result = {"status": 200, "message": "record user authentication success", "data": {}}
		except:
			print(traceback.format_exc())
		return result
	

	async def get_authentication(self,username):
		result = self.connection.get(name="authentication_info"+username)
		if result:
			return {"status": 200, "message": "get user authentication", "data": result.decode()}
		return {"status": 200, "message": "user authentication is dismissed or none", "data": ""}


class LoginSystemManager:
	def __init__(self, worlds = []):
		self.__aws_init()

	def __aws_init(self):
		self.__dynamodb = boto3.resource('dynamodb', region_name='cn-northwest-1',aws_access_key_id='AKIAYDN4Q6OUMFA7F46S', aws_secret_access_key='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')
		self.__table = self.__dynamodb.Table('AccountSys')


	def __aws_download(self, unique_id, game_name):
		message = self.__table.get_item(Key={"unique_id": unique_id, "game_name": game_name})
		return message["Item"]["game_data"]

	def __aws_account_query(self, account, password):
		resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
		id_account = len(resp["Items"])
		if id_account == 0:
			print("creating a new account:"+str(id_account))
			self.__aws_account_create(account, password)
			return False,resp["Items"]
		if id_account == 1:
			print("verify a old account:"+str(id_account))
			return True,resp["Items"]

	def __aws_account_query_only(self, account, password):
		resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
		id_account = len(resp["Items"])
		if id_account == 0:
			print("don't have such account:"+str(id_account))
			return False,resp["Items"]
		if id_account == 1:
			print("verify a old account:"+str(id_account))
			return True,resp["Items"]

	def __aws_account_create(self, account, password):
		resp = self.__table.update_item(
			Key={"account": account},ExpressionAttributeNames={"#password": "password",},
			ExpressionAttributeValues={":password": password,},
			UpdateExpression="SET #password = :password",
		)
		return str(resp)

	def __create_token(self):
		pass

	def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
		return {"status": status, "message": message, "data": data}

	async def signeinwithpassword(self, account, password):
		query_result, context = self.__aws_account_query(account, password)
		print("context="+str(context))
		if query_result==True:
			if context[0]['password']==password:
				return self._message_typesetting(200,"login success, verified passed",{"result":{"query_result":query_result}})
			else:
				return self._message_typesetting(-200,"login failed,password failed",{"result":{"query_result":query_result}})
		else:
			return self._message_typesetting(201,"login success, created a new account",{"result":{"query_result":query_result}})

	async def loginwithpassword(self, account, password):
		query_result, context = self.__aws_account_query_only(account, password)
		print("context="+str(context))
		if query_result==True:
			if context[0]['password']==password:
				return self._message_typesetting(200,"login success, verified passed",{"result":{"chineseid":context[0]['chineseid'] if "chineseid" in context[0] else "" }})
			else:
				return self._message_typesetting(-200,"login failed,password failed",{"result":{"chineseid":""}})
		else:
			return self._message_typesetting(-201,"login failed, account don't exist",{"result":{"chineseid":""}})

	async def updatechineseid(self, account, chineseid):
		resp = self.__table.update_item(
			Key={"account": account},ExpressionAttributeNames={"#chineseid": "chineseid",},
			ExpressionAttributeValues={":chineseid": chineseid,},
			UpdateExpression="SET #chineseid = :chineseid",
		)
		print(str(resp))
		# print("context="+str(context))
		# if query_result==True:
		# 	if context[0]['password']==password:
		# 		return self._message_typesetting(200,"login success, verified passed",{"result":{"query_result":query_result}})
		# 	else:
		# 		return self._message_typesetting(-200,"login failed,password failed",{"result":{"query_result":query_result}})
		# else:
		return self._message_typesetting(200,"login success, created a new account",{"result":{"query_result":str(resp)}})



	async def downloadgamedata(self, game_name, unique_id):
		return self._message_typesetting(200,"download data success",{"result":self.__aws_download(game_name, unique_id)})

ROUTES = web.RouteTableDef()
def _json_response(body: dict = "", **kwargs) -> web.Response:
	kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
	kwargs['content_type'] = 'text/json'
	return web.Response(**kwargs)




#json param, get result from request post
#http://localhost:10012/signeinwithpassword
@ROUTES.post('/signeinwithpassword')
async def _signeinwithpassword(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['MANAGER']).signeinwithpassword(post['account'], post['password'])
	return _json_response(result)

#json param, get result from request post
#http://localhost:10012/loginwithpassword
@ROUTES.post('/loginwithpassword')
async def _loginwithpassword(request: web.Request) -> web.Response:
	post = await request.post()
	print("loginwithpassword="+str(post))
	result = await (request.app['MANAGER']).loginwithpassword(post['account'], post['password'])
	return _json_response(result)

#json param, get result from request post
#http://localhost:10012/loginwithtoken
@ROUTES.post('/updatechineseid')
async def _updatechineseid(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['MANAGER']).updatechineseid(post['account'], post['chinese_id'])
	return _json_response(result)

#json param, get result from request post
#http://localhost:10012/loginwithuniqueid
@ROUTES.post('/loginwithuniqueid')
async def _loginwithuniqueid(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['MANAGER']).loginwithuniqueid(post['unique_id'])
	return _json_response(result)


#json param, get result from request post
#http://localhost:10012/loginwithphonenumber
@ROUTES.post('/loginwithphonenumber')
async def _loginwithphonenumber(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['MANAGER']).loginwithphonenumber(post['unique_id'], post['phone_number'], post['code'])
	return _json_response(result)

@ROUTES.post('/setlogintime')
async def _set_login_time(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['CACHE']).set_login_time(post['account'], post['time'])
	return _json_response(result)

@ROUTES.post('/getlogintime')
async def _set_login_time(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['CACHE']).get_login_time(post['account'])
	return _json_response(result)


@ROUTES.post('/setauthentication')
async def _set_login_authentication(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['CACHE']).set_authentication(post['account'], post['code'])
	return _json_response(result)

@ROUTES.post('/getauthentication')
async def _set_login_authentication(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['CACHE']).get_authentication(post['account'])
	return _json_response(result)


@ROUTES.get('/healthcheck')
async def healthcheck(request: web.Request) -> web.Response:
	return _json_response(
		{
			"status":200,
			"message":"health",
			"data":True
		}
	)
from datetime import datetime
from datetime import timedelta
def run():
	print("LoginSystemManager version:1.2")
	app = web.Application()
	app.add_routes(ROUTES)
	app['MANAGER'] = LoginSystemManager()
	app['CACHE'] = CacheManager()
	web.run_app(app, port = "8080")


if __name__ == '__main__':
	run()
