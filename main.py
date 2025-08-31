import os
import time
import logging
import datetime
import json
import requests
import xml.etree.ElementTree as ET

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("main.log"),
        logging.StreamHandler()
    ]
)

def load_feed(feed_id):
    url = f"https://api.dropshipping.ua/api/feeds/{feed_id}.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CopilotBot/1.0)"
    }
    logging.info(f"📥 Завантажую: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"❌ Помилка завантаження: {response.status_code}")
        return None

    filename = f"raw_feed_{feed_id}.xml"
    with open(filename, "wb") as f:
        f.write(response.content)
    logging.info(f"💾 Фід збережено у файл: {filename}")

    return ET.fromstring(response.content)

def find_quantity(offer):
    for elem in offer:
        tag = elem.tag.lower()
        if "quantity" in tag or "stock" in tag or "available" in tag or "presence" in tag:
            if elem.text and elem.text.strip().replace('.', '', 1).isdigit():
                return elem.text.strip()

    for param in offer.findall("param"):
        name_attr = param.attrib.get("name", "").lower()
        if "кількість" in name_attr or "наличие" in name_attr or "stock" in name_attr:
            if param.text and param.text.strip().replace('.', '', 1).isdigit():
                return param.text.strip()

    return None

def find_price(offer):
    for elem in offer:
        tag = elem.tag.lower()
        if "price" in tag:
            return elem.text.strip()
    return None

def process_feed(feed_id):
    logging.info("🚀 Скрипт стартував...")
    root = load_feed(feed_id)
    if root is None:
        return

    offers = root.findall(".//offer")
    logging.info(f"→ Знайдено {len(offers)} товарів у фіді {feed_id}")

    for offer in offers:
        price = find_price(offer)
        quantity = find_quantity(offer)
        logging.info(f"🔎 Товар: ціна = {price}, кількість = {quantity}")

if __name__ == "__main__":
    logging.info("Запускаю main.py...")
    process_feed(1849)
