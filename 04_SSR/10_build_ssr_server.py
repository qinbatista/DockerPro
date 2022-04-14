import sys, os, platform
def get_desktop():
	return os.path.join(os.path.expanduser("~"), 'Desktop')
def PythonLocation():
	return os.path.dirname(os.path.realpath(__file__))
def main():
	os.system("chmod 777 ssr-install.sh")
	os.system("/ssr-install.sh")
	os.system("cp /ssr.json /etc/ssr.json")
	os.system("python3 /usr/local/ssr/shadowsocks/server.py -c /etc/ssr.json")
if __name__ == '__main__':
    main()