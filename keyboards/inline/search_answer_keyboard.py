from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.emoji import emojize

search_answer_keyboard_callback = CallbackData("games", "place", "id")


async def create_keyboard(plain: str):
    keyboard = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(
                                                text=emojize(":heavy_plus_sign: Добавить в свой список"),
                                                callback_data=search_answer_keyboard_callback.new(
                                                    place="search",
                                                    id=plain
                                                ))
                                        ],
                                        [
                                            InlineKeyboardButton(text=emojize(":mag: Найти еще"),
                                                                 switch_inline_query_current_chat="")
                                        ]
                                    ])
    return keyboard


