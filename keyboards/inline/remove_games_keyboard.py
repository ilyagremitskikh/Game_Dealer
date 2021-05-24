from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

callback_data = CallbackData("game", "action", "plain")


async def create_keyboard(game_id: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Удалить",
                                 callback_data=callback_data.new(action="delete",
                                                                 plain=game_id)),
            InlineKeyboardButton(text="Назад",
                                 callback_data=callback_data.new(action="back",
                                                                 plain=game_id))
        ]
    ])
    return keyboard
