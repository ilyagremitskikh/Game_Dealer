import logging

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize

from keyboards.inline import deals_keyboard
from utils.db_api.models import deal

from loader import dp, db
from utils.misc.functions import get_rating_smile

logger = logging.getLogger(__name__)


def group_deals(list_):
    values = set(map(lambda x: x["game_id"], list_))
    res = [{"game_id": value, "deals": []} for value in values]
    for dict_ in list_:
        for i in range(len(res)):
            if dict_["game_id"] == res[i]["game_id"]:
                res[i]["title"] = dict_["title"]
                res[i]["image"] = dict_["image"]
                res[i]["rating"] = {"percent": dict_["rating_percent"],
                                    "total_reviews": dict_["total_reviews"]}
                res[i]["deals"].append({"price_new": dict_["price_new"],
                                        "price_old": dict_["price_old"],
                                        "price_cut": dict_["price_cut"],
                                        "shop_id": dict_["shop_id"],
                                        "shop_title": dict_["shop_title"],
                                        "url": dict_["url"]})

    sorted_res = sorted(res, key=lambda x: x['deals'][0]['price_new'])
    return sorted_res


# Обработка команды /deals
@dp.message_handler(Command('deals'))
async def send_user_deals(message: types.Message):
    user_id = message.from_user.id
    user_deals = await deal.get_user_deals(db.pool, user_id=user_id)
    if not user_deals:
        await message.answer("У игр из вашего списка пока нет скидок")
        return
    deals = group_deals(user_deals)
    keyboard = await deals_keyboard.create_keyboard(deals)
    await message.answer(text="По вашему списку найдены следующие скидки:",
                         reply_markup=keyboard)


# Обработка кнопок пагинации
@dp.callback_query_handler(deals_keyboard.pagination_callback_data.filter(action="paginate"))
async def process_games_pagination(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    user_id = callback.from_user.id
    page_number = int(callback_data['page_number'])
    user_deals = await deal.get_user_deals(db.pool, user_id=user_id)
    deals = group_deals(user_deals)
    keyboard = await deals_keyboard.create_keyboard(deals, page_number)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


# Обработка клика по кнопке скидки
@dp.callback_query_handler(deals_keyboard.callback_data.filter(action="view"))
async def send_game_deals(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    game_id = callback_data['plain']
    deals = await deal.get_game_deals(db.pool, game_id=game_id)
    grouped_deals = group_deals(deals)
    text = str()
    for item in grouped_deals:
        if item['rating']['percent']:
            rating_smile = get_rating_smile(item['rating']['percent'])
        else:
            rating_smile = ':no_mouth:'
        text = f":video_game: <b>{item['title']}</b>\n\n" \
               f"Рейтинг в Steam: {item['rating']['percent'] if item['rating']['percent'] else 'нет рейтинга'} " \
               f"{rating_smile}\n" \
               f"Всего отзывов: " \
               f"{item['rating']['total_reviews'] if item['rating']['total_reviews'] else 'нет отзывов в Steam'} :speech_balloon:\n\n" \
               f"-------------------------------------------" \

        for price in item['deals']:
            price_new = round(price['price_new'])
            price_old = round(price['price_old'])
            price_cut = round(price['price_cut'])
            shop_title = price['shop_title']
            url = price['url']
            text += f"\nМагазин: {shop_title}\n" \
                    f":small_red_triangle_down: <b>-{price_cut}%</b> | {price_old} руб. -> {price_new} руб.\n" \
                    f"<a href='{item['image']}'>&#8205;</a>" \
                    f":credit_card: <a href='{url}'>Купить</a> :credit_card:\n"
        text += f"-------------------------------------------"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="deals_back_button")
        ]
    ])
    await callback.message.edit_text(text=emojize(text),
                                     reply_markup=keyboard)


# Обработка клика по кнопке назад
@dp.callback_query_handler(text="deals_back_button")
async def process_back_button(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user_deals = await deal.get_user_deals(db.pool, user_id=user_id)
    deals = group_deals(user_deals)
    keyboard = await deals_keyboard.create_keyboard(deals)
    await callback.message.edit_text(text="По вашему списку найдены следующие скидки:",
                                     reply_markup=keyboard)
