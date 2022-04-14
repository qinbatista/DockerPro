from aiohttp import web
import socket
import time
import asyncio
import ssl
import threading
import os
import json
from pathlib import Path
class FolderSync(object):
	def __init__(self):
		self.mapping_table = {
			"PLpr1zUR-_qIN4v4o529V31XLzYwc8PYqr":
				["/Video/文昭思绪飞扬",
				"/OneDrive/Stream/文昭思绪飞扬"],
			"UUQ58rNgEE1Vt3G40E_NWAsA":
				["/Video/每日一本书"],
			"UUUlG55IHoeSWr7xbbYUOdwQ":
				["/Video/miniFish"],
			"UUtAIPjABiQD3qjlEl1T5VpA":
				["/Video/文昭谈古论今"],

				
		}
		#message sending destination server
		self._host = socket.gethostbyname("qinbatista.com")
		self._port = 10005
		self.crt = './mycert.crt'#os.path.abspath(os.path.join(os.path.dirname(__file__), '../tcp_download_system'))+'/ssl_cert/mycert.crt'
		self._thread_send_message()

	def _thread_send_message(self):
		thread1 = threading.Thread(target=self._loop_message, name="t1",args=())
		thread1.start()

	def _loop_message(self):
		while True:
			for key in self.mapping_table.keys():
				link = "https://www.youtube.com/playlist?list="+key+""
				result = asyncio.run(self.send_message('{"message":"'+link+'","type":"sync_youtube","proxy":""}'))
				time.sleep(5)
			time.sleep(60)

	async def send_message(self, message: str) -> dict:
		try:
			context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
			context.load_verify_locations(self.crt)
			context.check_hostname = False
			reader, writer = await asyncio.open_connection(self._host, self._port, ssl=context)
			writer.write((message + '\r\n').encode())
			await writer.drain()
			raw = await reader.readuntil(b'\r\n')
			resp = raw.decode().strip()
			writer.close()
			await writer.wait_closed()
			return resp
		except Exception as e:
			print(e)

	def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
		return {"status": status, "message": message, "data": data}

	async def get_video_list(self, list_id):
		Path(self.mapping_table[list_id][0]).mkdir(parents=True, exist_ok=True)
		if list_id in self.mapping_table:
			video_list = os.listdir(self.mapping_table[list_id][0])
		else:
			video_list = []
		# print("self.mapping_table="+str(self.mapping_table[list_id]))
		result = {"video_list":video_list,"folder_list":self.mapping_table[list_id]}
		return self._message_typesetting(200, "all video codes", result)


ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
	kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
	kwargs['content_type'] = 'text/json'
	return web.Response(**kwargs)

@ROUTES.get('/get_video_list')
async def healthcheck(request: web.Request) -> web.Response:
	query = request.query
	print("query=" + str(query))
	result = await (request.app['MANAGER']).get_video_list(query['list_id'])
	return _json_response(result)

def run():
	print("FolderSync version:1.1")
	app = web.Application()
	app.add_routes(ROUTES)
	app['MANAGER'] = FolderSync()
	web.run_app(app, port="10015")


if __name__ == "__main__":
	run()

