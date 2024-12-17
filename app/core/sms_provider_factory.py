# app/core/sms_provider_factory.py
from sms_provider import SmsProvider

class SmsProviderFactory:
    def __init__(self):
        self.providers = {}

    def register_provider(self, provider_name: str, provider_instance: SmsProvider):
        """Регистрирует нового провайдера."""
        self.providers[provider_name] = provider_instance

    def get_provider(self, provider_name: str) -> SmsProvider:
        """Возвращает провайдера по его имени."""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        return self.providers[provider_name]
