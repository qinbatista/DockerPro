import base64
import json
import traceback
import urllib
from urllib.parse import urlencode

import aiohttp

from config.PaymentConfig import GAMES, HuaWei as hw
from config.PaymentConfig import PaymentType
from data.model.Order import Order
from service.CommonService import CommonService
from utils.Response import Response


class HuaWei(CommonService):

    def __init__(self):
        super(HuaWei, self).__init__()

    async def process(self, request, game_name):
        result = hw.FAILURE_RESPONSE
        try:
            params = dict(await request.post())
            if params:
                params['game_name'] = game_name
                access_token = await self.get_access_token(params)
                if access_token:
                    params['access_token'] = access_token
                    order = await self.query_order(params)
                    if order and int(order.get('responseCode', hw.FAILURE_STATUS_CODE)) == hw.SUCCESS_STATUS_CODE:
                        params.update(json.loads(order['purchaseTokenData']))
                        result = await self.record_order(params)
        except:
            print(traceback.format_exc())
        return Response.text_response(result)

    def build_authorization(self, access_token):
        authorization = "Basic %s" % str(base64.b64encode(f"APPAT:{access_token}".encode('utf-8')), 'utf-8')
        headers = {"Authorization": authorization, "Content-Type": "application/json; charset=UTF-8"}
        return headers

    async def get_access_token(self, params):
        game_name = params['game_name']
        app_secret = GAMES[game_name][hw.NAME]['APP_SECRET']
        app_id = GAMES[game_name][hw.NAME]['APP_ID']
        body_dict = {"grant_type": "client_credentials", "client_secret": app_secret, "client_id": app_id}
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = urllib.parse.urlencode(body_dict).encode("utf-8")
        async with aiohttp.request('POST', hw.TOKEN_URL, data=data, headers=headers) as resp:
            result = await resp.json(content_type='text/html', encoding='utf-8')
            access_token = result.get('access_token', '')
        return access_token

    async def query_order(self, params):
        result = {}
        purchase_token = params['purchaseToken']
        product_id = params['productId']
        body_dict = {"purchaseToken": purchase_token, "productId": product_id}
        data = str.encode(json.dumps(body_dict))
        headers = self.build_authorization(params['access_token'])
        async with aiohttp.request('POST', hw.VERIFY_TOKEN_URL, data=data, headers=headers) as resp:
            result = await resp.json(encoding='utf-8')
        return result

    async def record_order(self, params):
        game_name = params.get("game_name", "")
        developer_payload = json.loads(params['developerPayload'])
        production_id = params["productId"]
        channel_order_id = params['orderId']
        price = float(params["price"] / 100)
        purchase_state = params['purchaseState']
        user_id = developer_payload['device_id']
        order_id = developer_payload['order_id']
        des = params["productName"]
        is_sandbox = 1 if params.get("purchaseType", 1) == 0 else 0
        is_existed_order = await self.is_existed_order(user_id, order_id)
        if is_existed_order:
            return hw.SUCCESS_RESPONSE
        else:
            if purchase_state == hw.TRADE_SUCCESS:
                result = await Order().insert(
                    game_name=game_name,
                    channel=hw.NAME,
                    price=price,
                    order_id=order_id,
                    payment=PaymentType.HuaWei,
                    claimed=1,
                    des=des,
                    production_id=production_id,
                    user_id=user_id,
                    role_id="",
                    channel_order_id=channel_order_id,
                    is_sandbox=is_sandbox
                )
                if result:
                    return hw.SUCCESS_RESPONSE
            return hw.FAILURE_RESPONSE
