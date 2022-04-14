import boto3


class PaymentVerifyManager:
    def __init__(self, worlds=[]):
        self.__aws_init()

    def __aws_init(self):
        self.__dynamodb = boto3.resource('dynamodb', region_name='cn-northwest-1',
                                         aws_access_key_id='AKIAYDN4Q6OUMFA7F46S',
                                         aws_secret_access_key='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')
        self.__table = self.__dynamodb.Table('AccountSys')

    def __aws_download(self, unique_id, game_name):
        message = self.__table.get_item(Key={"unique_id": unique_id, "game_name": game_name})
        return message["Item"]["game_data"]

    def __aws_account_query(self, account, password):
        resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
        id_account = len(resp["Items"])
        if id_account == 0:
            print("creating a new account:" + str(id_account))
            self.__aws_account_create(account, password)
            return False, resp["Items"]
        if id_account == 1:
            print("verify a old account:" + str(id_account))
            return True, resp["Items"]

    def __aws_account_query_only(self, account, password):
        resp = self.__table.query(KeyConditionExpression=Key('account').eq(account))
        id_account = len(resp["Items"])
        if id_account == 0:
            print("don't have such account:" + str(id_account))
            return False, resp["Items"]
        if id_account == 1:
            print("verify a old account:" + str(id_account))
            return True, resp["Items"]

    def __aws_account_create(self, account, password):
        resp = self.__table.update_item(
            Key={"account": account}, ExpressionAttributeNames={"#password": "password", },
            ExpressionAttributeValues={":password": password, },
            UpdateExpression="SET #password = :password",
        )
        return str(resp)

    def __create_token(self):
        pass

    def _message_typesetting(self, status: int, message: str, data: dict = {}) -> dict:
        return {"status": status, "message": message, "data": data}

    async def signeinwithpassword(self, account, password):
        query_result, context = self.__aws_account_query(account, password)
        print("context=" + str(context))
        if query_result == True:
            if context[0]['password'] == password:
                return self._message_typesetting(200, "login success, verified passed",
                                                 {"result": {"query_result": query_result}})
            else:
                return self._message_typesetting(-200, "login failed,password failed",
                                                 {"result": {"query_result": query_result}})
        else:
            return self._message_typesetting(201, "login success, created a new account",
                                             {"result": {"query_result": query_result}})

    async def loginwithpassword(self, account, password):
        query_result, context = self.__aws_account_query_only(account, password)
        print("context=" + str(context))
        if query_result == True:
            if context[0]['password'] == password:
                return self._message_typesetting(200, "login success, verified passed", {
                    "result": {"chineseid": context[0]['chineseid'] if "chineseid" in context[0] else ""}})
            else:
                return self._message_typesetting(-200, "login failed,password failed", {"result": {"chineseid": ""}})
        else:
            return self._message_typesetting(-201, "login failed, account don't exist", {"result": {"chineseid": ""}})

    async def updatechineseid(self, account, chineseid):
        resp = self.__table.update_item(
            Key={"account": account}, ExpressionAttributeNames={"#chineseid": "chineseid", },
            ExpressionAttributeValues={":chineseid": chineseid, },
            UpdateExpression="SET #chineseid = :chineseid",
        )
        print(str(resp))
        # print("context="+str(context))
        # if query_result==True:
        # 	if context[0]['password']==password:
        # 		return self._message_typesetting(200,"login success, verified passed",{"result":{"query_result":query_result}})
        # 	else:
        # 		return self._message_typesetting(-200,"login failed,password failed",{"result":{"query_result":query_result}})
        # else:
        return self._message_typesetting(200, "login success, created a new account",
                                         {"result": {"query_result": str(resp)}})

    async def server_success_callback(self, *args, **kargs):
        return self._message_typesetting(200, "server callback success", {"result": {}})

    async def client_success_callback(self, *args, **kargs):
        return self._message_typesetting(200, "client callback success", {"result": {}})

    async def downloadgamedata(self, game_name, unique_id):
        return self._message_typesetting(200, "download data success",
                                         {"result": self.__aws_download(game_name, unique_id)})
