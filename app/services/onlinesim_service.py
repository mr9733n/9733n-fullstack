# app/services/onlinesim_service.py
import aiohttp
import logging
from app.core.sms_provider import SmsProvider
from app.helpers.common_helper import CommonHelper
from app.core.sms_provider import ServiceConfig  # Импортируем ServiceConfig

class OnlineSimService(SmsProvider):
    def __init__(self, config: ServiceConfig):
        self.common_helper = CommonHelper(config)
        self.headers = config.headers
        self.urls = config.urls
        self.base_url = self.urls.get("base_url", "")
        self.fetch_numbers_url = self.urls.get("fetch_numbers_url", "")
        self.fetch_sms_url = self.urls.get("fetch_sms_url", "")
        self.api_key = self.headers.get("Authorization", "")
        logging.info("Services: OnlineSimService initialized with configuration.")

    async def fetch_numbers(self, country: str):
        url = self.fetch_numbers_url.format(country=country)
        logging.info(f"Fetching numbers for country: {country} from URL: {url}")
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logging.info(f"Services: Successfully fetched numbers for country: {country}")
                    return [
                        {
                            "country": country,
                            "full_number": number_info["full_number"],
                            "number": number_info["number"],
                            "age": number_info["data_humans"],
                            "age_id": self.common_helper.get_age_id_by_description(number_info["data_humans"])
                        }
                        for number_info in data.get("numbers", [])
                    ]
        except aiohttp.ClientError as e:
            logging.error(f"Services: Error fetching numbers for country: {country} - {e}")
            return []

    async def fetch_sms(self, country: str, number: str):
        url = self.fetch_sms_url.format(country=country, number=number)
        logging.info(f"Fetching SMS for number: {number} in country: {country} from URL: {url}")
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logging.info(f"Services: Successfully fetched SMS for number: {number} in country: {country}")
                    return data.get("messages", {}).get("data", [])
        except aiohttp.ClientError as e:
            logging.error(f"Services: Error fetching SMS for number: {number} in country: {country} - {e}")
            return []

    def get_supported_countries(self):
        return self.config.countries

    def get_number_data(self):
        age_id = 13  # Например, 1 day ago
        age_description = self.common_helper.get_age_description_by_id(age_id)

        return {
            "number": "79291234567",
            "age": age_description,
            "age_id": age_id
        }
