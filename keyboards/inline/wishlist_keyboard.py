from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

wishlist_keyboard_callback = CallbackData("games", "action", "steam_user_id")


async def create_keyboard(steam_user_id: str):
    keyboard = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text="Импортировать",
                                                                 callback_data=wishlist_keyboard_callback.new(
                                                                     action="add",
                                                                     steam_user_id=steam_user_id
                                                                 )),
                                            InlineKeyboardButton(text="Отмена",
                                                                 callback_data=wishlist_keyboard_callback.new(
                                                                     action="cancel",
                                                                     steam_user_id="None"
                                                                 ))
                                        ]
                                    ])
    return keyboard
