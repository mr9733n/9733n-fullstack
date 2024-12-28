import os
from pathlib import Path
import httpx
import logging
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

class OnlineSimAPIInterface:
    def __init__(self):
        api_host = os.getenv("API_HOST", "http://127.0.0.1:6066")
        self.api_urls = {
            "countries": f"{api_host}/numbers/countries",
            "numbers": f"{api_host}/numbers/{{country}}",
            "sms": f"{api_host}/numbers/{{country}}/{{number}}/sms",
            "update": f"{api_host}/numbers/update"
        }
        self.logger = logging.getLogger("OnlineSimAPIInterface")
        logging.basicConfig(level=logging.DEBUG)

    async def fetch_countries(self):
        """
        Fetch the list of available countries.
        """
        try:
            async with httpx.AsyncClient() as client:
                self.logger.debug(f"Fetching countries from {self.api_urls['countries']}")
                response = await client.get(self.api_urls["countries"], timeout=10)
                response.raise_for_status()
                data = response.json()
                self.logger.debug(f"Countries response: {data}")
                return data.get("countries", [])
        except httpx.RequestError as e:
            self.logger.error(f"Error fetching countries: {e}")
            return []

    async def update_cache(self):
        """
        Trigger the API to update/reset its cache.
        """
        try:
            async with httpx.AsyncClient() as client:
                self.logger.debug(f"Triggering cache update via {self.api_urls['update']}")
                response = await client.get(self.api_urls["update"], timeout=10)
                response.raise_for_status()
                self.logger.debug("Cache update successful.")
                return {"status": "success", "message": "Cache updated successfully."}
        except httpx.RequestError as e:
            self.logger.error(f"Error updating cache: {e}")
            return {"status": "error", "message": "Failed to update cache."}


    async def fetch_numbers(self, country):
        """
        Fetch the list of numbers for a specific country.
        :param country: Country code or name
        """
        try:
            url = self.api_urls["numbers"].format(country=country)  # Corrected key
            async with httpx.AsyncClient() as client:
                self.logger.debug(f"Fetching numbers for country {country} from {url}")
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                self.logger.debug(f"Numbers response for {country}: {data}")
                return data.get("numbers", [])  # Adjust to expected structure in response
        except httpx.RequestError as e:
            self.logger.error(f"Error fetching numbers for {country}: {e}")
            return []

    async def fetch_sms(self, country, number):
        """
        Fetch SMS messages for a specific number in a country.
        :param country: Country code or name
        :param number: Phone number
        """
        try:
            url = self.api_urls["sms"].format(country=country, number=number)
            async with httpx.AsyncClient() as client:
                self.logger.debug(f"Fetching SMS for number {number} in country {country} from {url}")
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                self.logger.debug(f"SMS response for {country} {number}: {data}")
                return data.get("sms", [])
        except httpx.RequestError as e:
            self.logger.error(f"Error fetching SMS for {number} in {country}: {e}")
            return []

