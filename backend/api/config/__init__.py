import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config(config_filename):
    config_path = os.path.join(BASE_DIR, config_filename)
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)  # Возвращает словарь

# Загружаем конфиги
main_config = load_config("main_config.json")
onlinesim_config = load_config("onlinesim_config.json")
