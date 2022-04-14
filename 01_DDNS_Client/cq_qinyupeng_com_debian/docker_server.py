import sys, os
import socket
import threading
from time import ctime
def main():
	os.system('service ssh start')
	while True:
		new_ssh = input('input your id_rsa.pub:')
		if new_ssh.find('ssh-rsa')==-1:
			print('[Wrong key, input again]')
			continue
		os.system('echo '+new_ssh+'>>~/.ssh/authorized_keys')
		print('Add successfully')
if __name__ == '__main__':
    main()