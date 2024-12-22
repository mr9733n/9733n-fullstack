import requests
from bs4 import BeautifulSoup
import random

from requests.adapters import HTTPAdapter
from unidecode import unidecode
import os
import sys

from urllib3 import Retry

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from backend.api.utils.logger import logger

class JapaneseNameGenerator:
    def __init__(self, num_names=1, sex="male", firstname_rarity="very_rare", lastname_rarity="very_rare"):
        self.num_names = num_names
        self.sex = sex
        self.firstname_rarity = firstname_rarity
        self.lastname_rarity = lastname_rarity
        self.logger = logger
        self.logger.info("Random Japanese names started..")

    def generate_names(self):
        url = self.build_url()
        response = self.send_request(url)

        if response:
            names_list = self.parse_response(response)
            self.logger.info("List of name was received.")
            if not names_list:
                self.logger.warning("There was no names in response.")
                return []

            random_names = random.sample(names_list, min(self.num_names, len(names_list)))
            self.logger.info("All done well.")
            return random_names

        self.logger.error("An error occurred while executing the request.")
        return []

    def build_url(self):
        base_url = "https://namegen.jp/en"
        params = {
            "country": "japan",
            "sex": self.sex,
            "firstname": "",
            "firstname_cond": "fukumu",
            "firstname_rarity": self.firstname_rarity,
            "lastname": "",
            "lastname_cond": "fukumu",
            "lastname_rarity": self.lastname_rarity,
        }
        self.logger.info("URL was builded.")
        return f"{base_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"

    def send_request(self, url):
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            self.logger.info("Response 200 OK")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred while executing the request. {e}")
            return None

    def parse_response(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        name_elements = soup.find_all("td", class_="name")
        self.logger.info("Names parsed well.")
        return [unidecode(name.text.strip()) for name in name_elements]

# Test usage
if __name__ == "__main__":

    name_generator = JapaneseNameGenerator(num_names=3, sex="female", firstname_rarity="common", lastname_rarity="rare")
    random_names = name_generator.generate_names()
    if random_names:
        name_generator.logger.info("Random Japanese names result:")
        for i, name in enumerate(random_names, 1):
            name_generator.logger.info(name)