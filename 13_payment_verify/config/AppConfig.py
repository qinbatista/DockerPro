from service.AW5 import AW5
from service.AliPay import AliPay
from service.CommonService import CommonService
from service.DefaultTest import DefaultTest
from service.HuaWei import HuaWei
from service.TestChannel import TestChannel
from service.PaymentVerifyManager import PaymentVerifyManager
from service.WXPay import WXPay
from service.UserRecordService import UserRecordService
from service.GameExpiryService import GameExpiryService

PORT = "8080"
APP_CONFIG = {
    "MANAGER": PaymentVerifyManager(),
    "NOTIFY_SERVICE": {
        'alipay': AliPay(),
        'wxpay': WXPay(),
        '5aw': AW5(),
        'default_test': DefaultTest(),
        'huawei':HuaWei(),
        'TestChannel':TestChannel(),
    },
    "COMMON_SERVICE": CommonService(),
    "USER_SERVICE": UserRecordService(),
    "GAME_EXPIRY_SERVICE": GameExpiryService(),
}
