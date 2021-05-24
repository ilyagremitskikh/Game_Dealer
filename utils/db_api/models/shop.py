import logging

logger = logging.getLogger(__name__)

import asyncpg


async def add_one(pool: asyncpg.pool.Pool, shop_id: str, shop_title: str = None):
    """
    Добавляет один магазин в базу данных
    Args:
        pool: Database.pool obj.
        shop_id: id магазина
        shop_title: title магазина

    Returns:

    """
    sql = """
        INSERT INTO Shops(id, title) VALUES($1, $2) ON CONFLICT DO NOTHING
        """
    try:
        await pool.execute(sql, shop_id, shop_title)
        logger.info(f"Добавляем в базу данных магазин: {shop_title}")
    except asyncpg.exceptions as e:
        logger.error(e)

async def get_all(pool: asyncpg.pool.Pool):
    sql = """
        SELECT id FROM shops
    """
    return await pool.fetch(sql)