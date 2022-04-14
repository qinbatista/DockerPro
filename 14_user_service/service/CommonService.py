import redis
from aiohttp import web
from redis.connection import ConnectionPool

from config.RedisConfig import REDIS_COMFIG
from config.ServiceConfig import SMS_TEMPLATE, MAX_SMS_CODE_CACHE_TIME,MAX_SMS_SEND_COUNT_IN_DAY, CACHE_DAY
from utils.Random import Random
from utils.Response import Response
from utils.SMS import SMS


class CommonService:

    def __init__(self, *args, **kargs):
        self.__dict__.update(*args)
        self.__dict__.update(**kargs)
        self.cache = redis.StrictRedis(connection_pool=ConnectionPool(**REDIS_COMFIG))

    async def get_params(self, request: web.Request):
        params = {}
        if request.method in ("POST", "PUT"):
            params = await request.post()
        elif request.method in ("GET", "DELETE"):
            params = request.query
        params = dict(params)
        params['headers'] = request.headers
        params['ip'] = request.remote
        return params

    async def send_sms_code(self, request: web.Request):
        params = await self.get_params(request)
        try:
            mobile = params['mobile']
            sms_send_count = self.cache.get(f"smd_send_count_{mobile}")
            if sms_send_count and int(sms_send_count) > MAX_SMS_SEND_COUNT_IN_DAY:
                return Response.json_response(
                    Response.message_typesetting(
                        status=400,
                        message=f"一个手机号码最多一天只能发送{MAX_SMS_SEND_COUNT_IN_DAY}次",
                        data=""
                    )
                )
            type = params['type']
            code = Random.generate_code(4)
            result = await SMS.send(
                mobile=mobile,
                template_code=SMS_TEMPLATE.type(type),
                code=code
            )
            if result.get("Code", "") == "OK":
                self.cache.setex(name=f"sms_code_{type}_{mobile}", value=code, time=MAX_SMS_CODE_CACHE_TIME)
                self.cache.incr(f"smd_send_count_{mobile}")
                if not sms_send_count:
                    self.cache.expire(f"smd_send_count_{mobile}",time=CACHE_DAY)
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="发送验证码成功",
                        data=code
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=500,
                        message="发送验证码错误",
                        data=False
                    )
                )
        except:
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="发送验证码错误,服务端错误",
                    data=False
                )
            )
    def process(self, request: web.Request):
        pass
