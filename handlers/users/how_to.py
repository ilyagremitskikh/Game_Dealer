import logging

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InputMediaPhoto

from loader import dp

logger = logging.getLogger(__name__)

@dp.message_handler(Command('how_to'))
async def send_how_to(message: types.Message):
    images = [InputMediaPhoto(media='https://i.imgur.com/WvX7Q5J.png'),
              InputMediaPhoto(media='https://i.imgur.com/MFfyW4f.png'),
              InputMediaPhoto(media='https://i.imgur.com/rSQ8dX1.png')]
    await message.answer_media_group(media=images)