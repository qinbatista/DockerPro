from data.db import execute as db_execute,\
    select as db_select,fetchone as db_fetchone,insert as db_insert
from config.ServiceConfig import AES_KEY

class Base:
    """
        基本curd操作，能满足目前的基本需要，个别需要定制化的model可以继承此类重写
    """
    table_name = ""
    coloum = {

    }
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    async def insert(self, return_sql=False, **kwargs):
        coloums = deepcopy(self.coloum)
        coloums.update(**kwargs)
        for key in coloums.keys():
            coloums[key] = "'{}'".format(coloums[key])
        sql = f"insert into `{self.table_name}` ({','.join(['`{0}`'.format(coloum) for coloum in coloums.keys()])}) " \
              f"values ({','.join(['{' + f'{coloum}' + '}' for coloum in coloums.keys()])})".format(**coloums)
        result = await db_execute(sql=sql)
        return result

    async def execute(self, sql):
        result = await db_execute(sql=sql)
        return result

    async def select(self, return_sql=False,  **kwargs):
        keys = list(kwargs.keys())
        for key in keys:
            kwargs[key] = "'{}'".format(kwargs[key])
        sql = f"select {','.join(['`{0}`'.format(coloum) for coloum in self.coloum.keys()])} from `{self.table_name}`" \
              f" where {' and '.join(['`{0}`={1}'.format(key,kwargs[key]) for key in keys])}"
        if return_sql:
            return sql
        result = await db_select(sql=sql)
        return result

    async def select_one(self, return_sql=False, **kwargs):
        keys = list(kwargs.keys())
        for key in keys:
            kwargs[key] = "'{}'".format(kwargs[key])
        sql = f"select {','.join(['`{0}`'.format(coloum) for coloum in self.coloum.keys()])} from `{self.table_name}` " \
              f"where {' and '.join(['`{0}`={1}'.format(key, kwargs[key]) for key in keys])}"
        if return_sql:
            return sql
        result = await db_fetchone(sql=sql)
        return result

    async def update(self, return_sql=False, **kwargs):
        keys = list(kwargs)
        params = ','.join(['`{0}`={1}'.format(key, kwargs[key]) for key in keys])
        sql = f"update `{self.table_name}` set {params}"
        if return_sql:
            return sql
        result = await db_execute(sql=sql)
        return result

    async def delete(self, return_sql=False, **kwargs):
        keys = list(kwargs.keys())
        for key in keys:
            kwargs[key] = "'{}'".format(kwargs[key])
        sql = f"delete `{self.table_name}` " \
              f"where {' and '.join(['`{0}`={1}'.format(key, kwargs[key]) for key in keys])}"
        if return_sql:
            return sql
        result = await db_execute(sql=sql)
        return result

    def update_by_where(self, **kwargs):
        keys = list(kwargs)
        for key in keys:
            if key == "password":
                kwargs[key] = "HEX(AES_ENCRYPT('{}','{}'))".format(kwargs[key], AES_KEY)
            else:
                kwargs[key] = "'{}'".format(kwargs[key])
        sql = f"update `{self.table_name}` set {','.join(['`{0}`={1}'.format(key, kwargs[key]) for key in keys])}"
        return Base(sql=sql)

    async def where(self, return_sql=False, **kwargs):
        keys = list(kwargs.keys())
        for key in keys:
            kwargs[key] = "'{}'".format(kwargs[key])
        sql = f"where {' and '.join(['`{0}`={1}'.format(key, kwargs[key]) for key in keys])}"
        if self.sql:
            sql = " ".join([self.sql,sql])
        if return_sql:
            return sql
        print(sql)
        result = await db_execute(sql=sql)
        return result