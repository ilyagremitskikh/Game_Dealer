import logging

import asyncpg

from loader import api
from utils.db_api.models import user_game, shop, deal

logger = logging.getLogger(__name__)


async def update_deals_for_user_games(pool: asyncpg.pool.Pool):
    logger.info("Очищаем список скидок...")
    await deal.delete_all_deals(pool)
    logger.info("Получаем игры из списков пользователей...")
    users_games = await user_game.get_all_users_games(pool)
    if not users_games:
        logger.info("В списках пользователей игр не найдено")
        return
    users_games_str = ','.join(game['game_id'] for game in users_games)
    shops = await shop.get_all(pool)
    shops_str = ','.join(item['id'] for item in shops)
    logger.info("Получаем текущие цены на игры...")
    prices = await api.get_current_prices(plains=users_games_str, shops=shops_str)
    logger.info("Извлекаем скидки...")
    deals_data = await api.extract_deals(prices_data=prices)
    if not deals_data:
        logger.info("Для игр в базе данных скидок нет.")
        return
    logger.info(f"Найдено {len(deals_data)} игр со скидками...")
    logger.info(f"Добавляем скидки в базу данных...")
    await deal.save_deals_to_db(pool, deals_data)


def get_rating_smile(rating_percent):
    if rating_percent > 80:
        rating_smile = ":heart_eyes:"
    elif 80 >= rating_percent > 60:
        rating_smile = ":stuck_out_tongue:"
    elif 60 >= rating_percent > 40:
        rating_smile = ":unamused:"
    elif 40 >= rating_percent > 20:
        rating_smile = ":confused:"
    else:
        rating_smile = ":astonished:"
    return rating_smile


if __name__ == '__main__':
    pass
