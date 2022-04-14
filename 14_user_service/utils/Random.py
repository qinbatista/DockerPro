import random


class Random:

    # 默认随机生成6位的验证码
    @classmethod
    def generate_code(cls,len=6):
        code_list = []
        for i in range(10):  # 0-9数字
            code_list.append(str(i))
        for i in range(65, 91):  # A-Z
            code_list.append(chr(i))
        for i in range(97, 123):  # a-z
            code_list.append(chr(i))
        verification_code_list = random.sample(code_list, len)
        verification_code = ''.join(verification_code_list)
        return verification_code
