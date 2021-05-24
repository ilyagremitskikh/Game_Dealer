from typing import Union
import asyncpg
from asyncpg import Pool

from data import config

import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Создается база данных без подключения в loader"""
        self.pool: Union[Pool, None] = None

    async def create(self):
        """В этой функции создается подключение к базе"""
        logger.info("Создаем подключение к базе данных")
        pool = await asyncpg.create_pool(
            user=config.PGUSER,
            password=config.PGPASSWORD,
            host=config.IP,
            database=config.DATABASE,
            max_size=100,
            max_inactive_connection_lifetime=0
        )
        self.pool = pool
        logger.info("Подключение к базе данных создано")

    async def create_table_users(self):
        logger.info("Создаем таблицу `users`")
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            user_id bigint NOT NULL UNIQUE,
            name varchar(255),
            username varchar(255),
            PRIMARY KEY (user_id)
            );
            """
        await self.pool.execute(sql)

    async def create_table_shops(self):
        logger.info("Создаем таблицу `shops`")
        sql = """
        CREATE TABLE IF NOT EXISTS Shops (
        id varchar(255) NOT NULL UNIQUE,
        title varchar(255),
        PRIMARY KEY (id)
        );
        """
        await self.pool.execute(sql)

    async def create_table_games(self):
        logger.info("Создаем таблицу `games`")
        sql = """
        CREATE TABLE IF NOT EXISTS Games (
        game_id varchar(255) NOT NULL UNIQUE,
        title varchar(255),
        image varchar(255),
        is_package bool,
        is_dlc bool,
        rating_percent real,
        rating_text varchar(255),
        total_reviews bigint,
        PRIMARY KEY (game_id)
        );
        """
        await self.pool.execute(sql)

    async def create_table_users_games(self):
        logger.info("Создаем таблицу `users_games`")
        sql = """
        CREATE TABLE IF NOT EXISTS Users_Games (
        user_id bigint,
        game_id varchar(255),
        PRIMARY KEY (user_id, game_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (game_id) REFERENCES Games(game_id)
        );
        """
        await self.pool.execute(sql)

    async def create_table_deals(self):
        logger.info("Создаем таблицу `deals`")
        sql = """
        CREATE TABLE IF NOT EXISTS Deals (
        game_id varchar(255),
        shop_id varchar(255),
        shop_title varchar(255),
        price_new real,
        price_old real,
        price_cut real,
        url varchar (255),
        was_sent bool default false,
        PRIMARY KEY (game_id, shop_id),
        FOREIGN KEY (game_id) REFERENCES Games(game_id),
        FOREIGN KEY (shop_id) REFERENCES Shops(id)
        );
        """
        await self.pool.execute(sql)

    async def create_tables(self):
        await self.create_table_users()
        await self.create_table_shops()
        await self.create_table_games()
        await self.create_table_deals()
        await self.create_table_users_games()