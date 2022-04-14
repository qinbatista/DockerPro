from data.model.Base import Base
from data.db import execute as db_execute

class UserRecord(Base):
    table_name = "user_record"
    coloum = {
        "unique_id": "",
        "channel": "",
        "game_name": "",
        "is_login_permitted": "",
        "is_pay_permitted": "",
        "first_login_time": "null",
        "last_login_time": "null",
        "create_time": "null",
    }

    def __init__(self, **kwargs):
        super(UserRecord, self).__init__(**kwargs)


    async def insert(self, **kwargs):
        self.coloum.update(**kwargs)
        for key in self.coloum.keys():
            if self.coloum[key] != "null":
                self.coloum[key] = "'{}'".format(self.coloum[key])
        sql = f"insert into `{self.table_name}` ({','.join(['`{0}`'.format(coloum) for coloum in self.coloum.keys()])}) " \
              f"values ({','.join(['{' + f'{coloum}' + '}' for coloum in self.coloum.keys()])})".format(**self.coloum)
        result = await db_execute(sql=sql)
        return result