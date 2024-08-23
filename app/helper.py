import re
import aiohttp
import logging

def is_relevant_number(age):
    """
    Проверяет, является ли номер "свежим" на основе времени его последнего использования.
    """
    day_match = re.match(r"(\d+) days? ago", age)
    hour_match = re.match(r"(\d+) hours? ago", age)
    week_match = re.match(r"1 week ago", age)
    
    if day_match:
        days = int(day_match.group(1))
        return days <= 7
    elif hour_match:
        hours = int(hour_match.group(1))
        return hours <= 168  # 7 дней в часах
    elif week_match:
        return True  # Допускаем 1 неделю как "свежий" номер
    else:
        return False

async def fetch_data(session, url, headers):
    """
    Выполняет асинхронный запрос и возвращает JSON-ответ.
    """
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return {}

def sort_numbers(fresh_numbers):
    """
    Сортирует номера по "свежести", выделяя сначала самые актуальные.
    """
    most_recent = [num for num in fresh_numbers if num["age"] in ["1 day ago", "12 hours ago"]]
    older_numbers = [num for num in fresh_numbers if num["age"] not in ["1 day ago", "12 hours ago"]]
    older_numbers.sort(key=lambda x: x["age"])
    return most_recent + older_numbers

def extract_code_from_text(text):
    """
    Извлекает код (4-6 цифр) из текста сообщения, если он есть.
    """
    match = re.search(r'\b(\d{4,6})\b', text)
    return match.group(1) if match else None
