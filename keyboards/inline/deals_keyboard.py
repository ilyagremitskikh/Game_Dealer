import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.emoji import emojize

callback_data = CallbackData("deal", "action", "plain")
pagination_callback_data = CallbackData("deal", "action", "page_number")


async def create_keyboard(deals: list, page: int = 0):
    MAX_ITEMS_PER_PAGE = 9
    max_page = math.ceil(len(deals) / MAX_ITEMS_PER_PAGE)
    first_item_index = page * MAX_ITEMS_PER_PAGE
    last_item_index = (page + 1) * MAX_ITEMS_PER_PAGE
    sliced_games = deals[first_item_index:last_item_index]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for game in sliced_games:
        lowest_price_item = min(game['deals'], key=lambda x:x['price_new'])
        price_new = round(lowest_price_item['price_new'])
        price_old = round(lowest_price_item['price_old'])
        price_text = f"{price_old} ₽ -> {price_new} ₽" if price_new != 0 else "Бесплатно"
        keyboard.add(InlineKeyboardButton(text=f"{game['title']} | {price_text}",
                                          callback_data=callback_data.new(action="view",
                                                                          plain=game['game_id'])))
    pagination_buttons = list()

    previous_page = page - 1
    if previous_page < 0:
        pass
    else:
        pagination_buttons.append(InlineKeyboardButton(text=emojize(":arrow_left:"),
                                                       callback_data=pagination_callback_data.new(
                                                           action="paginate",
                                                           page_number=previous_page
                                                       )))

    next_page = page + 1
    if next_page < max_page:
        pagination_buttons.append(InlineKeyboardButton(text=emojize(":arrow_right:"),
                                                       callback_data=pagination_callback_data.new(
                                                           action="paginate",
                                                           page_number=next_page
                                                       )))
    keyboard.row(*pagination_buttons)
    return keyboard