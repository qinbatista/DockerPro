import os
import shutil

image_mapping = {
    "qinbatista/redeemsystem-07": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "07_redeemsystem"),
        "command": "docker build -t qinbatista/redeemsystem",
        "nginx_conf_file": "redeem.conf",
        "build_command": "docker run -itdv /root:/root -v /root/redeemsystem:/root/redeemsystem -p 10007:10007  qinbatista/redeemsystem",
        "push_command":"docker push qinbatista/redeemsystem"
    },
    "qinbatista/configrequest-09": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "09_config_request"),
        "command": "docker build -t qinbatista/configrequest",
        "nginx_conf_file": "config_request.conf",
        "build_command": "docker run -itdv /root/operationlives:/root/operationlives -p 10009:10009  qinbatista/configrequest",
        "push_command":"docker push qinbatista/configrequest"
    },
    "qinbatista/gamedata_backup-10": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "10_gamedata_backup"),
        "command": "docker build -t qinbatista/gamedata_backup",
        "nginx_conf_file": "gamedata_backup.conf",
        "build_command": "docker run -itd -p 10010:10010  qinbatista/gamedata_backup",
        "push_command":"docker push qinbatista/gamedata_backup"
    },
    "qinbatista/chinese_id_verify-11": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "11_chinese_id_verify"),
        "command": "docker build -t qinbatista/chinese_id_verify",
        "nginx_conf_file": "chinese_id_verify.conf",
        "build_command": "docker run -itd -p 10011:10011  qinbatista/chinese_id_verify",
        "push_command":"docker push qinbatista/chinese_id_verify"
    },
    "qinbatista/login_systeam-12": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "12_login_systeam"),
        "command": "docker build -t qinbatista/login_systeam",
        "nginx_conf_file": "login_systeam.conf",
        "build_command": "docker run -itd -p 10012:10012  qinbatista/login_systeam",
        "push_command":"docker push qinbatista/login_systeam"
    },
    "qinbatista/payment_verify-13": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "13_payment_verify"),
        "command": "docker build -t qinbatista/payment_verify",
        "nginx_conf_file": "payment_order.conf",
        "build_command": "docker run -itd -p 10013:10013 qinbatista/payment_verify",
        "push_command":"docker push qinbatista/payment_verify"
    },
    "qinbatista/user_service-14": {
        "path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "14_user_service"),
        "command": "docker build -t qinbatista/user_service",
        "nginx_conf_file": "user_service.conf",
        "build_command":"docker run -itd -p 10014:10014 qinbatista/user_service",
        "push_command":"docker push qinbatista/user_service"
    }
}


def list_domain():
    domains = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    for domain in domains:
        if str(__file__).endswith(domain):
            domains.remove(domain)
    for index, name in enumerate(domains):
        print("["+str(index)+"]"+ name)
    return domains


def choose_image():
    images = image_mapping.keys()
    for index,images_name in enumerate(list(images)):
        print("["+str(index)+"]"+list(images)[index])
    print("[99]build all images")
    my_input = input("choose a image: ")
    if int(my_input)<len(list(images)):
        choose_image = list(images)[int(my_input)]
    else:
        print("don't have option:"+my_input)

    if my_input == "99":
        for image_name in images:
            os.chdir(choose_domain_path)
            nginx_conf_file = image_mapping[image_name]['nginx_conf_file']
            shutil.copyfile(nginx_conf_file, os.path.join(image_mapping[image_name]['path'], "pro", nginx_conf_file))
            for file in os.listdir('ssl_cert'):
                shutil.copyfile(os.path.join("ssl_cert", file),
                                os.path.join(image_mapping[image_name]['path'], "pro", "ssl_cert", file))
            commandTool(image_name)
    elif choose_image not in list(images):
        print("the image not in configuration")
    else:
        nginx_conf_file = image_mapping[choose_image]['nginx_conf_file']
        shutil.copyfile(nginx_conf_file, os.path.join(image_mapping[choose_image]['path'], "pro", nginx_conf_file))
        for file in os.listdir('ssl_cert'):
            shutil.copyfile(os.path.join("ssl_cert", file),
                            os.path.join(image_mapping[choose_image]['path'], "pro", "ssl_cert", file))
        commandTool(choose_image)

def commandTool(choose_image):
    print("[command1]"+os.path.join(image_mapping[choose_image]['path']))
    os.chdir(os.path.join(image_mapping[choose_image]['path']))
    print("[command2]"+image_mapping[choose_image]['command']+"_"+docker_domain_name.replace(".","")+" .")
    os.system(image_mapping[choose_image]['command']+"_"+docker_domain_name.replace(".","")+" .")
    print("[command3]"+image_mapping[choose_image]['build_command']+"_"+docker_domain_name.replace(".",""))
    os.system(image_mapping[choose_image]['build_command']+"_"+docker_domain_name.replace(".",""))
    print("[command4]"+image_mapping[choose_image]['push_command']+"_"+docker_domain_name.replace(".",""))
    os.system(image_mapping[choose_image]['push_command']+"_"+docker_domain_name.replace(".",""))

    os.system("git stash")
    # print(f"package {choose_image} success")

def choose_domain():
    global choose_domain_path
    global docker_domain_name

    domains = list_domain()
    choose_domain = input("choose your number: ")
    docker_domain_name = domains[int(choose_domain)]

    if domains[int(choose_domain)] not in domains:
        print("the domain not in configuration")
    else:
        os.chdir(domains[int(choose_domain)])
        choose_domain_path = os.getcwd()
        choose_image()


def pack():
    # os.system("git pull")
    choose_domain()


if __name__ == '__main__':
    pack()
