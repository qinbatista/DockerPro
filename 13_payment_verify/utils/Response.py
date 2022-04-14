import json
from aiohttp import web


class Response:

    @classmethod
    def message_typesetting(self, status: int, message: str, data: object) -> dict:
        return {"status": status, "message": message, "data": data}

    @classmethod
    def json_response(cls, body: dict = "", **kwargs) -> web.Response:
        kwargs['body'] = json.dumps(body or kwargs['kwargs']).encode('utf-8')
        kwargs['content_type'] = 'text/json'
        return web.Response(**kwargs)

    @classmethod
    def text_response(cls, body: str = "", **kwargs) -> web.Response:
        kwargs['body'] = str(body or kwargs['kwargs']).encode('utf-8')
        kwargs['content_type'] = 'text/plain'
        return web.Response(**kwargs)

