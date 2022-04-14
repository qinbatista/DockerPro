import traceback

from data.model.UserRecord import UserRecord
from data.model.GameExpiry import GameExpiry
from utils.Response import Response
from utils.Time import Time

class GameExpiryService:

    def __init__(self, *args, **kargs):
        pass

    async def insert(self, request):
        result = False
        params = await request.post()
        channel = params.get("channel")
        game_name = params.get("game_name")
        login_expiry_date = params.get('login_expiry_date')
        pay_expiry_date = params.get('pay_expiry_date')
        try:
            game_expiry = await GameExpiry().select_one(
                channel=channel,
                game_name=game_name
            )
            if game_expiry:
                return Response.json_response(
                    Response.message_typesetting(
                        200, "add  GameExpiry success", {}
                    )
                )
            result = await GameExpiry().insert(
                channel=channel,
                game_name=game_name,
                login_expiry_date=login_expiry_date,
                pay_expiry_date=pay_expiry_date
            )
            if result:
                result = True
            else:
                return Response.json_response(
                    Response.message_typesetting(
                        500, "insert  GameExpiry error ", result
                    )
                )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "insert  GameExpiry error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "insert  GameExpiry  success", result
            )
        )


    async def update(self, request):
        result = False
        params = await request.post()
        channel = params.get("channel")
        game_name = params.get("game_name")
        login_expiry_date = params.get('login_expiry_date')
        pay_expiry_date = params.get('pay_expiry_date')
        try:
            game_expiry = await GameExpiry().select_one(
                channel=channel,
                game_name=game_name
            )
            if not game_expiry:
                return Response.json_response(
                    Response.message_typesetting(
                        404, "no this  GameExpiry error", {}
                    )
                )
            result = await GameExpiry().update_by_where(
                login_expiry_date=login_expiry_date,
                pay_expiry_date=pay_expiry_date
            ).where(
                channel=channel,
                game_name=game_name
            )
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "update GameExpiry error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "update GameExpiry  success", result
            )
        )


    async def delete(self, request):
        result = False
        params = request.query
        channel = params.get("channel")
        game_name = params.get("game_name")
        try:
            game_expiry = await GameExpiry().select_one(
                channel=channel,
                game_name=game_name
            )
            if not game_expiry:
                return Response.json_response(
                    Response.message_typesetting(
                        404, "no this  GameExpiry error", {}
                    )
                )
            result = await GameExpiry().delete(
                channel=channel,
                game_name=game_name
            )
            if result:
                result = True
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "insert GameExpiry error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "insert GameExpiry  success", result
            )
        )

    async def query(self, request):
        result = {}
        params = request.query
        channel = params.get("channel")
        game_name = params.get("game_name")
        try:
            result = await GameExpiry().select_one(
                channel=channel,
                game_name=game_name
            )
            if result:
                result['login_expiry_date'] = result['login_expiry_date'].strftime("%Y-%m-%d %H:%M:%S")
                result['pay_expiry_date'] = result['pay_expiry_date'].strftime("%Y-%m-%d %H:%M:%S")
        except:
            print(traceback.format_exc())
            return Response.json_response(
                Response.message_typesetting(
                    500, "insert GameExpiry error", result
                )
            )
        return Response.json_response(
            Response.message_typesetting(
                200, "query  GameExpiry  success", result
            )
        )