import json
import logging
from app.helpers.common_helper import validate_countries

API_CONFIG = {
    "title": "Online SMS API",
    "description": "API for fetching and monitoring SMS messages via various services.",
    "version": "1.2.0",
    "autor": "9733n"
}

def load_config(service_name):
    config_path = f"config/{service_name}_config.json"
    
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file) 
            countries = validate_countries(config.get('countries', []))  
            config['countries'] = countries
            return config
    except Exception as e:
        logging.error(f"Config: Failed to load service configuration from {config_path}: {e}")
        raise

def load_main_config():
    try:
        with open('config/main_config.json', 'r') as main_config_file:
            return json.load(main_config_file)
    except Exception as e:
        logging.error(f"Config: Failed to load main configuration: {e}")
        raise
