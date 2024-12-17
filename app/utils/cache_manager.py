# app/utils/cache_manager.py
import logging
import asyncio
import ssl
import aiohttp
from datetime import timedelta
from app.helpers.onlinesim_helper import onlinesim_helper_sort_numbers
from app.models import service_config

class CacheManager:
    def __init__(self, service_config, cache_lifetime=timedelta(hours=1)):
        self.service_config = service_config
        self.number_cache = {}
        self.last_cache_update = None
        self.cache_lifetime = cache_lifetime
        self.countries = self.service_config.countries

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
                    numbers = await self.online_sim_service.fetch_numbers(session, country)
                    logging.debug(f"Fetched numbers for {country}: {numbers}")
                    if numbers:
                        return numbers
                    else:
                        logging.warning(f"No numbers fetched for {country}.")
                        return None
                except Exception as e:
                    logging.error(f"Error fetching numbers for {country}: {e}")
                retries += 1
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        logging.error(f"Failed to fetch numbers for {country} after {max_retries} retries.")
        return None

    async def fetch_numbers_for_country(self, session, country):
        try:
            logging.info(f"Utils: Fetching numbers for country: {country}")
            fresh_numbers = await self.online_sim_service.fetch_numbers(session, country)
            logging.debug(f"Fetched numbers before sorting: {fresh_numbers}")

            if not fresh_numbers:
                logging.debug(f"Utils: Skipping country {country} due to empty response.")
                return

            if isinstance(fresh_numbers, list) and all(isinstance(item, dict) for item in fresh_numbers):
                sorted_numbers = onlinesim_helper_sort_numbers(fresh_numbers)
                logging.debug(f"Sorted numbers: {sorted_numbers}")
                self.number_cache[country] = sorted_numbers
                logging.info(f"Utils: Cached numbers for {country}: {sorted_numbers}")
            else:
                logging.warning(f"Unexpected data format for country {country}: {fresh_numbers}")
        except aiohttp.ClientTimeout:
            logging.error(f"Utils: Timeout while fetching numbers for country: {country}.")
        except ssl.SSLError:
            logging.error(f"Utils: SSL error while fetching numbers for country: {country}.")
        except Exception as e:
            logging.error(f"Utils: Unexpected error fetching numbers for country {country}: {e}")

    def get_cached_numbers(self, country):
        cached_numbers = self.number_cache.get(country, [])
        return onlinesim_helper_sort_numbers(cached_numbers) 

    async def preload_numbers(self):
        logging.info("Utils: Starting initial number preloading (1-minute delay).")
        await asyncio.sleep(6)  # 1 minute delay before starting preload
        async with aiohttp.ClientSession() as session:
            for country in self.countries:
                await self.fetch_numbers_for_country(session, country)


    async def fetch_data(session, url, headers):
        """
        Выполняет асинхронный запрос и возвращает JSON-ответ.
        """
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"Utils: Failed to fetch data from {url}: {e}")
            return {}
        

