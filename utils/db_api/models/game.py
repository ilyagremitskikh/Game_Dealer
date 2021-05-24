import asyncpg


async def add_one(pool: asyncpg.pool.Pool, game_id, title, image, is_package, is_dlc, rating_percent,
                  rating_text, total_reviews):
    sql = """INSERT INTO games(game_id, title, image, is_package, is_dlc, rating_percent, rating_text, total_reviews) 
    VALUES($1, $2, $3, $4, $5, $6, $7, $8) ON CONFLICT (game_id) DO UPDATE SET game_id = $1 RETURNING *"""
    return await pool.fetchrow(sql, game_id, title, image, is_package, is_dlc, rating_percent, rating_text,
                       total_reviews)


async def find_by_title(pool: asyncpg.pool.Pool, query: str):
    """
    Ищет в БД подходящие игры по полю `title`

    Args:
        pool (asyncpg.pool.Pool): Объект пула базы данных
        query (str): Поисковый запрос

    Returns:
        list: Список найденных игр или пустой список, если игр по запросу не найдено
    """
    if len(query) >= 3:
        sql = "SELECT * FROM Games WHERE title ~* $1 AND is_dlc = False ORDER BY total_reviews DESC NULLS LAST"
        return await pool.fetch(sql, query)
    else:
        return []


async def select_game(pool: asyncpg.pool.Pool, plain: str):
    """

    Args:
        pool:
        plain:

    Returns:

    """
    sql = f"SELECT * FROM Games WHERE game_id = $1"
    return await pool.fetchrow(sql, plain)
