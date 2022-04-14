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

	async def send_message(self, message: str) -> dict:
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
	commaand = sys.argv[1] if len(sys.argv)>1 else input('command')
	link = sys.argv[2] if len(sys.argv)>1 else input('link')
	print(commaand)
	print(link)
	# print(link)
	# link = "youtube-dl https://www.youtube.com/watch?v=NkdoWDl2oQc"
	result = asyncio.run(qc.send_message('{"message":"'+commaand+" "+link+'","type":"command","proxy":""}'))
	# result = asyncio.run(qc.send_message('{"message":"https://www.charlesproxy.com/assets/release/4.5.6/charles-proxy-4.5.6.dmg","type":"wget","proxy":""}'))
	# result = asyncio.run(qc.send_message('{"message":"qinbatista","type":"instagram-scraper","proxy":""}'))
	print(result)