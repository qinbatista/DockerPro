import os
import sys
import time
import json
import random
from aiohttp import web
import threading
import boto3
class LoginSystemManager:
	def __init__(self, worlds = []):
		self.__aws_init()

	def __aws_init(self):
		self.__dynamodb = boto3.resource('dynamodb', region_name='cn-northwest-1',aws_access_key_id='AKIAYDN4Q6OUMFA7F46S', aws_secret_access_key='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')
		self.__table = self.__dynamodb.Table('GameBackup')

	def __aws_upload(self,unique_id, game_name, game_data):
		resp = self.__table.update_item(
			Key={"unique_id": unique_id, "game_name": game_name},ExpressionAttributeNames={"#game_data": "game_data",},
			ExpressionAttributeValues={":game_data": game_data,},
			UpdateExpression="SET #game_data = :game_data",
		)
		return str(resp)

	def __aws_download(self, unique_id, game_name):
		message = self.__table.get_item(Key={"unique_id": unique_id, "game_name": game_name})
		return message["Item"]["game_data"]

	def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
		return {"status": status, "message": message, "data": data}

	async def uploadgamedata(self, game_name, unique_id, data):
		return self._message_typesetting(200,"upload data success",{"result":self.__aws_upload(game_name, unique_id, data)})

	async def downloadgamedata(self, game_name, unique_id):
		return self._message_typesetting(200,"download data success",{"result":self.__aws_download(game_name, unique_id)})

ROUTES = web.RouteTableDef()
def _json_response(body: dict = "", **kwargs) -> web.Response:
	kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
	kwargs['content_type'] = 'text/json'
	return web.Response(**kwargs)




#json param, get result from request post
#http://localhost:10010/uploadgamedata
@ROUTES.post('/uploadgamedata')
async def _uploadgamedata(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['MANAGER']).uploadgamedata(post['gamename'], post['unique_id'], post['data'])
	return _json_response(result)

#json param, get result from request post
#http://localhost:10010/downloadgamedata
@ROUTES.post('/downloadgamedata')
async def _downloadgamedata(request: web.Request) -> web.Response:
	post = await request.post()
	print("post="+str(post))
	result = await (request.app['MANAGER']).downloadgamedata(post['gamename'], post['unique_id'])
	return _json_response(result)



def run():
	print("GameDataBackupManager version:1.0")
	app = web.Application()
	app.add_routes(ROUTES)
	app['MANAGER'] = GameDataBackupManager()
	web.run_app(app, port = "10010")


if __name__ == '__main__':
	run()
