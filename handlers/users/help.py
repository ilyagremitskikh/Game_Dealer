from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: \n",
            "/games - Управление своим списком игр",
            "/deals - Проверить скидки на отслеживаемые игры",
            "/how_to - Получить справку о том, как добавлять игры",
            "/faq - Часто задаваемые вопросы")
    
    await message.answer("\n".join(text))
