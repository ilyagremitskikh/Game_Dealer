import json
import logging

from utils.misc.functions import update_deals_for_user_games, notify_about_deals

logger = logging.getLogger(__name__)

from aiogram import executor

from loader import dp, db, scheduler
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.models import shop


def schedule_jobs():
    scheduler.add_job(update_and_notify, "interval", hours=6, args=(db.pool,))

async def update_and_notify(pool):
    await update_deals_for_user_games(pool)
    await notify_about_deals(pool)

async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Создаем подключение к базе данных
    await db.create()

    # Создаем таблицы
    await db.create_tables()

    # Добавляем магазины в базу данных
    with open('data/shops.json', 'r') as file:
        shops = json.load(file)
        for item in shops:
            await shop.add_one(db.pool, shop_id=item['id'], shop_title=item['title'])

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)

    # Запускаем повторяющиеся задачи
    schedule_jobs()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] %(name)s — %(message)s',
                        datefmt='%d/%m/%y %H:%M:%S')
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)
