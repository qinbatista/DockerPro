from config.PaymentConfig import OrderStatus
from data.model.Order import Order
from utils.Response import Response


class CommonService:

    def __init__(self, *args, **kargs):
        pass
        # self.log = Log().logger

    async def process(self, request, game_name):
        pass

    async def verify_notify_sign(self, params):
        pass

    async def record_notify_result(self, result):
        pass

    async def get_refunded_payment_order(self, request):
        result = []
        params = request.query
        user_id = params.get("user_id")
        game_name = params.get("game_name")
        channel = params.get("channel")
        try:
            result = await Order().select(
                user_id=user_id,
                claimed=OrderStatus.REFUNDED,
                game_name=game_name,
                channel=channel
            )
        except:
            # self.log.error(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "get refunded payment order error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "get refunded payment order success", result
            )
        )

    async def get_total_payment(self,request):
        result = []
        params = request.query
        user_id = params.get("user_id")
        game_name = params.get("game_name")
        channel = params.get("channel")
        try:
            result = await Order().totalpayment(
                user_id=user_id,
                game_name=game_name,
                channel=channel
            )
        except:
            # self.log.error(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "restore error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "restore success", result
            )
        )

    async def get_undelivered_payment_order(self, request):
        result = []
        params = request.query
        user_id = params.get("user_id")
        game_name = params.get("game_name")
        channel = params.get("channel")
        try:
            result = await Order().select(
                user_id=user_id,
                claimed=OrderStatus.UNDELIVERED,
                game_name=game_name,
                channel=channel
            )
        except:
            # self.log.error(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "restore error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "restore success", result
            )
        )

    async def is_existed_order(self, user_id, order_id):
        result = await Order().select(
            user_id=user_id,
            order_id=order_id
        )
        # self.log.info(result)
        if result:
            return True
        return False

    async def deliver_payment_order(self, request):
        result = []
        params = await request.post()
        user_id = params.get("user_id")
        order_id = params.get("order_id")
        game_name = params.get("game_name")
        channel = params.get("channel")
        try:
            is_claimed = await Order().select_one(
                claimed=OrderStatus.DELIVERED,
                user_id=user_id,
                order_id=order_id,
                game_name=game_name,
                channel=channel
            )
            if is_claimed:
                return Response.json_response(
                    Response.message_typesetting(
                        200, f"this order:{order_id} alread deliver", order_id
                    )
                )
            result = await Order().update_by_where(
                claimed=OrderStatus.DELIVERED
            ).where(
                user_id=user_id,
                order_id=order_id,
                game_name=game_name,
                channel=channel
            )
            if result == 0:
                return Response.json_response(
                    Response.message_typesetting(
                        404, f"deliver order failure, service has no this order:{order_id}", order_id
                    )
                )
        except:
            # self.log.error(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "deliver order error", order_id
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "deliver order success", order_id
            )
        )

    async def refund_payment_order(self, request):
        result = {}
        params = await request.post()
        user_id = params.get("user_id")
        order_id = params.get("order_id")
        game_name = params.get("game_name")
        channel = params.get("channel")
        channel_order_id = params.get("channel_order_id")
        try:
            if channel_order_id:
                is_refunded = await Order().select_one(
                        claimed=OrderStatus.REFUNDED,
                        game_name=game_name,
                        channel=channel,
                        channel_order_id=channel_order_id
                )
                params = dict(
                    game_name=game_name,
                    channel=channel,
                    channel_order_id=channel_order_id
                )
            else:
                is_refunded = await Order().select_one(
                    claimed=OrderStatus.REFUNDED,
                    user_id=user_id,
                    order_id=order_id,
                    game_name=game_name,
                    channel=channel
                )
                params = dict(
                    user_id=user_id,
                    order_id=order_id,
                    game_name=game_name,
                    channel=channel
                )
            if is_refunded:
                        return Response.json_response(
                            Response.message_typesetting(
                                200, f"this order:{order_id} is already refunded", order_id
                            )
                        )
            result = await Order().update_by_where(
                    claimed=OrderStatus.REFUNDED
            ).where(
                    **params        
                )
            if result == 0:
                    return Response.json_response(
                        Response.message_typesetting(
                            404, f"refund order failure, service has no this order:{order_id}", order_id
                        )
                    )

        except:
            return Response.json_response(
                Response.message_typesetting(
                    500, "refund order error", order_id
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "update order success", order_id
            )
        )

    async def cancel_payment_order(self, request):
        result = {}
        params = await request.post()
        user_id = params.get("user_id")
        order_id = params.get("order_id")
        game_name = params.get("game_name")
        channel = params.get("channel")
        try:
            is_refunded = await Order().select_one(
                claimed=OrderStatus.CANCELED,
                user_id=user_id,
                order_id=order_id,
                game_name=game_name,
                channel=channel
            )
            if is_refunded:
                return Response.json_response(
                    Response.message_typesetting(
                        200, f"this order:{order_id} is already canceled", order_id
                    )
                )
            result = await Order().update_by_where(
                claimed=OrderStatus.CANCELED
            ).where(
                user_id=user_id,
                order_id=order_id,
                game_name=game_name,
                channel=channel
            )
            if result == 0:
                return Response.json_response(
                    Response.message_typesetting(
                        404, f"cancel order failure, service has no this order:{order_id}", order_id
                    )
                )
        except:
            return Response.json_response(
                Response.message_typesetting(
                    500, "cancel order error", order_id
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "cancel order success", order_id
            )
        )
