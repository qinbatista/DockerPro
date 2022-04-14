import re
import time
import datetime
import aiohttp
from config.ServiceConfig import IDCARD_AUDIT_AUTHORIZATION_CODE, IDCARD_AUDIT_URL


class Identity:

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    @property
    def birth_year(self):
        return int(self.number[6:10])

    @property
    def birth_month(self):
        return int(self.number[10:12])

    @property
    def birth_day(self):
        return int(self.number[12:14])

    @property
    def gender(self):
        num = int(self.number[16:17])
        if num % 2 == 0:
            return 2
        else:
            return 1

    @property
    def birth(self):
        return f"{self.birth_year}-{self.birth_month}-{self.birth_day}"

    @property
    def age(self):
        """通过身份证号获取年龄"""
        now = (datetime.datetime.now() + datetime.timedelta(days=1))
        year = now.year
        month = now.month
        day = now.day
        if year == self.birth_year:
            return 0
        else:
            if self.birth_month > month or (self.birth_month == month and self.birth_day > day):
                return year - self.birth_year - 1
            else:
                return year - self.birth_year

    @property
    def common_number(self):
        """身份证号全小写"""
        return self.number.lower()

    @property
    def verify_number(self):
        if len(self.number) != 18:
            message = "身份证号码长度不符合要求"
            return False, message
        ten = ['X', 'x', 'Ⅹ']
        id = ["10" if x in ten else x for x in self.number]  # 将罗马数字Ⅹ和字母X替换为10
        w = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_code = [1, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        sum = 0
        for i in range(17):
            sum = sum + int(id[i]) * w[i]
        if check_code[sum % 11] == int(id[17]):
            message = "身份证号码验证正确"
            return True, message
        else:
            message = "身份证号码验证错误"
            return False, message

    @property
    def verify_name(self):
        message = "正确的名字"
        test_str = re.search(r"\W", self.name)
        if test_str:
            message = self.name + ",包含特色字符"
            return False, message
        if len(self.name) < 2 or len(self.name) >= 6:
            message = self.name + ",非正常名字长度"
            return False, message
        if bool(re.search('[a-z]', self.name)):
            message = self.name + ",包含小写英文"
            return False, message
        if bool(re.search('[A-Z]', self.name)):
            message = self.name + ",包含大写英文"
            return False, message
        return True, message

    async def verify(self):
        is_valid_number, message = self.verify_number
        if not is_valid_number:
            return is_valid_number, message
        is_valid_name, message = self.verify_name
        if not is_valid_name:
            return is_valid_name, message
        is_name_matched_number, message = await self.verify_name_matched_number
        if not is_name_matched_number:
            return is_name_matched_number, message
        message = "验证成功"
        return True, message

    @property
    async def verify_name_matched_number(self):
        try:
            headers = {
                "Authorization": IDCARD_AUDIT_AUTHORIZATION_CODE,
                "X-Ca-Nonce": str(int(time.time()))
            }
            data = dict(idcard=self.number, realname=self.name)
            async with aiohttp.request(
                    method='POST',
                    url=IDCARD_AUDIT_URL,
                    data=data,
                    headers=headers
            ) as resp:
                result = await resp.json(encoding='utf-8')
                code = result.get("errcode", "")
                message = result.get("result", {}).get("errmsg", "")
        except:
            return False, "实名认证接口异常"
        if code == "00000":
            return True, message
        return False, message

if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        Identity(name="吴甜洋", number="500381199212170217").verify_name_matched_number
    )


