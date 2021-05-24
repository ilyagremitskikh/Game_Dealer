from loader import db
from utils.db_api.models import game
import operator


async def save_multiple_games(games_info):
    results = []
    for plain, data in games_info.items():
        temp_res = await game.add_one(db.pool, game_id=plain, title=data['title'], image=data['image'],
                                      is_package=data['is_package'], is_dlc=data['is_dlc'],
                                      rating_text=data['reviews']['steam']['text'] if data.get('reviews') else '',
                                      rating_percent=data['reviews']['steam']['perc_positive'] if data.get(
                                          'reviews') else 0,
                                      total_reviews=data['reviews']['steam']['total'] if data.get('reviews') else 0)
        results.append(temp_res)
    results = sorted(results, key=operator.itemgetter('total_reviews'), reverse=True)
    return results
