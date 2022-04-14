import sys, os
import threading
import time
import uuid
import requests

def main():
    while True:
        post_ip_address()
        time.sleep(600)

def get_host_ip():
    return requests.get('https://checkip.amazonaws.com').text.strip()

def post_ip_address():
    requests.post("https://0CZAMRlonw60PWyg:77JKaTvVEfjbqOjA@domains.google.com/nic/update?hostname=us.qinyupeng.com&myip="+get_host_ip())

def get_mac_address(): 
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

if __name__ == '__main__':
    main()