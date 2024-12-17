# app/core/sms_provider_factory.py
import logging
from app.services.onlinesim_service import OnlineSimService
from app.core.sms_provider import SmsProvider

class SmsProviderFactory:
    def __init__(self):
        self.providers = {
            "onlinesim": OnlineSimService  # Здесь возвращается класс
    }
    def register_provider(self, provider_name: str, provider_instance: SmsProvider):
        """Регистрирует нового провайдера."""
        self.providers[provider_name] = provider_instance

    def get_provider(self, provider_name: str, *args, **kwargs) -> SmsProvider:
        """Возвращает экземпляр провайдера по его имени."""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        logging.debug(f"provider: {provider_name}")
        provider_class = self.providers[provider_name]
        return provider_class(*args, **kwargs)  # Возвращаем экземпляр
