from abc import ABC, abstractmethod
import aiohttp
import logging
from app.models.service_config import ServiceConfig


class SmsProvider(ABC):
    """Абстрактный базовый класс для всех сервисов получения номеров и SMS."""

    def __init__(self, config: ServiceConfig):
        """Инициализация конфигурации сервиса."""
        self.config = config
        self.base_url = config.urls.get("base_url", "")
        self.api_key = config.headers.get("Authorization", "")
        self.headers = config.headers
        self.fetch_numbers_url = config.urls.get("fetch_numbers_url", "")
        self.fetch_sms_url = config.urls.get("fetch_sms_url", "")
        logging.info(f"SmsProvider initialized with base_url: {self.base_url}")

    async def fetch_numbers(self, country: str):
        """Метод для получения номеров."""
        pass

    async def fetch_sms(self, country: str, number: str):
        """Метод для получения SMS."""
        pass

class ConfigurableSmsProvider(SmsProvider):
    def __init__(self, config: dict):
        self.fetch_numbers_url = config["urls"].get("fetch_numbers_url", "")
        self.fetch_sms_url = config["urls"].get("fetch_sms_url", "")
        self.headers = config.get("headers", {})

    async def fetch_numbers(self, country: str):
        url = self.fetch_numbers_url.format(country=country)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                return await response.json()

    async def fetch_sms(self, country: str, number: str):
        url = self.fetch_sms_url.format(country=country, number=number)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                return await response.json()

    def get_supported_countries(self):
        return self.config.countries