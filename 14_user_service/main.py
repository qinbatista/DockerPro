from aiohttp import web
from aiohttp_swagger import *

from config.AppConfig import APP_CONFIG, PORT
from data import db
from utils.Request import Request
from utils.Response import Response

ROUTES = web.RouteTableDef()


@ROUTES.post('/signup/password')
@Request.required_params("username", "password", "device_id")
async def signup_with_password(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].signup_with_password(request)
    return result


@ROUTES.post('/login/password')
@Request.required_params("username", "password", "device_id")
async def login_with_password(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].login_with_password(request)
    return result


@ROUTES.post('/login/device_id')
@Request.required_params('device_id')
async def login_with_device_id(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].login_with_device_id(request)
    return result


@ROUTES.post('/login/mobile')
@Request.required_params("mobile", "sms_code", "device_id")
async def login_with_mobile(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].login_with_mobile(request)
    return result


@ROUTES.post('/user/is_logged_in')
@Request.required_params("device_id", "token")
async def is_authenticated(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].is_logged_in(request)
    return result


@ROUTES.post('/user/bind_mobile')
@Request.required_params("username", "mobile", "sms_code")
async def bind_phone_number(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].bind_mobile(request)
    return result


@ROUTES.post('/user/verify_mobile')
@Request.required_params("username", "mobile")
async def bind_phone_number(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].verify_mobile(request)
    return result


@ROUTES.post('/user/change_mobile')
@Request.required_params("origin_mobile", "current_mobile")
async def bind_phone_number(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].change_mobile(request)
    return result


@ROUTES.post('/user/find_password')
@Request.required_params("mobile", "sms_code", "password")
async def bind_phone_number(request: web.Request) -> web.Response:
    result = await request.app['USER_SERVICE'].find_password(request)
    return result


@ROUTES.post('/user/is_authenticated')
@Request.required_params("username")
async def is_authenticated(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).is_authenticated(request)
    return result


@ROUTES.get('/user/login_time')
@Request.required_params("username")
async def get_login_time(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).get_login_time(request)
    return result


@ROUTES.put('/user/login_time')
@Request.required_params("username", "time")
async def set_login_time(request: web.Request) -> web.Response:
    result = await (request.app['USER_SERVICE']).set_login_time(request)
    return result


@ROUTES.post('/identity/verify')
@Request.required_params("name", "number")
async def verify_identity(request: web.Request) -> web.Response:
    result = await (request.app['IDENTITY_SERVICE']).verify(request)
    return result


@ROUTES.post('/identity/authenticate')
@Request.required_params("name", "number", "username")
async def authenticate(request: web.Request) -> web.Response:
    result = await (request.app['IDENTITY_SERVICE']).authenticate(request)
    return result


@ROUTES.post('/send_sms_code')
@Request.required_params("type", "mobile")
async def send_sms_code(request: web.Request) -> web.Response:
    result = await (request.app['COMMON_SERVICE']).send_sms_code(request)
    return result


@ROUTES.get('/healthcheck')
async def healthcheck(request: web.Request) -> web.Response:
    return Response.json_response(
        Response.message_typesetting(
            status=200,
            message="health",
            data=True
        )
    )


def run():
    print("LoginSystemManager version:1.0")
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
