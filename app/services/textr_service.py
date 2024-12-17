# app/services/textr_service.py
import logging
from bs4 import BeautifulSoup
from fastapi import requests

from app.core.sms_provider import SmsProvider
from app.helpers.constants import AGE_MAP


class TextrService(SmsProvider):
    def __init__(self, config):
        # Your existing initialization code
        self.config = config
        self.headers = config.headers
        self.url = self.config.urls.get('url')  # Fetch the correct URL key
        logging.info("Services: Textr initialized with configuration.")

    def fetch_numbers(self):
        # Your existing fetch_numbers implementation
        response = requests.get(self.url, headers=self.headers)
        logging.info(f"Fetching numbers from URL: {self.url}")
        
        if response.status_code != 200:
            logging.error(f"Failed to load the page. Status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        numbers = []
        age_id = 10  # Используем ID 10 для "1* week ago"

        # Получаем все ссылки на страницы номеров
        links = soup.find_all('a', class_='button-textr secondary w-button')
        
        for link in links:
            href = link.get('href')
            if href:
                number = self.extract_number_from_url(href)
                country_name = self.get_country_name_from_link(href)

                numbers.append({
                    'country': country_name,
                    'full_number': number,
                    'number': number[-10:],  # Выводим последние 10 цифр номера
                    'age': AGE_MAP[age_id]["description"]
                })

        if not numbers:
            logging.error(f"No numbers found.")
        
        return numbers

    def fetch_sms(self, session, country, number):
        # Placeholder implementation
        logging.warning(f"fetch_sms is not supported for TextrService.")
        return []

    def get_supported_countries(self):
        # Placeholder implementation if TextrService does not need to handle multiple countries
        return ["netherlands", "united_kingdom", "canada", "usa", "australia", "sweden"]

    def extract_number_from_url(self, url):
        logging.info(f"Extracting number from URL: {url}")
        return url.split('-')[-1]

    def get_country_name_from_link(self, link):
        if "netherlands" in link:
            return "netherlands"
        elif "uk" in link or "united-kingdom" in link:
            return "united_kingdom"
        elif "canada" in link:
            return "canada"
        elif "usa" in link or "united-states" in link:
            return "united_states"
        elif "australia" in link:
            return "australia"
        elif "sweden" in link:
            return "sweden"
        else:
            return "unknown"