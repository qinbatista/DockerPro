import json
import os
import random
import shutil
import threading
import time
from datetime import datetime
from datetime import timedelta

import aiomysql
from aiohttp import web
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

config = {
    "app_key": "53UwrmzD1q5GMlu0"
}


class GameManager:
    def __init__(self, worlds=[]):
        self.__reedem_codes_file = 'redeem'
        self.__root_OperationLives = '/root/redeemsystem'  # '/Users/batista/Desktop'#'/root/redeemsystem'
        self.__game_list = '/root/operationlives'  # '/Users/batista/SingmaanProject/OperationLives'#'/root/OperationLives'
        self.__git_list = '/root'
        self.__rep_link = 'https://qinbatista:qinyupeng1@bitbucket.org/qinbatista/operationlives.git'
        self.__scheduler = BlockingScheduler()
        self.__game_names = []
        self.__max_redeems = 700
        self.__item_quantity = 100
        self.__refresh_time = 60 * 60 * 24 * 30
        self.__redeem_codes = dict()
        self.__redeem_codes_list = []
        self.__used_redeem_codes = []
        self.__all_redeem_codes = {}
        self.__count = 0
        self.__expire_time = ""
        self.__reedem_code_version = 0
        self.__created_all_redeems = False
        self.__config_file_name = 'config.json'
        self.__used_redeem_codes_file_name = f"{self.__root_OperationLives}/redeemed_list.json"
        self._set_all_config()

    async def _connect_sql(self):
        self._pool = await aiomysql.create_pool(
            maxsize=20,
            host='192.168.1.102',
            user='root',
            password='lukseun',
            charset='utf8',
            autocommit=True)

    async def _execute_statement(self, database_name: int, statement: str) -> tuple:
        """
        Executes the given statement and returns the result.
        执行给定的语句并返回结果。
        :param statement: Mysql执行的语句
        :return: 返回执行后的二维元组表
        使用例子：data = await self._execute_statement(world, 'SELECT ' + material + ' FROM player WHERE unique_id="' + str(unique_id) + '";')
        """
        if self._pool is None: await self._connect_sql()
        async with self._pool.acquire() as conn:
            await conn.select_db(database_name)
            async with conn.cursor() as cursor:
                await cursor.execute(statement)
                return await cursor.fetchall()

    async def _execute_statement_update(self, database_name: int, statement: str) -> int:
        """
        Execute the update or set statement and return the result.
        执行update或set语句并返回结果。
        :param statement: Mysql执行的语句
        :return: 返回update或者是set执行的结果
        使用例子：return await self._execute_statement_update(world, f"UPDATE player SET {material}={value} where unique_id='{unique_id}'")
        """
        if self._pool is None: await self._connect_sql()
        async with self._pool.acquire() as conn:
            await conn.select_db(database_name)
            async with conn.cursor() as cursor:
                return await cursor.execute(statement)

    def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
        return {"status": status, "message": message, "data": data}

    def generate_verification_code(self):
        ''' 随机生成6位的验证码 '''
        code_list = []
        for i in range(10):  # 0-9数字
            code_list.append(str(i))
        for i in range(65, 91):  # A-Z
            code_list.append(chr(i))
        for i in range(97, 123):  # a-z
            code_list.append(chr(i))
        myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
        verification_code = ''.join(myslice)  # list to string
        return verification_code

    def _set_all_config(self):
        thread1 = threading.Thread(target=self._config_update)
        thread1.start()

    def _config_git(self):
        print("start reading config")
        os.system("pwd")
        # 如果不存在git库的文件则clone
        if not os.path.exists(self.__game_list):
            os.chdir(self.__git_list)
            os.system("git clone " + self.__rep_link)
            print("cloned repositoriy")
        else:
            os.chdir(self.__game_list)
            msg = subprocess.check_output('git pull', shell=True).decode()
            print(msg)
            if "conflicts" in msg:
                os.chdir(self.__git_list)
                os.rmdir(self.__game_list)
                os.system("git clone " + self.__rep_link)
            os.system("pwd")
            print("updated repositoriy")

    def current_count(self):
        config_file = f"{self.__root_OperationLives}/{self.__config_file_name}"
        if os.path.isfile(config_file):
            with open(config_file, mode='r', encoding="utf8") as file_context:
                read_text = file_context.readline()
                json_text = json.loads(read_text)
                start_time = json_text["start_time"]
                self.__created_all_redeems = json_text.get('created_all_redeems', False)
                record_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
                used_time = (current_time - record_time).total_seconds()
                self.__count = self.__refresh_time - used_time
        return self.__count

    def update_redeem_codes(self):
        folder_list = os.listdir(self.__root_OperationLives)
        for file_name in folder_list:
            print("file_name=" + file_name)
            if file_name.find("redeem_") != -1:
                game_name = file_name[file_name.find("_") + 1:file_name.rfind("_")]
                with open(f"{self.__root_OperationLives}/{file_name}", mode='r', encoding="utf8") as file_context:
                    self.__game_names.append(game_name)
                    game_redeem_codes = json.loads(file_context.read())
                    self.__all_redeem_codes[game_name] = game_redeem_codes
        self.__game_names = list(set(self.__game_names))
        self.update_redeem_used_code()

    def update_redeem_used_code(self):
        # read used redeem codes
        if os.path.isfile(self.__used_redeem_codes_file_name):
            with open(self.__used_redeem_codes_file_name, mode='r',
                      encoding="utf8") as file_context:
                self.__used_redeem_codes = file_context.readlines()
        print("read_redeem_text=" + str(self.__used_redeem_codes))
        for text_line in self.__used_redeem_codes:
            split_result = text_line.split(":")
            self.__all_redeem_codes[split_result[0]][split_result[1].replace("\n", "")] = -1

    # 将git 拉取下的兑换码文件放入兑换码目录
    def change_redeem_file(self):
        _ = [os.remove(file) for file in os.listdir(self.__root_OperationLives) if os.path.exists(f"file")]
        for home, dirs, files in os.walk(self.__game_list):
            for file_name in files:
                if file_name.startswith("redeem"):
                    game_name = file_name[file_name.find("_") + 1:file_name.rfind("_")]
                    abs_file_name = f"{self.__game_list}/{game_name}/{file_name}"
                    if os.path.exists(abs_file_name):
                        # 直接文件覆盖到兑换码目录
                        shutil.copyfile(abs_file_name, f"{self.__root_OperationLives}/{file_name}")

    def is_already_download_redeem_file(self):
        for file_name in os.listdir(self.__root_OperationLives):
            if file_name.startswith("redeem"):
                return True
        return False

    # 每次启动前拉去最新的兑换码文件
    def _config_update(self):
        self._config_git()
        # 将兑换码文件转移到指定目录
        self.change_redeem_file()
        # 更新兑换码
        self.update_redeem_codes()

        # 非第一次刷新则等待上次剩余时间后刷新
        if self.current_count() > 0:
            #此处从config中取出得到，如果为false则为，生成兑换码提交，写入新的刷新时间时服务中断，需要在刷新一次
            if self.__created_all_redeems:
                self.__refresh_all_redeem(is_manual=True)
            print(f"非第一次刷新,需要等待{self.__count}秒")
            self.get_expire_time()
            while self.__count >= 0:
                self.__count -= 1
                time.sleep(1)
            self.__refresh_all_redeem()
        else:
            #第一次运行服务，且兑换码目录上已经有了兑换码文件则不做刷新
            if not self.is_already_download_redeem_file():
                self.__refresh_all_redeem()
            else:
                self.get_expire_time()
                # 第一次运行服务，且兑换码目录上已经有了兑换码文件则不做刷新,但是兑换码生成flag为true
                self.__created_all_redeems = True

        # 定时执行刷新，每次刷新之后的兑换码文件，必会push到git库上
        self.__scheduler.add_job(
            self.__refresh_all_redeem, 'interval', seconds=self.__refresh_time
        )
        print("定时器开始等待下一次刷新")
        self.__scheduler.start()

    def generate_redeem_code(self):
        group = []
        result = dict()
        self.__redeem_codes_list = sorted(set(
            [self.generate_verification_code() for i in range(0, self.__max_redeems * self.__item_quantity)]
        ))
        for i in range(0, len(self.__redeem_codes_list), self.__max_redeems):
            group.append(self.__redeem_codes_list[i:i + self.__max_redeems])
        for i, v in enumerate(group):
            for code in v:
                result[code] = str(i)
        return result

    def save_redeem_code(self, game_name, code):
        file_name = f"{self.__root_OperationLives}/{self.__reedem_codes_file}_{game_name}_V{self.__reedem_code_version}.json"
        if os.path.isfile(file_name):
            os.remove(file_name)
        with open(file_name, mode='w', encoding="utf8") as file_context:
            all_codes_string = json.dumps(code)
            file_context.write(all_codes_string)
        git_file = f"{self.__game_list}/{game_name}/{self.__reedem_codes_file}_{game_name}_V{self.__reedem_code_version}.json"
        shutil.copyfile(file_name, git_file)

    def get_expire_time(self):
        now = datetime.now()
        if self.__count <= 0:
            delta = timedelta(seconds=self.__refresh_time)
        else:
            delta = timedelta(seconds=self.__count)
        self.__expire_time = (now + delta).strftime('%Y-%m-%d %H:%M:%S')

    def git_push(self):
        print(os.chdir(self.__game_list))
        print(os.system("git config --global user.email \"docker@singmaan.com\""))
        print(os.system("git config --global user.name \"docker\""))
        print(os.system("git status"))
        print(os.system("git add ."))
        print(os.system("git commit -m 'add redeemcode files'"))
        print(os.system("git push"))

    def __refresh_all_redeem(self, is_manual=False):
        print("__refresh_all_redeem")
        if not is_manual:
            self.get_expire_time()
        self._config_git()
        config_dic = {}
        self.__created_all_redeems = False
        self.__reedem_code_version = 1
        self.__game_names = []
        self.__redeem_codes = dict()
        self.__redeem_codes_list = []
        self.__all_redeem_codes = {}
        self.__used_redeem_codes = []
        # delete used redeem codes
        if os.path.isfile(self.__used_redeem_codes_file_name):
            os.remove(self.__used_redeem_codes_file_name)
        for game_name in os.listdir(self.__game_list):
            if game_name.rfind("") != -1 and game_name.rfind(".") != -1:
                continue
            self.__game_names.append(game_name)
            self.save_redeem_code(game_name, self.generate_redeem_code())
        with open(f"{self.__root_OperationLives}/{self.__config_file_name}", mode='w', encoding="utf8") as file_context:
            config_dic["start_time"] = str(datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S'))
            config_dic["created_all_redeems"] = True
            all_codes_string = json.dumps(config_dic)
            file_context.write(all_codes_string)
        self.__created_all_redeems = True
        self.__count = self.__refresh_time
        self.git_push()
        # 每次刷新之后更新兑换码
        self.update_redeem_codes()

    def __merge_dic(self, x, y):
        z = x.copy()
        z.update(y)
        return z

    async def get_redeemcodes(self, game_name):
        return self.__all_redeem_codes.get(game_name, {})

    async def get_games(self):
        return self.__game_names

    def __refresh_new_codes(self):
        self._config_git()
        count_new_game = 0
        self.__created_all_redeems = False
        folder_list = os.listdir(self.__game_list)
        for game_name in folder_list:
            if game_name.rfind("") != -1 and game_name.rfind(".") != -1:
                continue
            if game_name not in self.__game_names:
                count_new_game = count_new_game + 1
                self.save_redeem_code(game_name, self.generate_redeem_code())
                self.__game_names.append(game_name)
                print("added new game:" + game_name)
        self.git_push()
        self.update_redeem_codes()
        self.__created_all_redeems = True

    async def redeem(self, game_name: str, redeem_code: str):
        if game_name not in self.__game_names:
            return self._message_typesetting(400, "error", {"status": "200", "message": "don't have such name"})
        if redeem_code not in self.__all_redeem_codes[game_name]:
            return self._message_typesetting(401, "error", {"status": "200", "message": "don't have such redeem codes"})
        result = self.__all_redeem_codes[game_name][redeem_code]
        if result != -1:
            self.__all_redeem_codes[game_name][redeem_code] = -1
            self.__used_redeem_codes.append(game_name + ":" + redeem_code)
            with open(self.__used_redeem_codes_file_name, mode='a',
                        encoding="utf8") as file_context:
                file_context.write(game_name + ":" + redeem_code + "\r")
            return self._message_typesetting(200, "redeem success", {"result": result})
        else:
            return self._message_typesetting(201, "redeem codes had been used", {"result": result})

    async def expiretime(self):
        expire_time = datetime.strptime(self.__expire_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
        s = (expire_time - current_time).total_seconds()
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return self._message_typesetting(200, "redeem success",{"time": "%02ddays:%02dhours:%02dminutes:%02dseconds" % (d, h, m, s)})

    async def refreshnewgame(self, gamename):
        if self.__created_all_redeems == False:
            return self._message_typesetting(-200, "error", {"status": "-200", "message": "redeem codes is creating"})
        else:
            os.chdir(self.__game_list)
            if not os.path.exists(f"{self.__game_list}/{gamename}"):
                os.mkdir(gamename)
            thread1 = threading.Thread(target=self.__refresh_new_codes)
            thread1.start()
            folder_list = os.listdir(self.__game_list)
            count_new_game = 0
            for game_name in folder_list:
                if game_name.rfind("") != -1 and game_name.rfind(".") != -1:
                    continue
                if game_name not in self.__game_names:
                    count_new_game = count_new_game + 1
            return self._message_typesetting(200, "error", {"status": "200",
                                                            "message": "redeem codes creating is started:" + str(
                                                                count_new_game) + " game added"})

    async def usedredeemcodes(self):
        # card_info = await self._execute_statement(world, f'select vip_card_type from player where unique_id="{unique_id}"')
        return self._message_typesetting(200, "this is all used codes",{"status": "200", "result": str(self.__used_redeem_codes)})

    async def refreshall(self):
        try:
            thread1 = threading.Thread(target=self.__refresh_all_redeem(is_manual=True))
            thread1.start()
        except:
            return self._message_typesetting(200, "error", {"status": "500",
                                                            "message": "refresh all error"})
        return self._message_typesetting(200, "error", {"status": "200", "message": "refrsh all redeem codos success"})


ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
    kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
    kwargs['content_type'] = 'text/json'
    return web.Response(**kwargs)


# json param, get result from request post
# http://localhost:9989/redeem
@ROUTES.post('/redeem')
async def _redeem(request: web.Request) -> web.Response:
    post = await request.post()
    print("post=" + str(post))
    result = await (request.app['MANAGER']).redeem(post['gamename'], post['redeemcode'])
    return _json_response(result)


# no param, get result directly
# http://localhost:9989/expiretime
@ROUTES.get('/expiretime')
async def _expiretime(request: web.Request) -> web.Response:
    post = request.query
    result = await (request.app['MANAGER']).expiretime()
    return _json_response(result)


# no param, get result directly
# http://localhost:9989/refresh
@ROUTES.get('/refreshnewgame')
async def _refreshnewgame(request: web.Request) -> web.Response:
    post = request.query
    app_key = post.get("appkey")
    gamename = post.get("gamename")
    if app_key != config['app_key']:
        return _json_response(
            {
                "status": 200,
                "message": "error appkey",
                "data": False
            }
        )
    result = await (request.app['MANAGER']).refreshnewgame(gamename)
    return _json_response(result)

# 手工刷新
@ROUTES.post('/refreshall')
async def _refreshnewgame(request: web.Request) -> web.Response:
    query = request.query
    app_key = query['appkey']
    print("app_key="+str(app_key))
    if app_key != config['app_key']:
        return _json_response(
            {
                "status": 200,
                "message": "error appkey",
                "data": False
            }
        )
    result = await (request.app['MANAGER']).refreshall()
    return _json_response(result)


# no param, get result directly
# http://localhost:9989/usedredeemcodes
@ROUTES.get('/usedredeemcodes')
async def _usedredeemcodes(request: web.Request) -> web.Response:
    post = request.query
    result = await (request.app['MANAGER']).usedredeemcodes()
    return _json_response(result)


# no param, get result directly
# http://localhost:9989/usedredeemcodes
@ROUTES.get('/getredeemcodes')
async def getredeemcodes(request: web.Request) -> web.Response:
    post = request.query
    result = await (request.app['MANAGER']).get_redeemcodes(post['gamename'])
    return _json_response(result)


@ROUTES.get('/getgames')
async def getredeemcodes(request: web.Request) -> web.Response:
    post = request.query
    result = await (request.app['MANAGER']).get_games()
    return _json_response(result)


@ROUTES.get('/healthcheck')
async def healthcheck(request: web.Request) -> web.Response:
    return _json_response(
        {
            "status": 200,
            "message": "health",
            "data": True
        }
    )


def run():
    print("version:1.0")
    app = web.Application()
    app.add_routes(ROUTES)
    app['MANAGER'] = GameManager()
    web.run_app(app, port="8080")


if __name__ == '__main__':
    run()
