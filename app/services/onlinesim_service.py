# app/services/onlinesim_service.py
import aiohttp
import asyncio
from app.libs.onlinesim_lib import fetch_fresh_numbers, fetch_last_3_sms, sort_numbers

from app.utils.logger import logger

BATCH_SIZE = 5  # Количество запросов в одном цикле
WAIT_TIME = 5  # Время ожидания между циклами в секундах


class OnlinesimService:
    def __init__(self, config):
        self.update_in_progress = False
        self.cache_update_task = None
        self.logging = logger
        self.headers = config["headers"]
        self.urls = config["urls"]
        self.countries = config["countries"]
        self.number_cache = {}  # Локальный кеш номеров
        self.logging.info("OnlinesimService initialized successfully.")

    async def update_cache(self):
        """Обновляет кэш номеров батчами."""
        if self.update_in_progress:
            self.logging.info("Cache update already in progress.")
            return

        self.update_in_progress = True
        try:
            async with aiohttp.ClientSession() as session:
                # Обрабатываем страны батчами
                for i in range(0, len(self.countries), BATCH_SIZE):
                    batch_countries = self.countries[i:i + BATCH_SIZE]

                    tasks = [
                        fetch_fresh_numbers(session, country, self.headers, self.urls, show_all=False)
                        for country in batch_countries
                    ]

                    results = await asyncio.gather(*tasks)
                    for country, numbers in zip(batch_countries, results):
                        if numbers:
                            self.number_cache[country] = sort_numbers(numbers)

                    self.logging.info(f"Cache updated for batch: {batch_countries}")

                    if i + BATCH_SIZE < len(self.countries):
                        self.logging.info(f"Waiting {WAIT_TIME} seconds before next batch...")
                        await asyncio.sleep(WAIT_TIME)

        except Exception as e:
            self.logging.exception(f"Error updating cache: {e}")

        finally:
            self.update_in_progress = False

    async def get_cache(self):
        """Возвращает актуальный кеш."""
        if not self.number_cache and not self.update_in_progress:
            await self.update_cache()
        return self.number_cache

    async def get_fresh_countries(self):
        """Возвращает страны с актуальными номерами из кэша."""
        if not self.number_cache:
            self.logging.info("Cache is empty. Triggering update...")
            asyncio.create_task(self.update_cache())
        return [{"country": country, "numbers": numbers} for country, numbers in self.number_cache.items()]

    async def update_country_cache(self, country: str):
        """Обновляет кэш для указанной страны."""
        try:
            async with aiohttp.ClientSession() as session:
                fresh_numbers = await fetch_fresh_numbers(session, country, self.headers, self.urls, show_all=True)

                if fresh_numbers:
                    self.number_cache[country] = sort_numbers(fresh_numbers)
                    self.logging.info(f"Cache updated for country: {country}")
                else:
                    self.logging.warning(f"No numbers fetched for country: {country}")
        except Exception as e:
            self.logging.exception(f"Error updating cache for country {country}: {e}")

    async def get_numbers(self, country: str):
        """Fetch numbers for a specific country from cache or update it."""
        if country not in self.number_cache:
            self.logging.info(f"Cache miss for country: {country}. Updating cache...")
            await self.update_country_cache(country)
        return self.number_cache.get(country, [])

    async def get_sms(self, country: str, number: str):
        """Получает последние 3 SMS для указанного номера."""
        async with aiohttp.ClientSession() as session:
            sms_list = await fetch_last_3_sms(session, country, number, self.headers, self.urls)
            return sms_list



