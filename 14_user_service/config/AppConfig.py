import sys
from service.CommonService import CommonService
from service.UserService import UserService
from service.IdentityService import IdentityService
PORT = "8080"
APP_CONFIG = {
    "COMMON_SERVICE": CommonService(),
    "USER_SERVICE": UserService(),
    "IDENTITY_SERVICE": IdentityService(),
}
