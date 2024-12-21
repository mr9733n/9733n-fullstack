# app/libs/onlinesim_lib.py
import re
import aiohttp
from app.utils.logger import logger
logging = logger

def is_relevant_number(age, show_all):
    day_match = re.match(r"(\d+) days? ago", age)
    hour_match = re.match(r"(\d+) hours? ago", age)
    week_match = re.match(r"(\d+) week ago", age)

    if day_match:
        days = int(day_match.group(1))
        return days <= 7  # Оставляем только те, что не старше недели
    elif hour_match:
        hours = int(hour_match.group(1))
        return hours <= 168  # 168 часов = 7 дней
    elif week_match:
        week = int(week_match.group(1))
        return week <= 0 and not show_all
    else:
        return False

async def fetch_data(session, url, headers):
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch data from {url}: {e}")
        return {}


async def fetch_fresh_numbers(session, country, headers, urls, show_all=False):
    url = urls["fetch_numbers_url"].format(country=country)
    data = await fetch_data(session, url, headers)
    fresh_numbers = [
        {
            "country": country,
            "full_number": number_info["full_number"],
            "number": number_info["number"],
            "age": number_info["data_humans"]
        }
        for number_info in data.get("numbers", [])
        if is_relevant_number(number_info["data_humans"], show_all=show_all)
    ]
    logger.info(f"Fetched {len(fresh_numbers)} fresh numbers for {country}.")
    return fresh_numbers


async def fetch_last_3_sms(session, country, number, headers, urls):
    url = urls["fetch_sms_url"].format(country=country, number=number)
    data = await fetch_data(session, url, headers)
    messages_data = data.get("messages", {}).get("data", [])
    logger.info(f"Fetched {len(messages_data)} SMS for number {number} in {country}.")

    return [
        {
            "id": msg["id"],
            "text": msg.get("text", "No text available").strip(),
            "time": msg.get("created_at", "No timestamp available")
        }
        for msg in messages_data[:3]
        if msg.get("text", "").strip()
    ]


def sort_numbers(fresh_numbers):
    most_recent = [num for num in fresh_numbers if num["age"] in ["1 day ago", "12 hours ago"]]
    older_numbers = [num for num in fresh_numbers if num["age"] not in ["1 day ago", "12 hours ago"]]
    older_numbers.sort(key=lambda x: x["age"])
    return most_recent + older_numbers


def extract_code_from_text(text):
    match = re.search(r'\b(\d{4,6})\b', text)
    return match.group(1) if match else None



