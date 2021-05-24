import logging
import re

from aiogram import types
from aiogram.utils.emoji import emojize

from keyboards.inline import search_answer_keyboard
from loader import dp, db, api
from utils.db_api.models import game
from utils.misc.functions import get_rating_smile

logger = logging.getLogger(__name__)


@dp.message_handler(regexp='https?://')
async def process_link(message: types.Message):
    link = message.text
    if re.search("(<?(app|sub)/\\d+)", link):
        steam_id = re.search("(<?(app|sub)/\\d+)", link)
        steam_id = steam_id.group(0)
        game_id = await api.get_plain(game_id=steam_id, shop='steam')
        game_info = await api.get_info(plains=game_id)
        for plain, data in game_info.items():
            game_data = await game.add_one(db.pool, game_id=plain, title=data['title'], image=data['image'],
                               is_package=data['is_package'], is_dlc=data['is_dlc'],
                               rating_text=data['reviews']['steam']['text'] if data.get('reviews') else None,
                               rating_percent=data['reviews']['steam']['perc_positive'] if data.get(
                                   'reviews') else None,
                               total_reviews=data['reviews']['steam']['total'] if data.get('reviews') else None)
            if game_data['rating_percent']:
                rating_smile = get_rating_smile(game_data['rating_percent'])
            else:
                rating_smile = ""
            text = f":video_game: Игра — <b>{game_data['title']}</b>\n<a href='{game_data['image']}'>&#8205;</a>\n"
            if game_data['rating_percent']:
                text += f":chart_with_upwards_trend: Рейтинг в Steam: <b>{game_data['rating_percent']}</b> {rating_smile}\n\n" \
                        f"Всего оценок: <b>{game_data['total_reviews']}</b> :trophy:"
            keyboard = await search_answer_keyboard.create_keyboard(plain=game_id)
            await message.reply(text=emojize(text), reply_markup=keyboard)
