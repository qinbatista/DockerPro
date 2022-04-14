from config import ServiceConfig
from data.model.User import User
from service.CommonService import CommonService
from utils.MD5 import MD5
from utils.Response import Response
from utils.Time import Time
import traceback


class UserService(CommonService):

    async def is_logged_in(self, request):
        params = await self.get_params(request)
        try:
            device_id = params['device_id']
            token = params['token']
            if self.cache.get(name=f"session_{token}") == device_id:
                return Response.message_typesetting(
                    status=200,
                    message="该用户已登录",
                    data=token
                )
            return Response.message_typesetting(
                status=200,
                message="该用户已退出",
                data=""
            )
        except:
            print(traceback.format_exc())
            return Response.message_typesetting(
                status=500,
                message="获取用户状态错误,服务端错误",
                data=""
            )

    async def signup_with_password(self, request):
        params = await self.get_params(request)
        try:
            username = params['username']
            password = params['password']
            device_id = params['device_id']
            channel = params.get("channel", "")
            game_name = params.get("game_name", "")
            ip = params.get("ip", "")
            is_username_exsited = await User().is_existed(
                username=username
            )
            if is_username_exsited:
                return Response.json_response(
                    Response.message_typesetting(
                        status=400,
                        message="该用户已被注册",
                        data=0
                    )
                )
            result = await User().signup(
                username=username,
                password=password,
                device_id=device_id,
                channel=channel,
                signup_ip=ip
            )
            if result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="注册成功",
                        data=result
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=500,
                        message="注册错误，服务端错误",
                        data=result
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="注册错误，服务端错误",
                    data={}
                )
            )

    async def login_with_password(self, request):
        params = await self.get_params(request)
        result = {}
        try:
            username = params['username']
            password = params['password']
            device_id = params['device_id']
            token = MD5.encrypt_upper(device_id + username + ServiceConfig.MD5_KEY)
            session = self.cache.get(name=f"session_{token}")
            if session:
                if session == device_id:
                    return Response.json_response(
                        Response.message_typesetting(
                            status=200,
                            message="该用户已经处于登录状态",
                            data=token
                        )
                    )
            result = await User().login(
                username=username,
                password=password
            )
            if result:
                await User().update_last_login_time(
                    username=username,
                    password=password,
                    last_login_time=Time.local_format_time()
                )
                token = MD5.encrypt_upper(device_id + username + ServiceConfig.MD5_KEY)
                self.cache.setex(name=f"session_{token}", value=device_id, time=ServiceConfig.TOKEN_MAX_CACHE_TIME)
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="登录成功",
                        data=token
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="登陆失败,用户名或密码错误",
                        data=result
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="登录错误, 服务端错误",
                    data=result
                )
            )

    async def login_with_device_id(self, request):
        params = await self.get_params(request)
        try:
            device_id = params['device_id']
            result = await User().last_user_by_device_id(
                device_id=device_id
            )
            if result:
                username = result['username']
                token = MD5.encrypt_upper(device_id + username + ServiceConfig.MD5_KEY)
                if self.cache.get(name=f"session_{token}") == device_id:
                    return Response.json_response(
                        Response.message_typesetting(
                            status=200,
                            message="该用户已经处于登录状态",
                            data=token
                        )
                    )
                self.cache.setex(name=f"session_{token}", value=device_id, time=ServiceConfig.TOKEN_MAX_CACHE_TIME)
                await User().update_last_login_time(
                    username=username,
                    last_login_time=Time.local_format_time()
                )
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="登录成功",
                        data=token
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="登录失败,该设备未被注册,只有注册时使用的设备才能登陆",
                        data=result
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="登录错误, 服务端错误",
                    data={}
                )
            )

    async def login_with_mobile(self, request):
        params = await self.get_params(request)
        try:
            channel = params.get("channel", "")
            game_name = params.get("game_name", "")
            ip = params.get("ip", "")
            mobile = params['mobile']
            sms_code = params['sms_code']
            device_id = params['device_id']
            sms_cache_code = self.cache.get(name=f"sms_code_{ServiceConfig.SMS_TYPE.LOGIN}_{mobile}")
            if sms_cache_code != sms_code:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="输入的手机验证码错误,请输入手机验证码",
                        data=""
                    )
                )
            result = await User.is_existed(
                mobile=mobile
            )
            if result:
                username = result['username']
                token = MD5.encrypt_upper(device_id + username + ServiceConfig.MD5_KEY)
                session = self.cache.get(name=f"session_{token}")
                if session:
                    return Response.json_response(
                        Response.message_typesetting(
                            status=200,
                            message="该用户已经处于登录状态",
                            data=token
                        )
                    )
                self.cache.setex(name=f"session_{token}", value=device_id, time=ServiceConfig.TOKEN_MAX_CACHE_TIME)
                await User().update_last_login_time(
                    username=username,
                    last_login_time=Time.local_format_time()
                )
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="登录成功",
                        data=token
                    )
                )
            else:
                username = mobile
                result = await User().signup(
                    username=username,
                    password="",
                    device_id=device_id,
                    channel=channel,
                    signup_ip=ip,
                    mobile=mobile
                )
                token = MD5.encrypt_upper(device_id + username + ServiceConfig.MD5_KEY)
                self.cache.setex(name=f"session_{token}", value=device_id, time=ServiceConfig.TOKEN_MAX_CACHE_TIME)
                await User().update_last_login_time(
                    username=username,
                    last_login_time=Time.local_format_time()
                )
                if result:
                    return Response.json_response(
                        Response.message_typesetting(
                            status=200,
                            message="登录成功",
                            data=token
                        )
                    )
                else:
                    return Response.json_response(
                        Response.message_typesetting(
                            status=500,
                            message="登录错误, 服务端错误",
                            data=False
                        )
                    )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="登录错误, 服务端错误",
                    data={}
                )
            )

    async def verify_mobile(self, request):
        params = await self.get_params(request)
        try:
            username = params['username']
            mobile = params['mobile']
            sms_code = params['sms_code']
            sms_cache_code = self.cache.get(name=f"sms_code_{ServiceConfig.SMS_TYPE.VERIFY_MOBILE}_{mobile}")
            if sms_cache_code != sms_code:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="输入的手机验证码错误,请输入手机验证码",
                        data=""
                    )
                )
            user = User().is_existed(
                mobile=mobile,
                username=username
            )
            if user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="检查用户原有手机号码成功",
                        data=mobile
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="此号码不是用户原有的手机号码",
                        data=""
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="检查用户原有手机号码错误,服务端错误",
                    data=""
                )
            )

    async def change_mobile(self, request):
        params = await self.get_params(request)
        try:
            origin_mobile = params['origin_mobile']
            current_mobile = params['current_mobile']
            sms_code = params['sms_code']
            sms_cache_code = self.cache.get(name=f"sms_code_{ServiceConfig.SMS_TYPE.CHANGE_MOBILE}_{current_mobile}")
            if sms_cache_code != sms_code:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="输入的手机验证码错误,请输入手机验证码",
                        data=""
                    )
                )
            origin_user = await User().is_existed(
                mobile=origin_mobile
            )
            if not origin_user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=404,
                        message="该手机号码绑定的用户不存在,请注册用户",
                        data=""
                    )
                )
            current_user = await User().is_existed(
                mobile=current_mobile
            )
            if current_user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="填入的新手机号码已经绑定了用户,该号码无效",
                        data=""
                    )
                )
            username = origin_user["username"]
            result = await User().update_by_where(
                mobile=current_mobile
            ).where(
                username=username
            )
            if result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="换绑用户电话号码成功",
                        data=current_mobile
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=500,
                        message="换绑用户电话号码错误,服务端错误",
                        data=""
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="换绑用户电话号码错误,服务端错误",
                    data=""
                )
            )

    async def find_password(self, request):
        params = await self.get_params(request)
        try:
            mobile = params['mobile']
            password = params['password']
            sms_code = params['sms_code']
            sms_cache_code = self.cache.get(name=f"sms_code_{ServiceConfig.SMS_TYPE.CHANGE_PASSWORD}_{mobile}")
            if sms_cache_code != sms_code:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="输入的手机验证码错误,请输入正确的手机验证码",
                        data=""
                    )
                )
            user = await User().is_existed(
                mobile=mobile
            )
            if not user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=404,
                        message="该手机号码绑定的用户不存在,请注册用户",
                        data={}
                    )
                )
            username = user["username"]
            result = await User().update_by_where(
                password=password
            ).where(
                username=username
            )
            if result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="设置用户新密码成功",
                        data=password
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=500,
                        message="设置用户新密码成功错误,服务端错误",
                        data=""
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="设置用户新密码成功错误,服务端错误",
                    data=""
                )
            )

    async def bind_mobile(self, request):
        params = await self.get_params(request)
        try:
            username = params['username']
            mobile = params['mobile']
            sms_code = params['sms_code']
            sms_cache_code = self.cache.get(name=f"sms_code_{ServiceConfig.SMS_TYPE.BIND}_{mobile}")
            if sms_cache_code != sms_code:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="输入的手机验证码错误,请输入手机验证码",
                        data=""
                    )
                )
            user = await User().is_existed(
                username=username
            )
            if not user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=404,
                        message="该用户名不存在,请注册用户",
                        data=""
                    )
                )
            is_binded = user['mobile']
            if is_binded:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="该用户已绑定手机号码",
                        data=""
                    )
                )
            user = await User().is_existed(
                mobile=mobile
            )
            if user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=-200,
                        message="该号码已经被绑定",
                        data=""
                    )
                )
            result = await User().update_by_where(
                mobile=mobile
            ).where(
                username=username
            )
            if result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="绑定用户电话号码成功",
                        data=mobile
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=500,
                        message="绑定用户电话号码错误,服务端错误",
                        data=""
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="绑定用户电话号码错误,服务端错误",
                    data=""
                )
            )

    async def set_login_time(self, request):
        params = await self.get_params(request)
        try:
            time = params['time']
            username = params['username']
            user = await User().is_existed(
                username=username
            )
            if not user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=404,
                        message="该用户名不存在,请注册用户",
                        data={}
                    )
                )
            self.cache.setex(
                name=f"origin_login_time_{username}",
                value=time,
                time=ServiceConfig.RECORD_LOGIN_TIME_PERIOD
            )
            return Response.json_response(
                Response.message_typesetting(
                    status=200,
                    message="记录用户登陆时间成功",
                    data={}
                )
            )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="记录用户登陆时间错误，服务端错误",
                    data={}
                )
            )

    async def get_login_time(self, request):
        params = await self.get_params(request)
        try:
            username = params['username']
            result = self.cache.get(
                name=f"origin_login_time_{username}",
            )
            if result:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="获取到用户登陆时间e",
                        data=result
                    )
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="用户登录时间不存在",
                        data=""
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    status=500,
                    message="获取失败,服务端错误",
                    data={}
                )
            )

    async def is_authenticated(self, request):
        params = await self.get_params(request)
        try:
            username = params['username']
            user = await User().is_existed(
                username=username
            )
            if not user:
                return Response.json_response(
                    Response.message_typesetting(
                        status=404,
                        message="该用户不存在,请注册",
                        data=False
                    )
                )
            if user['is_authenticate']:
                return Response.json_response(
                    Response.message_typesetting(
                        status=200,
                        message="该用户已实名认证",
                        data=True
                    )
                )
            return Response.json_response(
                Response.message_typesetting(
                    status=-200,
                    message="该用户未实名认证",
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
