from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

import math

from aiogram.utils.emoji import emojize

callback_data = CallbackData("game", "action", "plain")
pagination_callback_data = CallbackData("game", "action", "page_number")


async def create_keyboard(games_rows, page: int = 0):
    MAX_ITEMS_PER_PAGE = 5
    max_page = math.ceil(len(games_rows) / MAX_ITEMS_PER_PAGE)
    first_item_index = page * MAX_ITEMS_PER_PAGE
    last_item_index = (page + 1) * MAX_ITEMS_PER_PAGE
    sliced_games = games_rows[first_item_index:last_item_index]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Добавить игры",
                                      switch_inline_query_current_chat=""))
    for game in sliced_games:
        keyboard.add(InlineKeyboardButton(text=game['title'],
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
