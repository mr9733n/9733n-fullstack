import requests
from bs4 import BeautifulSoup
import random
import os
from unidecode import unidecode
import logging

class JapaneseNameGenerator:
    def __init__(self, num_names=1, save_to_file=False, params=None, log_to_file=False):
        self.num_names = num_names
        self.save_to_file = save_to_file
        self.params = params or {}
        self.log_to_file = log_to_file
        self.temp_dir = 'temp' 
        self.log_dir = 'logs'  
        self.output_dir = 'output'  
       
        self.logger = self.setup_logger()
        self.logger.info("Random Japanese names started..")

    def setup_logger(self):
        logger = logging.getLogger("JapaneseNameGenerator")
        if not logger.handlers:  # Check if handlers are already added
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

            # Add a handler for console output
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)

            # If log_to_file=True, add a handler for file output
            if self.log_to_file:
                if not os.path.exists(self.log_dir):
                    os.makedirs(self.log_dir)
                log_file_path = os.path.join(self.log_dir, "japanese_name_generator_log.txt")
                fh = logging.FileHandler(log_file_path)
                fh.setFormatter(formatter)
                logger.addHandler(fh)

        return logger

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

            if self.save_to_file:
                self.save_names_to_file(names_list)
                self.logger.info("Names was successfully saved.")

            # Log generated names
            self.logger.info("Generated names:")
            for name in random_names:
                self.logger.info(name)

            self.logger.info("All done well.")
            return random_names

        self.logger.error("An error occurred while executing the request.")
        return []

    def build_url(self):
        base_url = "https://namegen.jp/en"
        params = {
            "country": "japan",
            "sex": "male",
            "firstname": "",
            "firstname_cond": "fukumu",
            "firstname_rarity": "very_rare",
            "lastname": "",
            "lastname_cond": "fukumu",
            "lastname_rarity": "very_rare",
        }
        params.update(self.params)
        self.logger.info("URL was builded.")
        return f"{base_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"

    def send_request(self, url):
        try:
            response = requests.get(url)
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

    def save_names_to_file(self, names_list):
        random_filename = f"japanese_names_{random.randint(1, 1000)}.txt"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        file_path = os.path.join(self.output_dir, random_filename)
        try:
            with open(file_path, "w", encoding="utf-8") as names_file:
                for name in names_list:
                    names_file.write(name + "\n")
                self.logger.info("File with names was saved well.")
        except IOError as e:
            self.logger.error(f"Error when saving names to a file: {e}")

# Test usage
if __name__ == "__main__":
    params = {
        "sex": "male",
    }

    name_generator = JapaneseNameGenerator(num_names=3, save_to_file=False, params=params, log_to_file=True)
    random_names = name_generator.generate_names()
    if random_names:
        name_generator.logger.info("Random Japanese names result:")
        for i, name in enumerate(random_names, 1):
            name_generator.logger.info(name)