# app/helpers/onlinesim_helper.py
import logging
from app.helpers.constants import AGE_MAP
from app.models.service_config import ServiceConfig


def onlinesim_helper_is_relevant_number(age, max_days=7):
    """
    Проверяет, является ли номер "свежим" на основе времени его последнего использования.
    """
    days = AGE_MAP.get(age)
    if days is not None:
        return days <= max_days
    else:
        return False

def onlinesim_helper_sort_numbers(fresh_numbers):
    """
    Сортирует номера по их возрасту, начиная с самых свежих.
    """
    if not isinstance(fresh_numbers, list):
        logging.error(f"Unexpected data format: {fresh_numbers}")
        return []

    def sort_key(item):
        return AGE_MAP.get(item.get('age'), float('inf'))

    return sorted(fresh_numbers, key=sort_key)

