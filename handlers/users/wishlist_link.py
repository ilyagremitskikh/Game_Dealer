import logging

logger = logging.getLogger(__name__)

import re

import aiohttp
from aiogram import types

from keyboards.inline import wishlist_keyboard
from loader import dp, api, db
from utils.db_api.models import user_game
from utils.db_api.useful_funcs import save_multiple_games


@dp.message_handler(regexp="<?wishlist/profiles/(\\d+)")
async def process_wishlist_link(message: types.Message):
    url = message.text
    steam_user_id = re.search("<?wishlist/profiles/(\\d+)", url).group(1)
    wishlist_json_link = f"https://store.steampowered.com/wishlist/profiles/{steam_user_id}/wishlistdata/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=wishlist_json_link) as response:
            if response.status != 200:
                logger.error(f"Ошибка подключения. Статус: {response.status}")
                return
            result = await response.json()
            titles = "\n".join(f"<b>{value['name']}</b>" for key, value in result.items())
            keyboard = await wishlist_keyboard.create_keyboard(steam_user_id=steam_user_id)
            await message.answer(f"В вашем списке желаемого найдены следующие игры:\n{titles}",
                                 reply_markup=keyboard)


@dp.callback_query_handler(wishlist_keyboard.wishlist_keyboard_callback.filter(action="add"))
async def import_wishlist_games_to_user(callback: types.CallbackQuery, callback_data: dict):
    steam_user_id = callback_data['steam_user_id']
    telegram_user_id = callback.from_user.id
    wishlist_json_link = f"https://store.steampowered.com/wishlist/profiles/{steam_user_id}/wishlistdata/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=wishlist_json_link) as response:
            if response.status != 200:
                logger.error("Ошибка подключения. Статус: {response.status}")
                return
            result = await response.json()
            game_ids = [key for key in result.keys()]
            game_ids_str = ','.join(('app/' + game_id) for game_id in game_ids)
            plains_list = await api.get_multiple_plains(shop="steam", game_ids=game_ids_str)
            plains_str = ','.join(plains_list)
            games_info = await api.get_info(plains_str)
            await save_multiple_games(games_info)
            for game_plain in plains_list:
                await user_game.add_game_to_user(db.pool, user_id=telegram_user_id, game_id=game_plain)
            await callback.message.delete_reply_markup()
            await callback.answer(text="Игры успешно импортированы в ваш список отслеживания")
            logger.info(f"Пользователь {telegram_user_id} успешно импортировал свой wishlist из steam")


@dp.callback_query_handler(wishlist_keyboard.wishlist_keyboard_callback.filter(action="cancel"))
async def remove_keyboard(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup()
