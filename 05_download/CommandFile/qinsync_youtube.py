#!/usr/bin/env python
import ssl
import asyncio
import socket
import os
import sys
class QinClient:
	def __init__(self, host: str = 'qinbatista.com', port: int = 10005):
		self._host = socket.gethostbyname(host)
		self._port = port
		self.crt = '/Users/batista/Library/Mobile Documents/com~apple~CloudDocs/Documents/ssl_cert/mycert.crt'#os.path.abspath(os.path.join(os.path.dirname(__file__), '../tcp_download_system'))+'/ssl_cert/mycert.crt'

	async def send_message(self, messaqcge: str) -> dict:
		'''
		send_message() sends the given message to the server and
		returns the decoded callback response
		'''
		context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
		# 加载服务器所用证书和私钥
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
if __name__ == "__main__":
	qc = QinClient()
	link = sys.argv[1] if len(sys.argv)>1 else input('video link:')
	link = "https://www.youtube.com/playlist?list=PLpr1zUR-_qIN4v4o529V31XLzYwc8PYqr"
	#https://www.youtube.com/playlist?list=PLpr1zUR-_qIN4v4o529V31XLzYwc8PYqr
	result = asyncio.run(qc.send_message('{"message":"'+link+'","type":"sync_youtube","proxy":""}'))
	# result = asyncio.run(qc.send_message('{"message":"https://www.charlesproxy.com/assets/release/4.5.6/charles-proxy-4.5.6.dmg","type":"wget","proxy":""}'))
	# result = asyncio.run(qc.send_message('{"message":"qinbatista","type":"instagram-scraper","proxy":""}'))
	print(result)