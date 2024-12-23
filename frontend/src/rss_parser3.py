import os
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import session

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)
RSS_FEED_URL = os.getenv("RSS_FEED_URL", "http://localhost")

# Список полей, которые вы хотите извлечь из каждой записи
fields_to_extract = [
    "id", "link", "published", "summary", "tags", "title", "description"
]


def get_rss_url(url=None):
    if url:
        session['rss_url'] = url
    return session.get('rss_url', RSS_FEED_URL)

# Получите данные из ленты RSS
def get_rss_feed(url):
    feed = feedparser.parse(url)

    if feed.bozo:
        error_message = f"Error parsing feed: {feed.bozo_exception}"
        print(error_message)
        return {"error": error_message}  # Возвращаем словарь с ошибкой

    parsed_feed = []
    for entry in feed.entries:
        parsed_entry = {}
        for field in fields_to_extract:
            if hasattr(entry, field):
                parsed_entry[field] = getattr(entry, field)
        parsed_feed.append(parsed_entry)

    return parsed_feed

def fetch_article_content(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the main article text
        article_div = soup.find('div', class_='main--single--article--content--text')
        article_text = article_div.get_text(separator='\n', strip=True) if article_div else "Article content not found."

        # Extract image URLs
        images = soup.find_all('img', src=True, id=True)
        image_urls = [img['src'] for img in images]

        return {
            "article_text": article_text,
            "images": image_urls
        }
    except Exception as e:
        return {"error": f"Failed to fetch article: {str(e)}"}

