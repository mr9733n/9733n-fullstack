import os
from pathlib import Path

import httpx
import logging

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

class JapaneseNameGenerator:
    def __init__(self):
        api_host = os.getenv("API_HOST", "http://127.0.0.1:6066")
        generate_name_route = os.getenv("GENERATE_NAME_ROUTE", "/rna/generate/names")
        self.api_url = f"{api_host}{generate_name_route}"

        self.logger = logging.getLogger("JapaneseNameGenerator")
        logging.basicConfig(level=logging.DEBUG)

    async def generate_names(self, num_names=1, sex="male", firstname_rarity="very_rare", lastname_rarity="very_rare"):
        """
        Запрос к API для генерации японских имен.

        :param num_names: Количество имен
        :param sex: Пол имен (male или female)
        :param firstname_rarity: Редкость имени
        :param lastname_rarity: Редкость фамилии
        :return: Список имен или пустой список в случае ошибки
        """
        params = {
            "num_names": num_names,
            "sex": sex,
            "firstname_rarity": firstname_rarity,
            "lastname_rarity": lastname_rarity
        }
        try:
            async with httpx.AsyncClient() as client:
                self.logger.debug(f"Sending request to {self.api_url} with params: {params}")
                response = await client.get(self.api_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                self.logger.debug(f"Response received: {data}")
                return data.get("names", [])
        except httpx.RequestError as e:
            self.logger.error(f"Error fetching names from backend API: {e}")
            return []
