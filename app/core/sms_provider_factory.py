from sms_provider import SmsProvider

class SmsProviderFactory:
    def __init__(self):
        self.providers = {}

    def register_provider(self, provider_name: str, provider_instance: SmsProvider):
        """
        Регистрирует нового провайдера.
        :param provider_name: Имя провайдера
        :param provider_instance: Экземпляр провайдера, реализующий SmsProvider
        """
        self.providers[provider_name] = provider_instance

    def get_provider(self, provider_name: str) -> SmsProvider:
        """
        Возвращает провайдера по его имени.
        :param provider_name: Имя провайдера
        :return: Экземпляр провайдера или None, если не найден
        """
        return self.providers.get(provider_name)
