from app.services.base_service import BaseService

class AnotherService(BaseService):
    def __init__(self, config):
        self.config = config
        # Логика инициализации для другого сайта

    async def fetch_numbers(self, session, country):
        # Логика получения номеров для другого сайта
        pass

    async def fetch_sms(self, session, country, number):
        # Логика получения SMS для другого сайта
        pass

    def get_supported_countries(self):
        # Возвращаем список поддерживаемых стран для этого сервиса
        return ["country1", "country2"]
