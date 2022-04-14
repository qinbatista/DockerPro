import hashlib
from utils import PYTHON_VERSION_3

class MD5:
    """
    md5的加密和验证
    """
    @classmethod
    def encrypt_lower(cls,content=""):
        if PYTHON_VERSION_3:
            content = content.encode()
        return hashlib.md5(content).hexdigest()

    @classmethod
    def encrypt_upper(cls,content=""):
        if PYTHON_VERSION_3:
            content = content.encode()
        return hashlib.md5(content).hexdigest().upper()

    @classmethod
    def verify(cls, content, sign, is_upper=False):
        if is_upper:
            result = cls.encrypt_upper(content)
            return result == sign
        return cls.encrypt_lower(content) == sign

