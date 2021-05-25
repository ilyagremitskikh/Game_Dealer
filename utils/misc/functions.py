import logging
import datetime
from datetime import timezone

import asyncpg
from aiogram import Dispatcher
from aiogram.utils.emoji import emojize
from aiogram_broadcaster import TextBroadcaster

from loader import api
from utils.db_api.models import user_game, shop, deal

logger = logging.getLogger(__name__)


def group_deals(list_):
    values = set(map(lambda x: x["game_id"], list_))
    res = [{"game_id": value, "deals": []} for value in values]
    for dict_ in list_:
        for i in range(len(res)):
            if dict_["game_id"] == res[i]["game_id"]:
                res[i]["title"] = dict_["title"]
                res[i]["image"] = dict_["image"]
                res[i]["rating"] = {"percent": dict_["rating_percent"],
                                    "total_reviews": dict_["total_reviews"]}
                res[i]["deals"].append({"price_new": dict_["price_new"],
                                        "price_old": dict_["price_old"],
                                        "price_cut": dict_["price_cut"],
                                        "shop_id": dict_["shop_id"],
                                        "shop_title": dict_["shop_title"],
                                        "url": dict_["url"]})

    sorted_res = sorted(res, key=lambda x: x['deals'][0]['price_new'])
    return sorted_res


async def update_deals_for_user_games(pool: asyncpg.pool.Pool):
    logger.info("Получаем игры из списков пользователей...")
    users_games = await user_game.get_all_users_games(pool)
    if not users_games:
        logger.info("В списках пользователей игр не найдено")
        return
    users_games_str = ','.join(game['game_id'] for game in users_games)
    shops = await shop.get_all(pool)
    shops_str = ','.join(item['id'] for item in shops)
    logger.info("Получаем текущие цены на игры...")
    prices = await api.get_current_prices(plains=users_games_str, shops=shops_str)
    logger.info("Извлекаем скидки...")
    deals_data = await api.extract_deals(prices_data=prices)
    if not deals_data:
        logger.info("Для игр в базе данных скидок нет.")
        return
    logger.info(f"Найдено {len(deals_data)} игр со скидками...")
    logger.info(f"Добавляем скидки в базу данных...")
    await deal.save_deals_to_db(pool, deals_data)
    logger.info("Удаляем устаревшие скидки...")
    await deal.delete_old_deals(pool)


def get_rating_smile(rating_percent):
    if rating_percent > 80:
        rating_smile = ":heart_eyes:"
    elif 80 >= rating_percent > 60:
        rating_smile = ":stuck_out_tongue:"
    elif 60 >= rating_percent > 40:
        rating_smile = ":unamused:"
    elif 40 >= rating_percent > 20:
        rating_smile = ":confused:"
    else:
        rating_smile = ":astonished:"
    return rating_smile


# Оповещает пользователей о новой скидке на игру из их списка
async def notify_about_deals(pool: asyncpg.pool.Pool):
    new_deals = await deal.get_all_new_deals(pool)
    if not new_deals:
        return
    grouped_new_deals = group_deals(new_deals)
    for game in grouped_new_deals:
        users_with_game = await user_game.get_users_with_game(pool, game['game_id'])
        users_with_game = [user_id['user_id'] for user_id in users_with_game]
        if game['rating']['percent']:
            rating_smile = get_rating_smile(game['rating']['percent'])
        else:
            rating_smile = ':no_mouth:'
        text = f"Новые скидки на игру:\n" \
               f":video_game: <b>{game['title']}!</b>\n\n" \
               f"Рейтинг в Steam: {game['rating']['percent'] if game['rating']['percent'] else 'нет рейтинга'} " \
               f"{rating_smile}\n" \
               f"Всего отзывов: " \
               f"{game['rating']['total_reviews'] if game['rating']['total_reviews'] else 'нет отзывов в Steam'} :speech_balloon:\n\n" \
               f"-------------------------------------------" \

        for price in game['deals']:
            price_new = round(price['price_new'])
            price_old = round(price['price_old'])
            price_cut = round(price['price_cut'])
            shop_title = price['shop_title']
            url = price['url']
            text += f"\nМагазин: {shop_title}\n" \
                    f":small_red_triangle_down: <b>-{price_cut}%</b> | {price_old} руб. -> {price_new} руб.\n" \
                    f"<a href='{game['image']}'>&#8205;</a>" \
                    f":credit_card: <a href='{url}'>Купить</a> :credit_card:\n"
        text += f"-------------------------------------------"
        await TextBroadcaster(users_with_game, text=emojize(text)).run()
    for new_deal in new_deals:
        await deal.change_deal_new_status(pool, new_deal)



if __name__ == '__main__':
    pass
