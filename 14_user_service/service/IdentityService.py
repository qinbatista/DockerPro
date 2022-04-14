import traceback

from data.model.Identity import Identity
from data.model.User import User
from service.CommonService import CommonService
from utils.Identity import Identity as IdentityUtil
from utils.Response import Response


class IdentityService(CommonService):

    async def verify(self, request):
        params = await self.get_params(request)
        try:
            number = params['number']
            name = params['name']
            result, message = await IdentityUtil(number=number, name=name).verify()
            if not result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message=message,
                        data=False
                    )
                )
            return Response.json_response(
                Response.message_typesetting(
                    status=200,
                    message="验证通过",
                    data=True
                )
            )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="验证错误,服务端错误",
                    data=""
                )
            )

    async def authenticate(self, request):
        params = await self.get_params(request)
        try:
            number = params['number'].lower()
            name = params['name']
            username = params['username']
            user = await User().select_one(
                username=username
            )
            if user and user['is_authenticate'] and user['identity_id']:
                return Response.json_response(
                    Response.message_typesetting(
                        status=202,
                        message="该用户已经通过实名认证",
                        data=True
                    )
                )
            if not user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="该用户不存在,请注册",
                        data=False
                    )
                )
            identity_util = IdentityUtil(number=number, name=name)
            result, message = await identity_util.verify()
            if not result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message=message,
                        data=False
                    )
                )
            result = await Identity().authenticate(
                username=username,
                name=name,
                number=number,
                gender=identity_util.gender,
                birth=identity_util.birth
            )
            if result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="实名认证通过",
                        data=True
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="实名认证未通过",
                        data=False
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="验证错误,服务端错误",
                    data=""
                )
            )
