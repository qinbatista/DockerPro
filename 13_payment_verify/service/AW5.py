from urllib.parse import urlencode
from config.PaymentConfig import GAMES, AW5 as aw5
from config.PaymentConfig import PaymentType
from data.model.Order import Order
from service.CommonService import CommonService
from utils.MD5 import MD5
from utils.Response import Response
import traceback
import json

class AW5(CommonService):
    def __init__(self):
        super(AW5, self).__init__()

    async def process(self, request, game_name):
        result = aw5.FAILURE_RESPONSE
        try:
            params = dict(await request.post())
            if params:
                params['game_name'] = game_name
                verify_sign_result = await self.verify_notify_sign(params)
                if not verify_sign_result:
                    result = await self.record_notify_result(params)
        except:
            print(traceback.format_exc())
        return Response.text_response(result)

    async def verify_notify_sign(self, params):
        game_name = params['game_name']
        key = GAMES[game_name][aw5.NAME]['APP_KEY']
        app_id = GAMES[game_name][aw5.NAME]['APP_ID']
        sign = params.pop("sign")
        data = json.loads(params.get("data", {}))
        service = params.get("service", "")
        message = app_id + service + "".join(sorted([f"{v}" for k, v in data.items()])) + key
        return MD5.verify(message, sign)

    async def record_notify_result(self, params):
        game_name = params.get("game_name", "")
        data = json.loads(params['data'])
        callback_info = json.loads(params['callbackInfo'])
        production_id = data["goodsID"]
        role_id = data['roleID']
        channel_order_id = data['orderId']
        price = data["money"]
        user_id = callback_info['device_id']
        order_id = callback_info['order_id']
        des = callback_info.get("des", "")
        is_existed_order = await self.is_existed_order(user_id, order_id)
        if is_existed_order:
            return aw5.SUCCESS_RESPONSE
        else:
            result = await Order().insert(
                game_name=game_name,
                channel=aw5.NAME,
                price=price,
                order_id=order_id,
                payment=PaymentType.AW5,
                claimed=0,
                des=des,
                production_id=production_id,
                user_id=user_id,
                role_id=role_id,
                channel_order_id=channel_order_id,
                is_sandbox=0
            )
            if result:
                return aw5.SUCCESS_RESPONSE
            return aw5.FAILURE_RESPONSE
