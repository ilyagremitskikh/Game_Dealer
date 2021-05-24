import logging

from utils.misc.functions import get_rating_smile

logger = logging.getLogger(__name__)

from aiogram.dispatcher.filters import ForwardedMessageFilter
from aiogram.types import InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize

import re

from aiogram import types
from aiogram.dispatcher import filters

from keyboards.inline import search_answer_keyboard
from loader import dp, db, api
from utils.db_api.models import game, user_game
from utils.db_api.useful_funcs import save_multiple_games


async def create_articles(search_results):
    """
    Возвращает список InlineQueryResultArticle
    из списка результатов поиска в БД

    Args:
        search_results (list): Список результатов поиска в БД

    Returns:
        list: список InlineQueryResultArticle
    """
    results = []
    for result in search_results:
        if result['rating_percent']:
            rating_percent = result['rating_percent']
            rating_smile = get_rating_smile(rating_percent)
            rating = emojize(f"Рейтинг в Steam: {result['rating_percent']} {rating_smile}\n"
                             f"Всего обзоров: {result['total_reviews']} :trophy:")
        else:
            rating = ""
        if result['image']:
            image = result['image']
        else:
            dummy_image = "https://i.imgur.com/UVrIUMw.jpeg"
            image = dummy_image

        input_message_content = InputTextMessageContent(
            message_text=f"reply_game:{result['game_id']}",
            parse_mode="HTML"
        )
        results.append(types.InlineQueryResultArticle(
            id=str(hash(result['game_id'])),
            title=result['title'],
            thumb_url=image,
            description=rating,
            input_message_content=input_message_content,
        ))
    return results


@dp.inline_handler(filters.Text)
async def process_inline_query(query: types.InlineQuery):
    user_query = query['query']
    if len(user_query) > 3:
        # Если длина строки запроса больше 3 символов
        logger.info(f"Ищу в базе данных игры по названию: {user_query}")
        db_results = await game.find_by_title(db.pool, user_query)
        # Ищем подходящие игры в базе данных
        if len(db_results) >= 3:
            logger.info(f"В базе данных найдено {len(db_results)} результатов")
        elif len(db_results) < 3:
            logger.info(f"В базе данных найдено недостаточно результатов, ищу данные на isthereanydeal.com")
            api_search_results = await api.search_games(user_query)
            if not api_search_results:
                pass  # Пустой артикл
            games_info = await api.get_info(api_search_results)
            if not games_info:
                return
            logger.info(f"На isthereanydeal найдено {len(games_info)} игр по запросу {user_query}. Добавляю их в "
                        f"базу данных")
            db_results = await save_multiple_games(games_info)
        articles = await create_articles(db_results)
        await query.answer(
            results=articles,
            cache_time=10)


@dp.message_handler(ForwardedMessageFilter, regexp='(?<=reply_game:).*')
async def reply_inline_game(message: types.Message):
    text = message.text
    game_match = re.search('(?<=reply_game:).*', text)
    game_id = game_match.group(0)
    await message.delete()
    game_data = await game.select_game(db.pool, plain=game_id)
    if game_data['rating_percent']:
        rating_smile = get_rating_smile(game_data['rating_percent'])
    else:
        rating_smile = ""
    text = f":video_game: Игра — <b>{game_data['title']}</b>\n<a href='{game_data['image']}'>&#8205;</a>\n"
    if game_data['rating_percent']:
        text += f":chart_with_upwards_trend: Рейтинг в Steam: <b>{game_data['rating_percent']}</b> {rating_smile}\n\n" \
                f"Всего оценок: <b>{game_data['total_reviews']}</b> :trophy:"
    keyboard = await search_answer_keyboard.create_keyboard(plain=game_id)
    await message.answer(text=emojize(text), parse_mode="HTML", reply_markup=keyboard)


@dp.callback_query_handler(search_answer_keyboard.search_answer_keyboard_callback.filter(place="search"))
async def add_game_to_user(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    game_id = callback_data['id']
    await user_game.add_game_to_user(pool=db.pool, user_id=user_id, game_id=game_id)
    logger.info(f"Пользователь {user_id} добавил в свой список игру {game_id}")
    await callback.message.edit_reply_markup(InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=emojize(":mag: Найти еще"), switch_inline_query_current_chat="")
    ]]))
    await callback.answer(text="Игра добавлена в ваш список")
