import logging

import asyncpg

logger = logging.getLogger(__name__)

async def add_game_to_user(pool: asyncpg.pool.Pool, user_id: int, game_id: str):
    sql = """
    INSERT INTO Users_Games(user_id, game_id) VALUES($1, $2) ON CONFLICT DO NOTHING
    """
    try:
        return await pool.execute(sql, user_id, game_id)
    except asyncpg.exceptions as exeption:
        pass
        # logger.error(f"Ошибка при добавлении игры в список пользователя: {exeption}")


async def get_all_users_games(pool: asyncpg.pool.Pool):
    sql = """
        SELECT game_id FROM users_games
    """
    return await pool.fetch(sql)


async def get_users(pool: asyncpg.pool.Pool, user_id):
    sql = """
        SELECT DISTINCT g.game_id, g.title 
        FROM Games g 
        JOIN Users_Games ug ON g.game_id = ug.game_id 
        JOIN Users 
        ON ug.user_id = $1
        ORDER BY g.title
        """
    return await pool.fetch(sql, user_id)


async def delete_game_from_user(pool: asyncpg.pool.Pool, game_id, user_id):
    sql = """
        DELETE FROM users_games WHERE game_id = $1 AND user_id = $2
        """
    await pool.execute(sql, game_id, user_id)


async def check_exist(pool: asyncpg.pool.Pool, user_id):
    sql = """
        SELECT COUNT(1) FROM users_games WHERE user_id = $1 
    """
    return await pool.fetchval(sql, user_id)
