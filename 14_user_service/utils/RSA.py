import base64
import rsa
from utils import PYTHON_VERSION_3


class RSA:

    @classmethod
    def add_start_end(cls, key, startMarker, endMarker):
        if key.find(startMarker) < 0:
            key = startMarker + key
        if key.find(endMarker) < 0:
            key = key + endMarker
        return key

    @classmethod
    def fill_public_key_marker(cls, public_key):
        return cls.add_start_end(public_key, "-----BEGIN PUBLIC KEY-----\n", "\n-----END PUBLIC KEY-----")

    @classmethod
    def fill_private_key_marker(cls, private_key):
        return cls.add_start_end(private_key, "-----BEGIN RSA PRIVATE KEY-----\n", "\n-----END RSA PRIVATE KEY-----")

    @classmethod
    def sign_with_rsa(cls, private_key, sign_content, charset):
        if PYTHON_VERSION_3:
            sign_content = sign_content.encode(charset)
        private_key = cls.fill_private_key_marker(private_key)
        signature = rsa.sign(sign_content, rsa.PrivateKey.load_pkcs1(private_key, format='PEM'), 'SHA-1')
        sign = base64.b64encode(signature)
        if PYTHON_VERSION_3:
            sign = str(sign, encoding=charset)
        return sign

    @classmethod
    def sign_with_rsa2(cls, private_key, sign_content, charset):
        if PYTHON_VERSION_3:
            sign_content = sign_content.encode(charset)
        private_key = cls.fill_private_key_marker(private_key)
        signature = rsa.sign(sign_content, rsa.PrivateKey.load_pkcs1(private_key, format='PEM'), 'SHA-256')
        sign = base64.b64encode(signature)
        if PYTHON_VERSION_3:
            sign = str(sign, encoding=charset)
        return sign

    @classmethod
    def verify_with_rsa(cls, public_key, message, sign):
        public_key = cls.fill_public_key_marker(public_key)
        sign = base64.b64decode(sign)
        return bool(rsa.verify(message, sign, rsa.PublicKey.load_pkcs1_openssl_pem(public_key)))
