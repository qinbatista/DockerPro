import base64
import json
import traceback
from config.PaymentConfig import GAMES, DefaultTest as DefaultTestConfig
from config.PaymentConfig import PaymentType
from data.model.Order import Order
from service.CommonService import CommonService
from utils.MD5 import MD5
from utils.Response import Response


class DefaultTest(CommonService):
    def __init__(self):
        super(DefaultTest, self).__init__()

    async def process(self, request, game_name):
        result = {"Code": DefaultTestConfig.FAILURE_STATUS_CODE, "Msg": DefaultTestConfig.FAILURE_RESPONSE}
        try:
            params = dict(request.query)
            if params:
                params['game_name'] = game_name
                verify_sign_result = await self.verify_notify_sign(params)
                if verify_sign_result:
                    result = await self.record_notify_result(params)
        except:
            print(traceback.format_exc())
        return Response.json_response(result)

    #通知道具发放业务
    async def notice(self, request, game_name):
        result = {"Code": DefaultTestConfig.FAILURE_STATUS_CODE, "Msg": DefaultTestConfig.FAILURE_RESPONSE}
        try:
            params = dict(await request.post())
            if params:
                params['game_name'] = game_name
                verify_sign_result = await self.verify_notify_sign(params)
                if verify_sign_result:
                    result = await self.on_notice(params)
        except:
            print(traceback.format_exc())
        return Response.json_response(result)

    #通知道具发放到游戏服
    async def on_notice(self, params):
        game_name = params.get("game_name", "")
        data = json.loads(base64.b64decode(params['Data']).decode("utf-8"))
        return {"Code": DefaultTestConfig.SUCCESS_STATUS_CODE, "Msg": DefaultTestConfig.SUCCESS_RESPONSE}

    async def verify_notify_sign(self, params):
        game_name = params['game_name']
        app_secret = GAMES[game_name][DefaultTestConfig.NAME]['APP_SECRET']
        sign = params.pop("Sign")
        data = params.get("Data", {})
        message = "&".join([data, app_secret])
        return MD5.verify(message, sign)

    async def record_notify_result(self, params):
        game_name = params.get("game_name", "")
        data = json.loads(base64.b64decode(params['Data']).decode("utf-8"))
        production_id = data["ProductId"]
        role_id = data['RoleId']
        channel_order_id = data['OrderId']
        price = float(data["Amount"]/100)
        user_id = data['UserId']
        order_id = data['AppOrderId']
        des = data.get("des", "")
        is_existed_order = await self.is_existed_order(user_id, order_id)
        if is_existed_order:
            return {"Code": DefaultTestConfig.SUCCESS_STATUS_CODE, "Msg": DefaultTestConfig.SUCCESS_RESPONSE}
        else:
            result = await Order().insert(
                game_name=game_name,
                channel=DefaultTestConfig.NAME,
                price=price,
                order_id=order_id,
                payment=PaymentType.DefaultTest,
                claimed=1,
                des=des,
                production_id=production_id,
                user_id=user_id,
                role_id=role_id,
                channel_order_id=channel_order_id
            )
            if result:
                return {"Code": DefaultTestConfig.SUCCESS_STATUS_CODE, "Msg": DefaultTestConfig.SUCCESS_RESPONSE}
            return {"Code": DefaultTestConfig.FAILURE_STATUS_CODE, "Msg": DefaultTestConfig.FAILURE_RESPONSE}
