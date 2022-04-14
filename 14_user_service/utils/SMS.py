import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from config.ServiceConfig import AliYun
from utils.Random import Random


class SMS:
    client = AcsClient(AliYun.ACCESS_KEY_ID, AliYun.ACCESS_SECRET, AliYun.REGION_ID)

    @classmethod
    async def request(cls):
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(AliYun.DOMAIN)
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version(AliYun.VERSION)
        request.set_action_name('SendSms')
        return request

    @classmethod
    async def send(cls, **kwargs):
        request = await cls.request()
        request.add_query_param('RegionId', AliYun.REGION_ID)
        request.add_query_param('PhoneNumbers', kwargs["mobile"])
        request.add_query_param('SignName', AliYun.SIGN_NAME)
        request.add_query_param('TemplateCode', kwargs['template_code'])
        request.add_query_param('TemplateParam', json.dumps(dict(code=kwargs['code'])))
        response = cls.client.do_action_with_exception(request)
        print(str(response, encoding='utf-8'))
        return json.loads(str(response, encoding='utf-8'))
