# app/utils/cache_manager.py
from app.core.sms_provider import SmsProvider

class AnotherService(SmsProvider):
    def __init__(self, config):
        self.config = config
        # Test Mock service

    async def fetch_numbers(self, session, country):
        # Логика получения номеров для другого сайта
        pass

    async def fetch_sms(self, session, country, number):
        # Логика получения SMS для другого сайта
        pass

    def get_supported_countries(self):
        # Возвращаем список поддерживаемых стран для этого сервиса
        return ["country1", "country2"]
