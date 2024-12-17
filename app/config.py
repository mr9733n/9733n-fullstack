from pydantic import BaseModel, ValidationError
import json
import os
import logging
from typing import List, Dict
from app.helpers.common_helper import validate_countries

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MainConfig(BaseModel):
    title: str
    description: str
    version: str
    author: str
    services: List[str]
    cache_for_fresh_numbers: List[str]
    exclude_from_cache: List[str]  # Добавлено это поле

class ServiceConfig(BaseModel):
    countries: List[str]
    headers: Dict[str, str]
    urls: Dict[str, str]

# Функции загрузки конфигураций
def load_main_config() -> MainConfig:
    try:
        config_path = os.path.abspath(os.path.join(BASE_DIR, "..", "config", "main_config.json"))
        logging.debug(config_path)
        with open(config_path, "r") as main_config_file:
            config_data = json.load(main_config_file)
            return MainConfig(**config_data)
    except (FileNotFoundError, ValidationError) as e:
        logging.error(f"Failed to load main configuration: {e}")
        raise

def load_service_config(service_name) -> ServiceConfig:

    try:
        config_path = os.path.abspath(os.path.join(BASE_DIR, "..", "config", f"{service_name}_config.json"))
        logging.debug(config_path)
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            countries = validate_countries(config_data.get('countries', []))
            config_data['countries'] = countries
            return ServiceConfig(**config_data)
    except (FileNotFoundError, ValidationError) as e:
        logging.error(f"Failed to load service configuration from {config_path}: {e}")
        raise


def load_all_service_configs(main_config: MainConfig) -> dict:
    service_configs = {}
    for service_name in main_config.services:
        service_configs[service_name] = load_service_config(service_name)
    return service_configs
