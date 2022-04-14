import traceback

from data.model.UserRecord import UserRecord
from data.model.GameExpiry import GameExpiry
from utils.Response import Response
from utils.Time import Time


class UserRecordService:

    def __init__(self, *args, **kargs):
        pass

    async def update_login_time(self, request):
        result = []
        params = await request.post()
        unique_id = params.get("unique_id")
        channel = params.get("channel")
        game_name = params.get("game_name")
        time = Time.local_format_time()
        try:
            user = await UserRecord().select_one(
                unique_id=unique_id,
                channel=channel,
                game_name=game_name
            )
            if user:
                first_login_time = user["first_login_time"]
                if not first_login_time:
                    await UserRecord().update_by_where(
                        first_login_time=time,
                        last_login_time=time
                    ).where(
                        unique_id=unique_id,
                        channel=channel,
                        game_name=game_name
                    )
                else:
                    await UserRecord().update_by_where(
                        last_login_time=time
                    ).where(
                        unique_id=unique_id,
                        channel=channel,
                        game_name=game_name
                    )
                result = time
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        404, "no data for this user", result
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "update user login time error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "get user login time success", result
            )
        )

    async def get_user_record(self, request):
        result = []
        params = request.query
        unique_id = params.get("unique_id")
        channel = params.get("channel")
        game_name = params.get("game_name")
        try:
            result = await UserRecord().select_one(
                unique_id=unique_id,
                channel=channel,
                game_name=game_name
            )
            if result:
                result['first_login_time'] = result['first_login_time'].strftime("%Y-%m-%d %H:%M:%S")
                result['last_login_time'] = result['last_login_time'].strftime("%Y-%m-%d %H:%M:%S")
                result['create_time'] = result['create_time'].strftime("%Y-%m-%d %H:%M:%S")
        except:
            return Response.json_response(
                Response.message_typesetting(
                    500, "get user record error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "get user record success", result
            )
        )

    async def is_login_permitted(self, request):
        result = []
        login_expiry_date = ""
        params = await request.post()
        unique_id = params.get("unique_id")
        channel = params.get("channel")
        game_name = params.get("game_name")
        time = Time.local_format_time()
        try:
            game_expiry = await GameExpiry().select_one(
                game_name=game_name,
                channel=channel
            )
            if game_expiry and game_expiry['login_expiry_date']:
                login_expiry_date = game_expiry['login_expiry_date'].strftime("%Y-%m-%d %H:%M:%S")

            user = await UserRecord().select_one(
                unique_id=unique_id,
                channel=channel,
                game_name=game_name
            )

            if user:
                create_time = user['create_time'].strftime("%Y-%m-%d %H:%M:%S") if user['create_time'] else ""
                if create_time and login_expiry_date and Time.cmp(create_time, login_expiry_date):
                    return Response.json_response(
                        Response.message_typesetting(
                            200, "get user login permition success", -1
                        )
                    )
                result = user['is_login_permitted']
            else:
                await UserRecord().insert(
                    unique_id=unique_id,
                    channel=channel,
                    game_name=game_name,
                    is_pay_permitted=1,
                    is_login_permitted=0,
                    create_time=time
                )
                result = 0
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "get user login permition error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "get user login permition success", result
            )
        )

    async def set_login_permition(self, request):
        result = []
        params = await request.post()
        unique_id = params.get("unique_id")
        channel = params.get("channel")
        game_name = params.get("game_name")
        permition = params.get("permition")
        try:
            user = await UserRecord().select(
                unique_id=unique_id,
                channel=channel,
                game_name=game_name
            )
            if user:
                await UserRecord().update_by_where(
                    is_login_permitted=permition
                ).where(
                    unique_id=unique_id,
                    channel=channel,
                    game_name=game_name
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        404, "no information for this user", result
                    )
                )
            result = permition
        except:
            return Response.json_response(
                Response.message_typesetting(
                    500, "set user login permition error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "set user login permition success", result
            )
        )

    async def is_pay_permitted(self, request):
        result = []
        params = await request.post()
        pay_expiry_date = ""
        unique_id = params.get("unique_id")
        channel = params.get("channel")
        game_name = params.get("game_name")
        time = Time.local_format_time()
        try:
            game_expiry = await GameExpiry().select_one(
                game_name=game_name,
                channel=channel
            )

            if game_expiry and game_expiry['pay_expiry_date']:
                pay_expiry_date = game_expiry['pay_expiry_date'].strftime("%Y-%m-%d %H:%M:%S")

            user = await UserRecord().select_one(
                unique_id=unique_id,
                channel=channel,
                game_name=game_name
            )
            if user:
                create_time = user['create_time'].strftime("%Y-%m-%d %H:%M:%S") if user['create_time'] else ""
                if create_time and pay_expiry_date and Time.cmp(create_time, pay_expiry_date):
                    return Response.json_response(
                            Response.message_typesetting(
                                200, "get user pay permition success", -1
                            )
                        )
                result = user['is_pay_permitted']
            else:
                await UserRecord().insert(
                    unique_id=unique_id,
                    channel=channel,
                    game_name=game_name,
                    is_pay_permitted=1,
                    is_login_permitted=0,
                    create_time=time
                )
                result = 1
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "get user pay permition error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "get user pay permition success", result
            )
        )

    async def set_pay_permition(self, request):
        result = []
        params = await request.post()
        unique_id = params.get("unique_id")
        channel = params.get("channel")
        game_name = params.get("game_name")
        permition = params.get("permition")
        try:
            user = await UserRecord().select_one(
                unique_id=unique_id,
                channel=channel,
                game_name=game_name
            )
            if user:
                await UserRecord().update_by_where(
                    is_pay_permitted=permition
                ).where(
                    unique_id=unique_id,
                    channel=channel,
                    game_name=game_name
                )
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        404, "no information for this user", result
                    )
                )
            result = permition
        except:
            return Response.json_response(
                Response.message_typesetting(
                    500, "set user login permition error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "set user login permition success", result
            )
        )


