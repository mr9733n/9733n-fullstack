import feedparser
import time
from flask import Flask, jsonify, render_template, request
import requests
from bs4 import BeautifulSoup
import re

# Список полей, которые вы хотите извлечь из каждой записи
fields_to_extract = [
    "id", "link", "published", "summary", "tags", "title", "description"
]

RSS_FEED_URL = "https://www.newsru.co.il/il/www/news/hot"

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

def remove_adv_words(article_text):
    # Определите регулярное выражение для поиска слов, начинающихся с "adv_"
    adv_pattern = r'\b(adv_|m_|incontent_)\w+\b'
    
    # Используйте re.sub для замены найденных слов на пустую строку
    cleaned_text = re.sub(adv_pattern, '', article_text, flags=re.IGNORECASE)
    
    return cleaned_text

# Храните последние данные RSS для сравнения
last_feeds = {}

def rss_parser(version):
    return render_template('rss_parser.html', version)


