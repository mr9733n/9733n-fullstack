import aiohttp
import logging
from app.services.base_service import BaseService
import json

class OnlineSimService(BaseService):
    def __init__(self, config):
        self.config = config
        self.headers = config['headers']
        self.urls = config['urls']
        logging.info("OnlineSimService initialized with configuration.")

    async def fetch_numbers(self, session, country):
        url = self.urls['fetch_numbers_url'].format(country=country)
        logging.info(f"Fetching numbers for country: {country} from URL: {url}")
        try:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                logging.info(f"Successfully fetched numbers for country: {country}")
                return [
                    {
                        "country": country,
                        "full_number": number_info["full_number"],
                        "number": number_info["number"],
                        "age": number_info["data_humans"]
                    }
                    for number_info in data.get("numbers", [])
                ]
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching numbers for country: {country} - {e}")
            return []

    async def fetch_sms(self, session, country, number):
        url = self.urls['fetch_sms_url'].format(country=country, number=number)
        logging.info(f"Fetching SMS for number: {number} in country: {country} from URL: {url}")
        try:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                logging.info(f"Successfully fetched SMS for number: {number} in country: {country}")
                return data.get("messages", {}).get("data", [])
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching SMS for number: {number} in country: {country} - {e}")
            return []

    def get_supported_countries(self):
        logging.info("Fetching supported countries.")
        return self.config['countries']
