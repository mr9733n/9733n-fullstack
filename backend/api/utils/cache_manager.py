# app/utils/cache_manager.py
import aiohttp
from datetime import timedelta
import asyncio
import ssl
from linecache import cache
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from backend.api.utils.logger import logger

# Глобальный кэш для хранения данных
cache = {"data": {}, "last_update": None}


class CacheManager:
    def __init__(self, service_config, onlinesim_helper, cache_lifetime=timedelta(hours=12)):
        self.logging = logger
        self.service_config = service_config
        self.number_cache = {}
        self.last_cache_update = None
        self.cache_lifetime = cache_lifetime
        self.countries = self.service_config.countries
        self.onlinesim_helper = onlinesim_helper  # Инициализация

    def cache_numbers(self):
        # Example of using self.countries
        for country in self.countries:
            # Perform caching logic here
            pass

    async def fetch_numbers_with_retry(self, country, max_retries=2, retry_delay=30):
        retries = 0
        async with aiohttp.ClientSession() as session:
            while retries < max_retries:
                try:
                    numbers = await self.onlinesim_helper.fetch_numbers(session, country)
                    self.logging.debug(f"Fetched numbers for {country}: {numbers}")
                    if numbers:
                        return numbers
                    else:
                        self.logging.warning(f"No numbers fetched for {country}.")
                        return None
                except Exception as e:
                    self.logging.error(f"Error fetching numbers for {country}: {e}")
                retries += 1
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        self.logging.error(f"Failed to fetch numbers for {country} after {max_retries} retries.")
        return None

    async def fetch_numbers_for_country(self, session, country):
        try:
            self.logging.info(f"Utils: Fetching numbers for country: {country}")
            fresh_numbers = await self.onlinesim_helper.fetch_numbers(session, country)
            self.logging.debug(f"Fetched numbers before sorting: {fresh_numbers}")

            if fresh_numbers:
                sorted_numbers = self.onlinesim_helper.sort_numbers(fresh_numbers)
                self.logging.debug(f"Sorted numbers: {sorted_numbers}")

            # Обновляем глобальный кэш
            cache["data"][country] = sorted_numbers
            cache["last_update"] = asyncio.get_event_loop().time()
            self.logging.info(f"Utils: Updated cache for {country}")
        except aiohttp.ClientTimeout:
            self.logging.error(f"Utils: Timeout while fetching numbers for country: {country}.")
        except ssl.SSLError:
            self.logging.error(f"Utils: SSL error while fetching numbers for country: {country}.")
        except Exception as e:
            self.logging.error(f"Utils: Unexpected error fetching numbers for country {country}: {e}")

    def get_cached_numbers(self, country):
        cached_numbers = self.number_cache.get(country, [])
        return self.onlinesim_helper.sort_numbers(cached_numbers)

    async def fetch_data(session, url, headers):
        """
        Выполняет асинхронный запрос и возвращает JSON-ответ.
        """
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Utils: Failed to fetch data from {url}: {e}")
            return {}
        
    def get_fresh_countries(self):
        """Возвращает список стран с актуальными номерами из кэша."""
        return [country for country, numbers in cache["data"].items() if numbers]

