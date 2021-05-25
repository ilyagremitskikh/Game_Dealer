import logging

logger = logging.getLogger(__name__)

import asyncpg


async def save_deals_to_db(pool: asyncpg.pool.Pool, deals: dict):
    for plain, prices in deals.items():
        for price in prices:
            sql = """
                INSERT INTO deals(game_id, shop_id, shop_title, price_new, price_old, price_cut, url) 
                VALUES($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (game_id, shop_id)
                DO UPDATE SET added_at = now()
                RETURNING game_id
            """
            await pool.fetch(sql,
                             plain,
                             price['shop']['id'],
                             price['shop']['name'],
                             price['price_new'],
                             price['price_old'],
                             price['price_cut'],
                             price['url']
                             )


async def get_user_deals(pool: asyncpg.pool.Pool, user_id: int):
    sql = """
        SELECT ug.user_id, g.game_id, g.title, d.shop_id, d.shop_title, d.price_new, d.price_old,
       d.price_cut, d.url, g.image, g.rating_percent, g.total_reviews
        FROM deals d
        INNER JOIN games g on g.game_id = d.game_id
        INNER JOIN users_games ug on g.game_id = ug.game_id
        WHERE ug.user_id = $1
    """
    return await pool.fetch(sql, user_id)


async def get_game_deals(pool: asyncpg.pool.Pool, game_id: str):
    sql = """
        SELECT g.title, g.game_id, g.image, g.rating_percent,
       g.total_reviews, d.shop_title, d.price_new,
       d.price_old, d.price_cut, d.url, d.shop_id
        FROM games g
        INNER JOIN deals d on g.game_id = d.game_id
        WHERE d.game_id = $1
        ORDER BY d.price_new
    """
    return await pool.fetch(sql, game_id)


async def delete_all_deals(pool: asyncpg.pool.Pool):
    sql = """
    DELETE FROM deals WHERE True
    """
    await pool.execute(sql)


async def delete_old_deals(pool: asyncpg.pool.Pool):
    sql = """
    DELETE FROM deals WHERE added_at < current_timestamp - interval '5' minute
    """
    await pool.execute(sql)


async def get_all_new_deals(pool: asyncpg.pool.Pool):
    sql = """
    SELECT g.title, g.image, g.rating_percent, g.total_reviews, d.game_id, d.shop_id, d.shop_title,
       d.price_new, d.price_old, d.price_cut, d.url, d.is_new
    FROM games g
    INNER JOIN deals d on g.game_id = d.game_id
    WHERE is_new = True
    ORDER BY d.price_new
    """
    return await pool.fetch(sql)


async def change_deal_new_status(pool: asyncpg.pool.Pool, record: asyncpg.Record):
    sql = """
    UPDATE deals 
    SET is_new = False
    WHERE game_id = $1 AND shop_id = $2 AND price_new = $3
    AND price_old = $4 AND price_cut = $5 AND is_new = True
    """
    await pool.execute(sql, record['game_id'], record['shop_id'], record['price_new'],
                       record['price_old'], record['price_cut'])
