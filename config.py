from pydantic import BaseModel, ValidationError
import json
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Функции загрузки конфигураций
def load_main_config():
    from app.models.main_config import MainConfig  # Импорт внутри функции
    try:
        config_path = os.path.abspath(os.path.join(BASE_DIR, "..", "config", "main_config.json"))
        logging.debug(config_path)
        with open(config_path, "r") as main_config_file:
            config_data = json.load(main_config_file)
            return MainConfig(**config_data)
    except (FileNotFoundError, ValidationError) as e:
        logging.error(f"Failed to load main configuration: {e}")
        raise


def load_service_config(service_name):
    from app.models.service_config import ServiceConfig  # Импорт модели
    from app.helpers.common_helper import CommonHelper  # Импорт класса CommonHelper

    try:
        # Путь к файлу конфигурации
        config_path = os.path.abspath(os.path.join(BASE_DIR, "..", "config", f"{service_name}_config.json"))
        logging.debug(config_path)

        # Чтение конфигурации
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)

            # Создание экземпляра CommonHelper
            helper = CommonHelper(config_data)
            countries = helper.validate_countries(config_data.get('countries', []))

            # Обновление данных конфигурации
            config_data['countries'] = countries

            # Возвращение ServiceConfig
            return ServiceConfig(**config_data)

    except (FileNotFoundError, ValidationError) as e:
        logging.error(f"Failed to load service configuration from {config_path}: {e}")
        raise


def load_all_service_configs(main_config):
    service_configs = {}
    for service_name in main_config.services:
        service_configs[service_name] = load_service_config(service_name)
    return service_configs

def initialize_providers(main_config):
    from app.services import OnlineSimService, TextrService  # Импорты здесь!
    from app.core.sms_provider_factory import SmsProviderFactory

    service_configs = load_all_service_configs(main_config)
    sms_provider_factory = SmsProviderFactory()
    logging.debug(f"Available providers: {SmsProviderFactory.__name__}")

    services = {}
    for service_name, service_config in service_configs.items():
        if service_name == "onlinesim":
            services[service_name] = OnlineSimService(service_config)
        elif service_name == "textr":
            services[service_name] = TextrService(service_config)
        sms_provider_factory.register_provider(service_name, services[service_name])

    return sms_provider_factory