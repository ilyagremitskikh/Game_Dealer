import logging

from aiogram import types
from aiogram.dispatcher.filters import Command

from filters import IsAdminFilter
from utils.db_api.models import deal, user_game, shop

logger = logging.getLogger(__name__)

from loader import dp, db, api


@dp.message_handler(IsAdminFilter(), Command('update_deals'))
async def update_deals_command(message: types.Message):
    await deal.delete_all_deals(db.pool)
    users_games = await user_game.get_all_users_games(db.pool)
    users_games_str = ','.join(game['game_id'] for game in users_games)
    shops = await shop.get_all(db.pool)
    shops_str = ','.join(item['id'] for item in shops)
    prices = await api.get_current_prices(plains=users_games_str, shops=shops_str)
    deals_data = await api.extract_deals(prices_data=prices)
    await deal.save_deals_to_db(db.pool, deals_data)
    logger.info("Список скидок успешно обновлен по команде /update_deals")
    await message.answer(text="Список скидок успешно обновлен!")