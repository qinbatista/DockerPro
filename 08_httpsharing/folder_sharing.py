import os
import random
import time
class FtpManager:
	def __init__(self):
		self.__reedem_codes_file = 'redeem'
		self.__download_folder = "/root/download_folder/"#"/Users/batista/Desktop/" #/root/download_folder/
		self.__readme = "README.txt" #~/download_folder/
		self.__port = 10008
		self.__access_URL = "http://office.singmaan.com:"+str(self.__port) #~/download_folder/
		self.folder_name = self.__list_folder(self.__download_folder)

	def	__list_folder(self, _path):
		List = []
		for i in os.listdir(_path):
			if i.find(".DS_Store")!=-1 or i.find(".")!=-1:
				continue
			List.append(i)
		return List

	def generate_verification_code(self):
		''' 随机生成6位的验证码 '''
		code_list = []
		for i in range(10): # 0-9数字
			code_list.append(str(i))
		for i in range(65, 91): # A-Z
			code_list.append(chr(i))
		for i in range(97, 123): # a-z
			code_list.append(chr(i))
		myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
		verification_code = ''.join(myslice) # list to string
		return verification_code

	def create_file(self,_path,_context):
		with open(_path,mode='w',encoding="utf8") as file_context:
			file_context.write(_context)

	def start_server(self):
		print("folder_name="+str(self.folder_name))
		os.chdir(self.__download_folder)
		os.system("python3 -m http.server "+str(self.__port))
		#实例化DummyAuthorizer来创建ftp用户
		# authorizer = DummyAuthorizer()
		# for my_name in self.folder_name:
		# # 参数：用户名，密码，目录，权限
		# 	my_password = self.generate_verification_code()
		# 	print(f"URL:		{self.__access_URL}\nPathName:	{self.__download_folder+my_name}\nUserName:	{my_name}\nPassword:	{my_password}\n")
		# 	self.create_file(self.__download_folder+"/"+my_name+"/"+self.__readme, f"URL:		{self.__access_URL}\nPathName:	{self.__download_folder+my_name}\nUserName:	{my_name}\nPassword:	{my_password}\n")
		# 	print("my_name="+my_name)
		# 	print("my_password="+my_password)
		# 	print("self.__download_folder+my_name="+self.__download_folder+my_name)
		# 	authorizer.add_user(my_name, my_password, self.__download_folder+my_name, perm='elradfmwMT')
		# # 匿名登录
		# # authorizer.add_anonymous('/home/nobody')
		# handler = FTPHandler
		# handler.authorizer = authorizer
		# # 参数：IP，端口，handler
		# server = FTPServer(('', self.__port), handler)
		# server.serve_forever()

	def detecting(self):
		while True:
			detecting_folder = self.__list_folder(self.__download_folder)
			if len(detecting_folder)==self.folder_name:
				time.sleep(1)
			else:
				self.folder_name = detecting_folder


if __name__ == '__main__':
	print("version:2.0")
	my_ftp = FtpManager()
	my_ftp.start_server()