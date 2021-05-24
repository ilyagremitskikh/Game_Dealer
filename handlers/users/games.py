from aiogram import types
from aiogram.dispatcher.filters import Command

import logging
logger = logging.getLogger(__name__)

from keyboards.inline import users_games_keyboard, remove_games_keyboard

from loader import dp, db
from utils.db_api.models import user_game, game


# Обработка команды /games
@dp.message_handler(Command('games'))
async def send_games_edit(message: types.Message):
    user_id = message.from_user.id
    games_exist = await user_game.check_exist(db.pool, user_id=user_id)
    if games_exist == 0:
        await message.answer("Вы пока не добавили ни одной игры для отслеживания. Используйте команду /help, чтобы "
                             "узнать о способах добавления игр в свой список")
    else:
        users_games = await user_game.get_users(db.pool, user_id=user_id)
        keyboard = await users_games_keyboard.create_keyboard(users_games)
        await message.answer(text="Управляйте списком ваших игр",
                             reply_markup=keyboard)


# Обработка кнопок пагинации
@dp.callback_query_handler(users_games_keyboard.pagination_callback_data.filter(action="paginate"))
async def process_games_pagination(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    page_number = int(callback_data['page_number'])
    users_games = await user_game.get_users(db.pool, user_id=user_id)
    keyboard = await users_games_keyboard.create_keyboard(users_games, page=page_number)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


# Обработка клика по кнопке игры
@dp.callback_query_handler(users_games_keyboard.callback_data.filter(action="view"))
async def send_game_menu(callback: types.CallbackQuery, callback_data: dict):
    game_id = callback_data['plain']
    game_data = await game.select_game(db.pool, plain=game_id)
    text = f"<b>{game_data['title']}</b>\n" \
           f"<b>Рейтинг в Steam:</b> {game_data['rating_percent'] if game_data['rating_percent'] else 'Отсутствует'}\n" \
           f"<b>Количество отзывов:</b> {game_data['total_reviews'] if game_data['total_reviews'] else 'Отсутствуют'}" \
           f"<a href='{game_data['image']}'>&#8205;</a>"
    keyboard = await remove_games_keyboard.create_keyboard(game_id=game_id)
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)


# Обработка клика удаления игры
@dp.callback_query_handler(remove_games_keyboard.callback_data.filter(action="delete"))
async def delete_game_from_user(callback: types.CallbackQuery, callback_data: dict):
    game_id = callback_data['plain']
    user_id = callback.from_user.id
    await user_game.delete_game_from_user(db.pool, game_id=game_id, user_id=user_id)
    logger.info(f"Пользователь {user_id} удалил из своего списка игру {game_id}")
    await callback.answer(text="Игра удалена из вашего списка")
    games_exist = await user_game.check_exist(db.pool, user_id=user_id)
    if games_exist == 0:
        await callback.message.edit_text(
            "Вы пока не добавили ни одной игры для отслеживания. Используйте команду /help, чтобы "
            "узнать о способах добавления игр в свой список")
    else:
        users_games = await user_game.get_users(db.pool, user_id=user_id)
        keyboard = await users_games_keyboard.create_keyboard(users_games)
        await callback.message.edit_text(text="Управляйте списком ваших игр",
                                         reply_markup=keyboard)


# Обработка клика "Назад"
@dp.callback_query_handler(remove_games_keyboard.callback_data.filter(action="back"))
async def back_to_user_games(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    users_games = await user_game.get_users(db.pool, user_id=user_id)
    keyboard = await users_games_keyboard.create_keyboard(users_games)
    await callback.message.edit_text(text="Управляйте списком ваших игр",
                                     reply_markup=keyboard)
