from config.ServiceConfig import AES_KEY
from data.model.Base import Base
from data.db import fetchone,insert,execute
from data.model.Game import Game

class User(Base):
    table_name = "user"
    coloum = {
        "username": "",
        "password": "",
        "device_id": "",
        "is_authenticate": "",
        "identity_id": None,
        "mobile": None,
        "email": None,
        "game_name": None,
        "signup_ip": "",
        "last_login_time": "",
    }

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def is_existed(self, **kwargs):
        return self.select_one(**kwargs)

    async def login(self, username, password):
        sql = f"select count(1) from `{self.table_name}` where `username`= '{username}'" + \
              "and `password` = HEX(AES_ENCRYPT('{}', '{}'))".format(password, AES_KEY)
        result = await fetchone(sql)
        if result:
            return result["count(1)"]
        return 0

    async def signup(self,**kwargs):
        self.coloum.update(**kwargs)
        _ = [self.coloum.pop(key) for key in list(self.coloum.keys()) if not self.coloum[key]]
        for key in self.coloum.keys():
            if key == "password":
                self.coloum[key] = "HEX(AES_ENCRYPT('{}','{}'))".format(self.coloum[key], AES_KEY)
            else:
                self.coloum[key] = "'{}'".format(self.coloum[key])
        sql = f"insert into `{self.table_name}` ({','.join(['`{0}`'.format(coloum) for coloum in self.coloum.keys()])}) " \
            f"values ({','.join(['{' + f'{coloum}' + '}' for coloum in self.coloum.keys()])})".format(**self.coloum)
        result = await insert(sql=sql)
        return result

    async def last_user_by_device_id(self,**kwargs):
        self.coloum.update(**kwargs)
        device_id = kwargs['device_id']
        sql = f"select {','.join(['`{0}`'.format(coloum) for coloum in self.coloum.keys()])} from `{self.table_name}`" \
            f"where `device_id`='{device_id}' order by `last_login_time` desc limit 1"
        result = await fetchone(sql)
        return result

    async def update_last_login_time(self, **kwargs):
        last_login_time =  kwargs['last_login_time']
        user_name = kwargs['username']
        password = kwargs['password']
        sql = f"update `user` set `last_login_time`='{last_login_time}' where `username`='{user_name}' and `password`=HEX(AES_ENCRYPT('{password}','{AES_KEY}'))"
        result = await execute(sql)
        return result
