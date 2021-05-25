from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data import config
from utils.db_api.db import Database
from utils.itad_api.itad import Itad

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
api = Itad(api_key=config.ITAD_API_KEY)
db = Database()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()

