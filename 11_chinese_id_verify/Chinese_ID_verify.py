import datetime
from aiohttp import web
import json
import re
from boto3.dynamodb.conditions import Key
import boto3
import os
import urllib, sys
# import urllib2
import subprocess
import aiohttp
import ssl
import time

ID_CRAD_VERIFY_URL = "https://pidysc2zx.market.alicloudapi.com/pidinfo/ysc2zx";
APP_CODE = "583d11c3eea249c5adecc5e7822d0ebb"

class ChineseIDVerifyManager(object):
    def __init__(self):
        self.is_correct_chinese_id = False
        self.is_correct_chinese_name = False
        self.__aws_init()
        self.__isReallyIDCheck=False
        self.__verifycode ="singmaan123"

    def get_birthday(self):
        if self.is_correct_chinese_id:
            """通过身份证号获取出生日期"""
            birthday = "{0}-{1}-{2}".format(self.birth_year, self.birth_month, self.birth_day)
            return birthday

    def __aws_init(self):
        self.__dynamodb = boto3.resource('dynamodb', region_name='cn-northwest-1',
                                        aws_access_key_id='AKIAYDN4Q6OUMFA7F46S',
                                        aws_secret_access_key='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')
        self.__table = self.__dynamodb.Table('AccountSys')

        self.__dynamodb_chinese_id = boto3.resource('dynamodb', region_name='cn-northwest-1',
                                                    aws_access_key_id='AKIAYDN4Q6OUMFA7F46S',
                                                    aws_secret_access_key='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')
        self.__table_chinese_id = self.__dynamodb_chinese_id.Table('ChineseID')

    def get_sex(self):
        if self.is_correct_chinese_id:
            """男生：1 女生：2"""
            num = int(self.id[16:17])
            if num % 2 == 0:
                return "f"
            else:
                return "m"

    def get_age(self):
        """通过身份证号获取年龄"""
        if self.is_correct_chinese_id:
            now = (datetime.datetime.now() + datetime.timedelta(days=1))
            year = now.year
            month = now.month
            day = now.day
            if year == self.birth_year:
                age = 18
            else:
                if self.birth_month > month or (self.birth_month == month and self.birth_day > day):
                    age = year - self.birth_year - 1
                else:
                    age = year - self.birth_year
            age = age if age > 18 or age==18 else 18
            return age
        return 18

    def veriy_id_number(self, id_number):
        if len(id_number) != 18:
            return False
        ten = ['X', 'x', 'Ⅹ']
        ID = ["10" if x in ten else x for x in id_number]  # 将罗马数字Ⅹ和字母X替换为10
        W = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        Checkcode = [1, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        sum = 0
        for i in range(17):
            sum = sum + int(ID[i]) * W[i]
        if Checkcode[sum % 11] == int(ID[17]):
            # print("veriy_id_number=True")
            return True
        else:
            # print("veriy_id_number=False")
            return False

    def veriy_chinese_name(self, chinese_name):
        test_str = re.search(r"\W", chinese_name)
        if test_str != None and "·" not in test_str.string:
            print("[chinese_name]:" + chinese_name + ",包含特色字符")
            return False
        if len(chinese_name) <= 2 and len(chinese_name) >= 6:
            print("[chinese_name]:" + chinese_name + ",非正常名字长度")
            return False
        if bool(re.search('[a-z]', chinese_name)):
            print("[chinese_name]:" + chinese_name + ",包含小写英文")
            return False
        if bool(re.search('[A-Z]', chinese_name)):
            print("[chinese_name]:" + chinese_name + ",包含大写英文")
            return False
        if re.search("\d",chinese_name):
            print("[chinese_name]:" + chinese_name + ",包含数字")
            return False
        return True

    async def _aliy_ID_verify(self, idcard, name):
        result = True
        try:
            headers = {
                "Authorization":f"APPCODE {APP_CODE}",
                "X-Ca-Nonce":str(int(time.time()))
            }
            data = dict(idcard=idcard,realname=name)
            async with aiohttp.request(
                    method='POST',
                    url=ID_CRAD_VERIFY_URL,
                    data=data,
                    headers=headers
                ) as resp:
                result = await resp.json(encoding='utf-8')
                print(f"检验结果:{result}")
                code = result.get("errcode", "")
        except:
            print("实名认证接口异常")
            return False
        if code == "00000":
            result = True
        return result


    def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
        return {"status": status, "message": message, "data": data}

    def _is_id_contained(self, chinese_id):
        resp = self.__table_chinese_id.query(KeyConditionExpression=Key('id').eq(chinese_id))
        print("resp[\"Items\"]="+str(resp["Items"]))
        id_account = len(resp["Items"])
        if id_account == 0:
            return False
        if id_account == 1:
            return True

    def _is_account_contained(self, account, chinese_id):
        resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
        result = resp["Items"]
        if result and result[0].get("chineseid",""):
            return chinese_id==result[0].get("chineseid","")
        return False

    def _is_account_contained_chineseid(self, account):
        resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
        result = resp["Items"]
        # print("result="+str(result))
        if result and result[0].get("chineseid",""):
            return result[0].get("chineseid","")
        else:
            return ""

    def _is_authenticated(self, account):
        resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
        result = resp["Items"]
        if result and result[0].get("chineseid",""):
            print("authenticated")
            return True
        print("is not authenticated")
        return False

    def _update_account_table(self, account, chinese_id):
        resp = self.__table.update_item(
            Key={"account": account}, ExpressionAttributeNames={"#chineseid": "chineseid", },
            ExpressionAttributeValues={":chineseid": chinese_id, },
            UpdateExpression="SET #chineseid = :chineseid", )

    def _update_chinese_id_table(self, chinese_id, name):
        resp = self.__table_chinese_id.update_item(
            Key={"id": chinese_id}, ExpressionAttributeNames={"#name": "name", },
            ExpressionAttributeValues={":name": name, },
            UpdateExpression="SET #name = :name", )

    async def verify_chinese_id(self, account, chinese_id, chinese_name):
        self.id = chinese_id
        self.is_correct_chinese_id = self.veriy_id_number(chinese_id)
        self.is_correct_chinese_name = self.veriy_chinese_name(chinese_name)
        if not self.is_correct_chinese_id:
            return self._message_typesetting(-209, "incorrect chinese id",{"result": "id:" + chinese_id + " is not correct."})
        if not self.is_correct_chinese_name:
            return self._message_typesetting(-208, "incorrect name",{"result": "chinese_name:" + chinese_name + " is not correct."})

        self.birth_year = int(self.id[6:10])
        self.birth_month = int(self.id[10:12])
        self.birth_day = int(self.id[12:14])
        m_chinese_id = self._is_account_contained_chineseid(account)
        # print("m_chinese_id="+str(m_chinese_id))
        is_chinese_id_in_database = self._is_id_contained(chinese_id)
        # print("is_chinese_id_in_database="+str(is_chinese_id_in_database))
        #如上身份证基本校验全部通过
        #账号已绑定身份证
        if m_chinese_id!="":
            #不用阿里验证
            if self.__isReallyIDCheck==False:
                #更新身份证
                self._update_account_table(account, chinese_id)
                return self._message_typesetting(200, "updated chinese id, new id is="+chinese_id,{"result": {"age": self.get_age(), "sex": self.get_sex()}})
            #用阿里验证
            else:
                self.birth_year = int(m_chinese_id[6:10])
                self.birth_month = int(m_chinese_id[10:12])
                self.birth_day = int(m_chinese_id[12:14])
                #身份证不在数据库
                return self._message_typesetting(200, "you already have chinese id, returned your account Chinese id",{"result": {"age": self.get_age(), "sex": self.get_sex()}})
        #该账号未绑定身份证
        else:
            #不用阿里验证
            if self.__isReallyIDCheck==False:
                self._update_chinese_id_table(chinese_id, chinese_name)
                self._update_account_table(account, chinese_id)
                return self._message_typesetting(200, "you don't have chinese id with your account, binded your account with id:"+chinese_id,{"result": {"age": self.get_age(), "sex": self.get_sex()}})
            #用阿里验证
            else:
                #身份证已在身份证列表服务器
                if is_chinese_id_in_database==True:
                    return self._message_typesetting(-202, "input id is already in database",{"result": {"age": self.get_age(), "sex": self.get_sex()}})
                #身份证未在身份证列表服务器
                else:
                    ID_verify_result = await  self._aliy_ID_verify(chinese_id, chinese_name)
                    #阿里校验通过
                    if ID_verify_result == True:
                        self._update_account_table(account, chinese_id)
                        self._update_chinese_id_table(chinese_id, chinese_name)
                        return self._message_typesetting(200, "you inputed a correct chinese id(aliy verified), updated your input id as account id",{"result": {"age": self.get_age(), "sex": self.get_sex()}})
                    #阿里校验未通过
                    else:
                        return self._message_typesetting(-207, "your input id doesn't pass verify(aliy verify)",{"result": {"age": self.get_age(), "sex": self.get_sex()}})

    async def is_authenticated(self, account):
        result = self._is_authenticated(account)
        if result:
            return self._message_typesetting(200, "authenticated", result)
        return self._message_typesetting(200, "not authenticated", result)

    async def is_online_Verify(self, verifycode):
        if verifycode==self.__verifycode:
            if self.__isReallyIDCheck==True:
                self.__isReallyIDCheck = False
            else:
                self.__isReallyIDCheck = True
            return self._message_typesetting(200, "verify code is not correct", "self.__isReallyIDCheck:"+str(self.__isReallyIDCheck))
        else:
            return self._message_typesetting(200, "verify code is not correct", "self.__isReallyIDCheck:"+str(self.__isReallyIDCheck))


    async def verify_chinese_id_only(self, chinese_id, chinese_name):
        self.id = chinese_id
        self.is_correct_chinese_id = self.veriy_id_number(chinese_id)
        self.is_correct_chinese_name = self.veriy_chinese_name(chinese_name)
        if self.is_correct_chinese_id and self.is_correct_chinese_name:
            self.birth_year = int(self.id[6:10])
            self.birth_month = int(self.id[10:12])
            self.birth_day = int(self.id[12:14])
            return self._message_typesetting(200, "correct id",
                                            {"result": {"age": self.get_age(), "sex": self.get_sex()}})
        else:
            if self.is_correct_chinese_id == False:
                return self._message_typesetting(-200, "wrong id", {"result": "id:" + id + " is not correct."})
            if self.is_correct_chinese_name == False:
                return self._message_typesetting(-201, "wrong id",
                                                {"result": "chinese_name:" + chinese_name + " is not correct."})


ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
    kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
    kwargs['content_type'] = 'text/json'
    return web.Response(**kwargs)


# json param, get result from request post
# http://localhost:10010/verify_chinese_id
@ROUTES.post('/verify_chinese_id')
async def _verify_chinese_id(request: web.Request) -> web.Response:
    post = await request.post()
    # print("post=" + str(post))
    account_id = post.get("account_id", "")
    chinese_id = post.get("chinese_id", "")
    chinese_name = post.get("chinese_name", "")
    manager = request.app['MANAGER']
    if not account_id and chinese_id and chinese_name:
        result = await manager.verify_chinese_id_only(chinese_id, chinese_name)
    if account_id and chinese_id and chinese_name:
        result = await manager.verify_chinese_id(account_id, chinese_id, chinese_name)
    if not account_id and not chinese_id and not chinese_name:
        return _json_response(
            manager._message_typesetting(
                status=400,
                message="missing parameters",
                data={}
            )
        )
    return _json_response(result)

    # json param, get result from request post
    # http://localhost:10010/verify_chinese_id_only

@ROUTES.post('/is_online_Verify')
async def _is_online_Verify(request: web.Request) -> web.Response:
    post = await request.post()
    # print("post=" + str(post))
    result = await (request.app['MANAGER']).is_online_Verify(post['verifycode'])
    return _json_response(result)

@ROUTES.get('/healthcheck')
async def healthcheck(request: web.Request) -> web.Response:
	return _json_response(
		{
			"status":200,
			"message":"health",
			"data":True
		}
	)

@ROUTES.get('/isauthenticated')
async def healthcheck(request: web.Request) -> web.Response:
    query = request.query
    print("query=" + str(query))
    result = await (request.app['MANAGER']).is_authenticated(query['account'])
    return _json_response(result)

def run():
    print("ChineseIDVerifyManager version:1.1")
    app = web.Application()
    app.add_routes(ROUTES)
    app['MANAGER'] = ChineseIDVerifyManager()
    web.run_app(app, port="8080")

if __name__ == "__main__":
    run()
