import logging

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data import config


class IsAdminFilter(BoundFilter):
    async def check(self, message: types.Message):
        if message.from_user.id in config.ADMINS:
            return True
        else:
            return False