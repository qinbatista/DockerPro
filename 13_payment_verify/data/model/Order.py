from data.model.Base import Base
from data.db import fetchone as db_fetchone

class Order(Base):
    table_name = "order"
    coloum = {
        "order_id": "",
        "channel": "",
        "price": "",
        "des": "",
        "production_id": "",
        "user_id": "",
        "claimed": "",
        "payment": "",
        "game_name": "",
        "channel_order_id": "",
        "role_id": "",
        "is_sandbox": 0
    }

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)

    async def select_last_order(self, **kwargs):
        keys = list(kwargs.keys())
        print("keys="+keys)
        for key in keys:
            kwargs[key] = "'{}'".format(kwargs[key])
        sql = f"select {','.join(['`{0}`'.format(coloum) for coloum in self.coloum.keys()])} from `{self.table_name}` " \
            f"where {' and '.join(['`{0}`={1}'.format(key, kwargs[key]) for key in keys])} and claimed in (0,1) order by record_date desc limit 0,1"
        result = await db_fetchone(sql=sql)
        return result



