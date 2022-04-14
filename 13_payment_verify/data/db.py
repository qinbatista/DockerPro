import logging

logging.basicConfig(level=logging.INFO)
import aiomysql
from config.DBConfig import DB_CONFIG
import traceback

async def init(app):
    """定义mysql全局连接池"""
    global _mysql_pool
    _mysql_pool = await aiomysql.create_pool(
        **DB_CONFIG
    )
    return _mysql_pool


async def fetchone(sql, args=()):
    """封装select，查询单个，返回数据为字典"""
    async with _mysql_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(sql, args)
                rs = await cur.fetchone()
                return rs
            finally:
                if cur:
                    await cur.close()


async def select(sql, args=(), size=None):
    """封装select，查询多个，返回数据为列表"""
    async with _mysql_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(sql, args)
                if size:
                    rs = await cur.fetchmany(size)
                else:
                    rs = await cur.fetchall()
                return rs
            finally:
                if cur:
                    await cur.close()


async def execute(sql, args=()):
    """封装insert, delete, update"""
    async with _mysql_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(sql, args)
            except BaseException:
                #log.error(traceback.format_exc())
                await conn.rollback()
                return False
            else:
                affected = cur.rowcount
                return affected
            finally:
                if cur:
                    await cur.close()


async def close(app):
    _mysql_pool.close()
    await _mysql_pool.wait_closed()
