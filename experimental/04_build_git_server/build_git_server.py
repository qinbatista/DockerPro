#!/usr/bin/env python
import sys, os, platform
def get_desktop():
	return os.path.join(os.path.expanduser("~"), 'Desktop')
def PythonLocation():
	return os.path.dirname(os.path.realpath(__file__))

def change_shall_premssion(name):
	'''
	only git can shall to this user
	'''
	new_content = []
	with open("/etc/passwd",mode='r',encoding="utf8") as file:
		content =  file.readlines()
		for raw in content:
			if raw.find(name)!=-1:new_content.append(raw[:raw.rfind(":")]+":/usr/bin/git-shell")
			else:new_content.append(raw)
	with open("/etc/passwd",mode='w',encoding="utf8") as file:
		file.writelines(new_content)


def create_user():
	name = input("user name:")
	os.system("adduser "+name)
	change_shall_premssion(name)

def list_user():
	'''
	nevigate to /home for finding all users
	'''
	file_name_lists = os.listdir('/home')
	for index, name in enumerate(file_name_lists):
		print(f'[{index}]\t{name}')
	return file_name_lists[int(input('input your choice(integer only):'))]

def add_ssh_to_user(name, key):
	if os.path.exists("/home/" + name + "/.ssh/")==False:os.system("mkdir "+"/home/" + name + "/.ssh/")
	if os.path.exists("/home/" + name + "/.ssh/")==False:os.system("touch authorized_keys")
	os.system('chmod 700 ~/.ssh/')
	os.system('chmod 600 ~/.ssh/*')
	with open("/home/" + name + "/.ssh/authorized_keys", mode='a', encoding="utf8") as file:
		file.writelines(key+"\n")
	print(f'/home/{name}/.ssh/authorized_keys added:{key}')

def add_ssh_to_all_user(key):
	name_list = os.listdir('/home')
	for name in name_list:
		if os.path.exists("/home/" + name + "/.ssh/")==False:os.system("mkdir "+"/home/" + name + "/.ssh/")
		if os.path.exists("/home/" + name + "/.ssh/")==False:os.system("touch authorized_keys")
		os.system('chmod 700 ~/.ssh/')
		os.system('chmod 600 ~/.ssh/*')
		with open("/home/" + name + "/.ssh/authorized_keys", mode='a', encoding="utf8") as file:
			file.writelines(key+"\n")
		print(f'/home/{name}/.ssh/authorized_keys added:{key}')

def create_git_repositories(repositories):
	name = list_user()
	if os.path.exists("/home/" + name + "/.ssh/")==False:os.system('mkdir /Repositories/'+ name)
	os.system('git init --bare '+'/Repositories/'+name+'/'+repositories+'.git')
	os.system('chown -R '+name+":"+name+' /Repositories/'+ name)
	os.system('chown -R '+name+":"+name+' /Repositories/'+ name+'/'+repositories+".git")
	os.system('chmod 700 /Repositories/'+ name+"/")
	print(f'[success]\tgit clone ssh://{name}@office.singmaan.com:10022/Repositories/{name}/{repositories}.git')

def show_all_repositories():
	print("------------------------")
	file_name_lists = os.listdir('/Repositories')
	for index, name in enumerate(file_name_lists):
		if name.rfind("#recycle")!=-1 or name.rfind("@eaDir")!=-1:
			continue
		print(f'-{name}')
		repositories_list  = os.listdir('/Repositories/'+name)
		for index, repos_name in enumerate(repositories_list):
			if repos_name.rfind(".git")==-1:
				continue
			print(f'	[{repos_name}]\t')
			print(f'	git clone ssh://{name}@office.singmaan.com:10022/Repositories/{name}/{repos_name}')
			print(f'	\t')
	print("------------------------")



def main():
	while True:
		print("[1]\tCreate user")
		print("[2]\tAdd ssh key to user")
		print("[3]\tCreate a repositories")
		print("[4]\tShow all repositories info")
		print("[5]\tAdd ssh key to all users")
		choice = input('Input your choice:')
		if choice == '1':
			create_user()
		elif choice == '2':
			add_ssh_to_user(list_user(),input('Input your ssh public key:'))
		elif choice =='3':
			create_git_repositories(input('Input repositories name:'))
		elif choice == '4':
			show_all_repositories()
		elif choice == '5':
			add_ssh_to_all_user(input('Input your ssh public key:'))


if __name__ == '__main__':
	main()