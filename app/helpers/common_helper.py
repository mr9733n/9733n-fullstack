# app/helpers/common_helper.py
import re
import aiohttp
import logging
from app.helpers.onlinesim_helper import OnlinesimHelper
from app.models.service_config import ServiceConfig
from app.helpers.constants import AGE_MAP

class CommonHelper:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def get_age_days_by_id(age_id):
        """
        Возвращает количество дней на основе идентификатора age_id.
        """
        return AGE_MAP.get(age_id, {}).get("days", None)

    @staticmethod
    def get_age_description_by_id(age_id):
        """
        Возвращает текстовое описание возраста на основе идентификатора age_id.
        """
        return AGE_MAP.get(age_id, {}).get("description", "Unknown age")

    @staticmethod
    def get_age_id_by_description(description):
        """
        Возвращает идентификатор возраста на основе текстового описания.
        """
        for age_id, age_data in AGE_MAP.items():
            if age_data.get("description") == description:
                return age_id
        return None

    def get_supported_countries(self):
        return self.config.countries

    def extract_code_from_text(text):
        """
        Извлекает код (4-6 цифр) из текста сообщения, если он есть.
        """
        match = re.search(r'\b(\d{4,6})\b', text)
        return match.group(1) if match else None

    def get_fresh_numbers(numbers, max_age_days=7):
        """
        Фильтрует номера, не старше `max_age_days` на основе форматов "1 day ago", "12 hours ago" и т.д.
        """
        onlinesim_helper = OnlinesimHelper()
        fresh_numbers = [num for num in numbers if onlinesim_helper.is_relevant_number(num["age"])]
        return fresh_numbers

    def validate_countries(self, countries):
        """
        Проверяет, что:
        - Список стран является списком и содержит не более 200 элементов.
        - Названия стран не содержат цифр и других недопустимых символов.
        """
        max_countries = 200

        # Проверяем, что список не пустой и содержит не более 200 стран
        if not isinstance(countries, list) or len(countries) > max_countries:
            raise ValueError("The list of countries should be a list with no more than 200 items.")

        # Проверяем, что каждое название страны - строка и не содержит цифр
        for country in countries:
            if not isinstance(country, str) or any(char.isdigit() for char in country):
                raise ValueError(f"Invalid country name detected: '{country}'. Country names should not contain numbers.")

        logging.debug(f"Helper: Validated countries: {countries}")
        return [country for country in countries if isinstance(country, str) and len(country) > 0]

    async def fetch_data(session, url, headers):
        """
        Выполняет асинхронный запрос и возвращает JSON-ответ.
        """
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.даjson()
        except aiohttp.ClientError as e:
            logging.error(f"Helper: Failed to fetch data from {url}: {e}")
            return {}



