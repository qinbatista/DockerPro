from functools import wraps

from aiohttp import web
import re
from utils.MD5 import MD5
from utils.RSA import RSA
from utils.Response import Response
from utils.Time import Time


class Request:

    @classmethod
    def verify_sign(cls, func):
        @wraps(func)
        async def wrapper(request: web.Request):
            params = {}
            if request.method.lower() in ("post", "put"):
                params = await request.post()
            elif request.method.lower() in ("get", "delete"):
                params = request.query
            sign = params.pop("sign")
            if not sign:
                return Response.json_response(Response.message_typesetting(
                    400, "请求错误,请求必须带有签名", {"required_params": ["sign"]}
                ))
            else:
                sign_type = params.get("sign_type")
                message = "&".join(sorted([f"{k}={v}" for k, v in params.items()]))
                if sign_type == "md5":
                    verify_result = MD5.verify(message, sign)
                elif sign_type == "rsa":
                    verify_result = RSA.verify_with_rsa("", message, sign)
                else:
                    verify_result = MD5.verify(message, sign)
                if verify_result:
                    result = await func(request)
                    return result
                return Response.json_response(Response.message_typesetting(400, "签名验证不通过", {}))

        return wrapper

    @classmethod
    def required_params(cls, *args):
        def middle(func):
            @wraps(func)
            async def wrapper(request: web.Request):
                params = {}
                if request.method.lower() in ("post", "put"):
                    params = await request.post()
                elif request.method.lower() in ("get", "delete"):
                    params = request.query
                for key in args:
                    if not params.get(key, ""):
                        return Response.json_response(Response.message_typesetting(
                            400, "请求方式错误,部分必要参数不能为空", {"required_params": args}
                        ))
                    if re.search("date|time|day", key) and not Time.is_valid(params[key]):
                        return Response.json_response(Response.message_typesetting(
                            400, "请求参数错误,该参数不能表示有效的日期", {"error_key": key}
                        ))
                result = await func(request)
                return result

            return wrapper

        return middle