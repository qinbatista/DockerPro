import os
import sys
import time
import json
import random
from aiohttp import web
import threading
import boto3
import traceback


class GameDataBackupManager:
    def __init__(self, worlds=[]):
        self.__aws_init()

    def __aws_init(self):
        self.__dynamodb = boto3.resource('dynamodb', region_name='cn-northwest-1',
                                         aws_access_key_id='AKIAYDN4Q6OUMFA7F46S',
                                         aws_secret_access_key='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')
        self.__s3 = boto3.resource("s3", region_name='cn-northwest-1', aws_access_key_id='AKIAYDN4Q6OUMFA7F46S',
                                   aws_secret_access_key='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')
        self.__bucket = self.__s3.Bucket("gamebackup")
        self.__table = self.__dynamodb.Table('GameBackup')

    def __aws_upload(self, unique_id, game_name, game_data):
        resp = ""
        try:
            key = f"{game_name}_{unique_id}"
            resp = self.__bucket.meta.client.put_object(Body=game_data, Key=key, ACL='public-read', Bucket="gamebackup")
        # resp = self.__table.update_item(
        # 	Key={"unique_id": unique_id, "game_name": game_name},ExpressionAttributeNames={"#game_data": "game_data",},
        # 	ExpressionAttributeValues={":game_data": game_data,},
        # 	UpdateExpression="SET #game_data = :game_data",
        # )
        except:
            print(traceback.format_exc())
        # key = f"{game_name}_{unique_id}"
        # resp = self.__bucket.meta.client.put_object(Body=game_data, Key=key, ACL='public-read',Bucket="gamebackup")
        return str(resp)


    def __aws_download(self, unique_id, game_name):
        try:
            key = f"{game_name}_{unique_id}"
            return self.__bucket.meta.client.get_object(Bucket="gamebackup", Key=key)["Body"].read().decode()
        except:
            print("The specified key does not exist.")
            message = self.__table.get_item(Key={"unique_id": unique_id, "game_name": game_name})
            if "Item" in message:
                return message["Item"]["game_data"]
            else:
                print("empty data")
                return ""


    def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
        return {"status": status, "message": message, "data": data}


    async def uploadgamedata(self, game_name, unique_id, data):
        return self._message_typesetting(200, "upload data success",
                                         {"result": self.__aws_upload(game_name, unique_id, data)})


    async def downloadgamedata(self, game_name, unique_id):
        return self._message_typesetting(200, "download data success",
                                         {"result": self.__aws_download(game_name, unique_id)})


ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
    kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
    kwargs['content_type'] = 'text/json'
    return web.Response(**kwargs)


# json param, get result from request post
# http://localhost:10010/uploadgamedata
@ROUTES.post('/uploadgamedata')
async def _uploadgamedata(request: web.Request) -> web.Response:
    post = await request.post()
    # print("post="+str(post))
    print("got uploadgamedata")
    print(post['gamename'], post['unique_id'])
    result = await (request.app['MANAGER']).uploadgamedata(post['gamename'], post['unique_id'], post['data'])
    return _json_response(result)


# json param, get result from request post
# http://localhost:10010/downloadgamedata
@ROUTES.post('/downloadgamedata')
async def _downloadgamedata(request: web.Request) -> web.Response:
    post = await request.post()
    print("got downloadgamedata")
    # print("post="+str(post))
    print(post['gamename'], post['unique_id'])
    result = await (request.app['MANAGER']).downloadgamedata(post['gamename'], post['unique_id'])
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

def run():
    print("GameDataBackupManager version:1.0")
    app = web.Application(client_max_size=1024**2*100)
    app.add_routes(ROUTES)
    app['MANAGER'] = GameDataBackupManager()
    web.run_app(app, port="8080")


if __name__ == '__main__':
    run()
