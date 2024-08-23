import logging
import asyncio
import ssl
import aiohttp
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.onlinesim_service import OnlineSimService
from app.helper import is_relevant_number, sort_numbers

class CacheManager:
    def __init__(self, online_sim_service, cache_lifetime=timedelta(hours=1)):
        self.online_sim_service = online_sim_service
        self.countries = self.online_sim_service.get_supported_countries()
        self.number_cache = {}
        self.last_cache_update = None
        self.cache_lifetime = cache_lifetime

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

            # Проверяем, что данные являются списком словарей
            if isinstance(fresh_numbers, list) and all(isinstance(item, dict) for item in fresh_numbers):
                # Сортируем номера и сохраняем в кеш
                sorted_numbers = sort_numbers(fresh_numbers)
                logging.debug(f"Sorted numbers: {sorted_numbers}")
                self.number_cache[country] = sorted_numbers
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
        return sort_numbers(cached_numbers)  # Дополнительно сортируем перед возвратом

    async def preload_numbers(self):
        logging.info("Utils: Starting initial number preloading (1-minute delay).")
        await asyncio.sleep(6)  # Задержка для предварительной загрузки
        async with aiohttp.ClientSession() as session:
            for country in self.countries:
                await self.fetch_numbers_for_country(session, country)

@asynccontextmanager
async def app_lifecycle(app: FastAPI, cache_manager: CacheManager):
    logging.info("Utils: Starting preloading cache...")
    task = asyncio.create_task(cache_manager.preload_numbers())
    
    yield

    task.cancel()
    logging.info("Utils: Service stopped.")
