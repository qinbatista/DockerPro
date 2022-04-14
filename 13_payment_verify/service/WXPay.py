from config.PaymentConfig import WXPayConfig
from utils.MD5 import MD5
import xmltodict
from service.CommonService import CommonService
import traceback
from utils.Response import Response
from config.PaymentConfig import GAMES, PaymentType, WXPayConfig
from data.model.Order import Order
import time
import aiohttp
from config.PaymentConfig import OrderStatus

class WXPay(CommonService):
    def __init__(self):
        super(WXPay, self).__init__()

    async def process(self, request, game_name):
        result = WXPayConfig.FAILURE_RESPONSE
        try:
            params = await request.text()
            params = xmltodict.parse(params).get('xml')
            if params:
                #self.log.info(f"client_wxpay_success_callback={params}")
                params['game_name'] = game_name
                verify_sign_result = await self.verify_notify_sign(params)
                if not verify_sign_result:
                    result = await self.very_order_status(params)
        except:
            pass
            #self.log.error(traceback.format_exc())
        return Response.text_response(result)

    async def very_order_status(self, params):
        result = WXPayConfig.FAILURE_RESPONSE
        game_name = params['game_name']
        app_id = GAMES[game_name][WXPayConfig.NAME]["WX_APP_ID"]
        key = GAMES[game_name][WXPayConfig.NAME]['WX_API_KEY']
        order_params = dict(
            appid=app_id,
            mch_id=params.get("mch_id", ""),
            nonce_str=int(time.time()),
            transaction_id=params.get("transaction_id", "")
        )
        message = "&".join(sorted([f"{k}={v}" for k, v in order_params.items()]) + [f"key={key}"])
        order_params['sign'] = MD5.encrypt_upper(message)
        order_params = '<xml>\n{0}\n</xml>'.format("\n".join(["<{0}>{1}</{2}>".format(key, order_params[key], key)
                                                              for key in order_params]))
        async with aiohttp.request('POST', WXPayConfig.ORDER_URL, data=order_params) as resp:
            order_status_result = await resp.text(encoding='utf-8')
            order_status_result = xmltodict.parse(order_status_result)['xml']
            #self.log.info(order_status_result)
            if order_status_result.get("trade_state", "") == WXPayConfig.TRADE_STATUS.SUCCESS:
                result = await self.record_notify_result(params)
        return result

    async def verify_notify_sign(self, params):
        game_name = params['game_name']
        key = GAMES[game_name][WXPayConfig.NAME]['WX_API_KEY']
        sign = params.pop("sign")
        message = "&".join(sorted([f"{k}={v}" for k, v in params.items()]) + [f"key={key}"])
        return MD5.verify(message, sign, is_upper=True)

    async def record_notify_result(self, params):
        order_id = params.get("out_trade_no")
        attach = params.get("attach", "")
        attach = attach.split(",")
        des = attach[0]
        user_id = attach[1]
        channel = attach[2]
        is_existed_order = await self.is_existed_order(user_id,order_id)
        if is_existed_order:
            #self.log.info(f"existed_order:{order_id}")
            return WXPayConfig.SUCCESS_RESPONSE
        else:
            result = await Order().insert(
                game_name=params.get("game_name", ""),
                channel=channel,
                price=int(params.get("total_fee", 0))/100,
                order_id=order_id,
                payment=PaymentType.WXPay,
                claimed=OrderStatus.UNDELIVERED,
                des=des,
                role_id="",
                channel_order_id=params.get("transaction_id", ""),
                production_id="com.test.pid",
                user_id=user_id
            )
            if result:
                return WXPayConfig.SUCCESS_RESPONSE
            return WXPayConfig.FAILURE_RESPONSE
