from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db
from utils.db_api.models import user


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    tg_user = message.from_user
    await user.add(db.pool, user_id=tg_user.id, name=tg_user.full_name, username=tg_user.username)
    text = f"""Привет, приятель!\n
Хочешь найти лучшие скидки на ПК-игры? Я могу помочь!\n
Я ищу скидки по 12 лучшим магазинам игр и ключей!\n
Тебе нужно лишь добавить желаемые игры в свой список отслеживания. Чтобы узнать как это сделать, используй
команду /how_to. После того, как ты их добавишь, используй команду /deals, чтобы увидеть текущие скидки на твои игры.\n
Для вызова справки используй команду /help\n
Желаю тебе огромных скидок и приятной игры! GL&HF!
    """
    await message.answer(text=text)
