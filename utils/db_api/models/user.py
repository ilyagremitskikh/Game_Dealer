import logging

logger = logging.getLogger(__name__)

import asyncpg


async def add(pool: asyncpg.pool.Pool, user_id: int, name: str = None, username: str = None):
    # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'johnthebest')"
    sql = """
        INSERT INTO Users(user_id, name, username)
        VALUES($1, $2, $3)
        ON CONFLICT (user_id) DO NOTHING
        RETURNING user_id, name, username
        """
    try:
        result = await pool.fetchrow(sql, user_id, name, username)
        logger.info(f"Добавляем пользователя: [user_id: {user_id}, name: {name if name else 'Не задан'},"
                    f" username: {username if username else 'Не задан'}] в базу данных")
        return result
    except BaseException as e:
        logger.error(e)
