from data.db import get_mysqlpool
from data.model.Base import Base
from data.model.User import User


class Identity(Base):
    table_name = "identity"
    coloum = {
        "id": "",
        "chinese_name": "",
        "id_number": "",
        "gender": "",
        "birth": ""
    }

    def __init__(self, **kwargs):
        super(Identity, self).__init__(**kwargs)

    async def authenticate(self, **kwargs):
        name = kwargs['name']
        number = kwargs['number']
        username = kwargs['username']
        gender = kwargs['gender']
        birth = kwargs['birth']
        identity = await self.select_one(
            chinese_name=name,
            id_number=number,
        )
        mysql_pool = await get_mysqlpool()
        async with mysql_pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if not identity:
                        sql = await self.insert(
                            chinese_name=name,
                            id_number=number,
                            gender=gender,
                            birth=birth,
                            return_sql=True
                        )
                        await cur.execute(sql)
                        identity_id = cur.rowcount
                    else:
                        identity_id = identity['id']
                    sql = await User().update_by_where(
                        identity_id=identity_id,
                        is_authenticate=1
                    ).where(
                        username=username,
                        return_sql=True
                    )
                    await cur.execute(sql)
                    result = cur.rowcount
                except BaseException:
                    await conn.rollback()
                    return False
                else:
                    return result
                finally:
                    if cur:
                        await cur.close()
