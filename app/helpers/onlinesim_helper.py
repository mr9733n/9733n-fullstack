# app/helpers/onlinesim_helper.py
import logging
from app.helpers.constants import AGE_MAP

class OnlinesimHelper:
    def __init__(self, max_days=7):
        self.max_days = max_days

    def is_relevant_number(self, age):
        """
        Проверяет, является ли номер "свежим" на основе времени его последнего использования.
        """
        days = AGE_MAP.get(age)
        if days is not None:
            return days <= self.max_days
        else:
            return False

    def sort_numbers(self, fresh_numbers):
        """
        Сортирует номера по их возрасту, начиная с самых свежих.
        """
        if not isinstance(fresh_numbers, list):
            logging.error(f"Unexpected data format: {fresh_numbers}")
            return []

        def sort_key(item):
            return AGE_MAP.get(item.get('age'), float('inf'))

        return sorted(fresh_numbers, key=sort_key)
