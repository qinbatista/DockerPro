import json
from utils.RSA import RSA
from service.CommonService import CommonService
from config.PaymentConfig import AliPayConfig, GAMES, PaymentType
from utils.Response import Response
import traceback
import aiohttp
from data.model.Order import Order
from utils.Time import Time
from config.PaymentConfig import OrderStatus

class AliPay(CommonService):

    def __init__(self):
        super(AliPay, self).__init__()

    async def process(self, request, game_name):
        result = AliPayConfig.FAILURE_RESPONSE
        try:
            params = dict(await request.post())
            #self.log.info(params)
            if params:
                params['game_name'] = game_name
                result = await self.very_order_status(params)
                #self.log.info(verify_order_result)
        except:
            pass
            #self.log.error(traceback.format_exc())
        return Response.text_response(result)

    async def very_order_status(self, params):
        result = AliPayConfig.FAILURE_RESPONSE
        game_name = params['game_name']
        private_key = GAMES[game_name][AliPayConfig.NAME]["PRIVATE_KEY"]
        app_id = GAMES[game_name][AliPayConfig.NAME]["APP_ID"]
        order_params = {
            "app_id": app_id,
            "method": "alipay.trade.query",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": Time.local_format_time(),
            "version": "1.0",
            "biz_content": json.dumps({
                "out_trade_no": params['out_trade_no'],
                "trade_no": params['trade_no'],
            }),
        }
        message = "&".join(sorted([f"{k}={v}" for k, v in order_params.items()]))
        order_params['sign'] = RSA.sign_with_rsa2(private_key=private_key, sign_content=message, charset="utf-8")
        async with aiohttp.request('POST', AliPayConfig.ORDER_URL, params=order_params) as resp:
            order_status_result = await resp.json(content_type='text/html', encoding='utf-8')
            #self.log.info(f"alipay order status result:{order_status_result}")
        if order_status_result.get("alipay_trade_query_response", {}).get("trade_status", "") \
                == AliPayConfig.TRADE_STATUS.TRADE_SUCCESS:
            #self.log.info(f"alipay order trade success")
            result = await self.record_notify_result(params)
        return result

    async def record_notify_result(self, params):
        order_id = params.get("out_trade_no")
        body = params.get("body", "")
        body = body.split("|")
        channel = body[0]
        des = body[1]
        user_id = body[2]
        is_existed_order = await self.is_existed_order(user_id,order_id)
        if is_existed_order:
            #self.log.info(f"existed_order:{order_id}")
            return AliPayConfig.SUCCESS_RESPONSE
        else:
            result = await Order().insert(
                game_name=params.get("game_name", ""),
                channel=channel,
                price=params.get("total_amount", 0),
                order_id=order_id,
                payment=PaymentType.AliPay,
                claimed=OrderStatus.UNDELIVERED,
                des=des,
                role_id="",
                channel_order_id=params.get("trade_no", ""),
                production_id="com.test.pid",
                user_id=user_id
            )
            if result:
                return AliPayConfig.SUCCESS_RESPONSE
            return AliPayConfig.FAILURE_RESPONSE
