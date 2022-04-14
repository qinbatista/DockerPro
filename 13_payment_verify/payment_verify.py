from aiohttp import web
from aiohttp_swagger import *

from config.AppConfig import APP_CONFIG, PORT
from config.PaymentConfig import GAMES
from data import db
from utils.Request import Request
from utils.Response import Response

ROUTES = web.RouteTableDef()


@ROUTES.get('/order/undelivered')
@Request.required_params("user_id", "game_name", "channel")
async def get_undelivered_order(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).get_undelivered_payment_order(request)
    return result

@ROUTES.get('/order/totalpayment')
@Request.required_params("user_id", "game_name", "channel")
async def get_total_payment(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).get_total_payment(request)
    return result

@ROUTES.post('/order/deliver')
@Request.required_params("user_id", "order_id", "game_name", "channel")
async def deliver_order(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).deliver_payment_order(request)
    return result


@ROUTES.post('/order/refund')
async def refund_order(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).refund_payment_order(request)
    return result


@ROUTES.get('/order/refunded')
@Request.required_params("user_id", "game_name", "channel")
async def get_refunded_order(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).get_refunded_payment_order(request)
    return result


@ROUTES.post('/order/cancel')
@Request.required_params("user_id", "order_id", "game_name", "channel")
async def cancel_order(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).cancel_payment_order(request)
    return result


@ROUTES.get('/user')
@Request.required_params("unique_id", "game_name", "channel")
async def get_user_record(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).get_user_record(request)
    return result


@ROUTES.post('/user/is_login_permitted')
@Request.required_params("unique_id", "game_name", "channel")
async def is_login_permitted(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).is_login_permitted(request)
    return result


@ROUTES.post('/user/set_login_permition')
@Request.required_params("unique_id", "game_name", "channel", "permition")
async def set_login_permition(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).set_login_permition(request)
    return result


@ROUTES.post('/user/is_pay_permitted')
@Request.required_params("unique_id", "game_name", "channel")
async def set_login_permition(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).is_pay_permitted(request)
    return result


@ROUTES.post('/user/set_pay_permition')
@Request.required_params("unique_id", "game_name", "channel", "permition")
async def set_login_permition(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).set_pay_permition(request)
    return result


@ROUTES.put('/user/update_login_time')
@Request.required_params("unique_id", "game_name", "channel")
async def set_login_permition(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).update_login_time(request)
    return result

@ROUTES.get('/game_expiry')
@Request.required_params("game_name", "channel")
async def get_game_expiry(request: web.Request) -> web.Response:
    result = await (request.app['GAME_EXPIRY_SERVICE']).query(request)
    return result

@ROUTES.post('/game_expiry')
@Request.required_params("game_name", "channel", "login_expiry_date", "pay_expiry_date")
async def insert_game_expiry(request: web.Request) -> web.Response:
    result = await (request.app['GAME_EXPIRY_SERVICE']).insert(request)
    return result


@ROUTES.delete('/game_expiry')
@Request.required_params( "game_name", "channel")
async def delete_game_expiry(request: web.Request) -> web.Response:
    result = await (request.app['GAME_EXPIRY_SERVICE']).delete(request)
    return result


@ROUTES.put('/game_expiry')
@Request.required_params("game_name", "channel", "login_expiry_date", "pay_expiry_date")
async def update_game_expiry(request: web.Request) -> web.Response:
    result = await (request.app['GAME_EXPIRY_SERVICE']).update(request)
    return result

# notify callback
@ROUTES.post('/{game_name}/{pay_type}/client_success_callback_isbn')
async def _client_success_callback(request: web.Request) -> web.Response:
    post = await request.post()
    pay_type = request.match_info.get("pay_type", "")
    game_name = request.match_info.get("game_name", "")

    channel = post.get("channel", "")
    price = post.get("price", "")
    order_id = post.get("order_id", "")
    des = post.get("des", "")
    production_id = post.get("production_id", "")
    user_id = post.get("user_id", "")

    if pay_type in request.app['NOTIFY_SERVICE'] and game_name in GAMES:
        service = request.app['NOTIFY_SERVICE'][pay_type]
        result = await service.process(request, game_name, channel, price, order_id, des, production_id, user_id)
        return result
    else:
        return Response.json_response(request.app['MANAGER']._message_typesetting(404, "目前不支持该支付方式", {}))


# notify callback
@ROUTES.post('/{game_name}/{pay_type}/client_success_callback')
async def _client_success_callback(request: web.Request) -> web.Response:
    pay_type = request.match_info.get("pay_type", "")
    game_name = request.match_info.get("game_name", "")
    if pay_type in request.app['NOTIFY_SERVICE'] and game_name in GAMES:
        service = request.app['NOTIFY_SERVICE'][pay_type]
        result = await service.process(request, game_name)
        return result
    else:
        return Response.json_response(request.app['MANAGER']._message_typesetting(404, "目前不支持该支付方式", {}))


# notify callback
@ROUTES.get('/{game_name}/{pay_type}/client_success_callback')
async def _client_success_callback(request: web.Request) -> web.Response:
    pay_type = request.match_info.get("pay_type", "")
    game_name = request.match_info.get("game_name", "")
    if pay_type in request.app['NOTIFY_SERVICE'] and game_name in GAMES:
        service = request.app['NOTIFY_SERVICE'][pay_type]
        result = await service.process(request, game_name)
        return result
    else:
        return Response.json_response(request.app['MANAGER']._message_typesetting(404, "目前不支持该支付方式", {}))


# notify callback
@ROUTES.post('/{game_name}/{pay_type}/notice')
async def notice(request: web.Request) -> web.Response:
    pay_type = request.match_info.get("pay_type", "")
    game_name = request.match_info.get("game_name", "")
    if pay_type in request.app['NOTIFY_SERVICE'] and game_name in GAMES:
        service = request.app['NOTIFY_SERVICE'][pay_type]
        result = await service.notice(request, game_name)
        return result
    else:
        return Response.json_response(request.app['MANAGER']._message_typesetting(404, "目前不支持该支付方式", {}))


@ROUTES.get('/healthcheck')
async def healthcheck(request: web.Request) -> web.Response:
    return Response.json_response(
        {
            "status": 200,
            "message": "health",
            "data": True
        }
    )


def run():
    print("Payment_verify version 1:0")
    app = web.Application()
    app.add_routes(ROUTES)
    app.update(APP_CONFIG)
    app.on_startup.append(db.init)
    app.on_cleanup.append(db.close)
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  swagger_from_file="swagger.yaml",
                  api_version="1.0.0", )
    web.run_app(app, port=PORT)


if __name__ == '__main__':
    run()
