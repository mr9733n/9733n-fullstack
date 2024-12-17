import aiohttp
import asyncio
from app.libs.onlinesim_lib import fetch_fresh_numbers, fetch_last_3_sms, sort_numbers
from app.utils.logger import logger
logging = logger

class OnlinesimService:
    def __init__(self, config):
        self.headers = config["headers"]
        self.urls = config["urls"]
        self.countries = config["countries"]
        self.number_cache = {}  # Локальный кэш номеров
        logger.info("OnlinesimService initialized successfully.")

    async def update_cache(self):
        """Обновляет кэш номеров для всех стран."""
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [
                    fetch_fresh_numbers(session, country, self.headers, self.urls)
                    for country in self.countries
                ]
                results = await asyncio.gather(*tasks)
                self.number_cache = {
                    country: sort_numbers(numbers) for country, numbers in zip(self.countries, results) if numbers
                }
            logging.info(f"Number cache updated: {list(self.number_cache.keys())}")
        except Exception as e:
            logging.exception(f"Error updating cache: {e}")

    def get_cached_numbers(self, country):
        cached_numbers = self.number_cache.get(country, [])
        return cached_numbers

    async def get_numbers(self, country: str):
        """Получает номера из кэша или обновляет его."""
        if country not in self.number_cache:
            logger.info(f"Cache miss for country: {country}. Updating cache...")
            await self.update_cache()
        self.get_cached_numbers(country)
        return self.number_cache.get(country, [])

    async def get_sms(self, country: str, number: str):
        """Получает последние 3 SMS для указанного номера."""
        async with aiohttp.ClientSession() as session:
            sms_list = await fetch_last_3_sms(session, country, number, self.headers, self.urls)
            return sms_list

    def get_fresh_countries(self):
        """Возвращает страны, у которых есть кэшированные номера."""
        return [country for country, numbers in self.number_cache.items() if numbers]

    async def fetch_data(session, url, headers):
        """
        Выполняет асинхронный запрос и возвращает JSON-ответ.
        """
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                logger.debug(f"{response.json()}")
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Helper: Failed to fetch data from {url}: {e}")
            return {}

