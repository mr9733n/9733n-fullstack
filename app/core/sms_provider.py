# app/core/sms_provider.py
from abc import ABC, abstractmethod
import aiohttp

class SmsProvider(ABC):
    """Абстрактный базовый класс для всех сервисов получения номеров и SMS."""

    @abstractmethod
    async def fetch_numbers(self):
        """Метод для получения списка номеров."""
        pass

    @abstractmethod
    async def fetch_sms(self, number):
        """Метод для получения последних SMS для заданного номера."""
        pass

    @abstractmethod
    def get_supported_countries(self):
        """Метод для получения списка поддерживаемых стран."""
        pass

class ExampleSmsProvider(SmsProvider):
    async def fetch_numbers(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.example.com/numbers") as response:
                return await response.json()

    async def fetch_sms(self, number):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com/sms/{number}") as response:
                return await response.json()

    def get_supported_countries(self):
        return ["US", "UK"]
