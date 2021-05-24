import logging

import asyncio
import json
from typing import Union, List, Dict

import aiohttp

logger = logging.getLogger(__name__)

class Itad:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    async def get_all_stores() -> Union[list, None]:
        """
        Returns:
            list: Сохраняет список магазинов в RU регионе в json-файл
        """
        base_url = "https://api.isthereanydeal.com/v02/web/stores/?region=ru&country=RU"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=base_url) as response:
                if response.status != 200:
                    logger.error(f"Ошибка подключения. Статус: {response.status}")
                    return
                result = await response.json()
                with open('../../data/shops.json', 'w') as file:
                    json.dump(result['data'], file)

    async def search_games(self, query: str) -> Union[str, None]:
        """
            Ищет игры на ITAD и возвращает строку plains для найденных игр
        Args:
            query: str -> поисковой запрос

        Returns:
            plains_str: str -> строка plains найденных игр
        """
        payload = {'key': self.api_key, 'limit': 20, 'q': query, 'strict': 1}
        base_url = "https://api.isthereanydeal.com/v02/search/search/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=base_url, params=payload) as response:
                if response.status != 200:
                    logger.error(f"Ошибка подключения. Статус: {response.status}")
                    return
                result = await response.json()
                result = result['data'].get('results')
                if not result:
                    logger.warning(f"Игры по запросу:{query} не найдены на ITAD")
                else:
                    plains_list = [game['plain'] for game in result]
                    plains_str = ','.join(plains_list)
                    return plains_str

    async def get_info(self, plains: str):
        base_url = f"https://api.isthereanydeal.com/v01/game/info/?key={self.api_key}&plains={plains}"
        if plains:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=base_url) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка подключения. Статус: {response.status}")
                        return
                    result = await response.json()
                    return result['data']
        else:
            return None

    async def get_plain(self, identify_type: str = "id",
                        shop: str = None, game_id=None) -> Union[str, None]:
        """
        Args:
            identify_type: str -> может быть id или link
            shop: str -> steam, epic etc.
            game_id: -> идентификатор игры в определенном магазине

        Returns:
            result: -> plain идентифицируемой игры
        """
        base_url = f"https://api.isthereanydeal.com/v02/game/plain/?key={self.api_key}"
        if identify_type == "id":
            url = base_url + f"&shop={shop}&game_id={game_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка подключения. Статус: {response.status}")
                        return
                    result = await response.json()
                    if result.get('data'):
                        return result['data']['plain']
                    else:
                        logger.warning(f"Игра по ссылке {url} не найдена")

    async def get_multiple_plains(self, shop: str = None, game_ids: str = None) -> Union[list, None]:
        """
        Возвращает plains игр по строке их идентификаторов в магазине
        Пример строки: app/377160,app/96100,sub/28187,sub/1245
        Args:
            shop: str -> название магазина
            game_ids: str -> строка идентификаторов через запятую

        Returns:
            result: list -> список plains для идентифицируемых игр
        """
        url = f"https://api.isthereanydeal.com/v01/game/plain/id/?key={self.api_key}&shop={shop}&ids={game_ids}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                if response.status != 200:
                    logger.error(f"Ошибка подключения. Статус: {response.status}")
                    return
                result = await response.json()
                if result.get('data'):
                    result = [v for v in result['data'].values() if v is not None]
                    return result
                else:
                    logger.warning(f"Игры по ссылке {url} не найдены")

    async def get_current_prices(self, plains: str, shops: str):
        """Получает текущие цены для игр по строке plains

        Args:
            shops: (str): список магазинов в виде строки через запятую
            plains (str): список игр в виде строки через запятую
        """
        plains_list = plains.split(',')
        plains_list = [plains_list[i:i + 10] for i in range(0, len(plains_list), 10)]
        final_result = dict()
        # Получаем цены по 10 игр в цикле
        for chunk in plains_list:
            plains_str = ','.join(chunk)
            base_url = "https://api.isthereanydeal.com/v01/game/prices/"
            payload = {'key': self.api_key,
                       'plains': plains_str,
                       'region': 'ru',
                       'country': 'RU',
                       'shops': shops}
            async with aiohttp.ClientSession() as session:
                async with session.get(url=base_url, params=payload) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка подключения. Статус: {response.status}")
                        return
                    result = await response.json()
                    for plain, list_ in result['data'].items():
                        final_result[plain] = list_
        return final_result

    @staticmethod
    async def extract_deals(prices_data: dict):
        deals = {plain: [item for item in data['list'] if item['price_cut'] > 0] for plain, data in prices_data.items()
                 if any([item for item in data['list'] if item['price_cut'] > 0])}
        return deals


if __name__ == '__main__':
    itad = Itad('3fcc953675c2cce17f6605c24bbcb538845f6713')
    loop = asyncio.get_event_loop()
    prices = loop.run_until_complete(
        itad.get_current_prices(plains="vampyr", shops='steam,gog,epic,greenmangaming,gamersgate,bundlestars'))
    loop.run_until_complete(itad.extract_deals(prices))
