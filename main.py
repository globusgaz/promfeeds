import os
import sys
import time
import json
import gzip
import logging
import datetime
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

# 🔧 Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("main.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# 📥 Завантаження XML-фіду
def load_feed(feed_id: int) -> Optional[ET.Element]:
    url = f"https://api.dropshipping.ua/api/feeds/{feed_id}.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CopilotBot/1.0)"
    }
    logging.info(f"📥 Завантажую: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            logging.error(f"❌ Помилка завантаження: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"❌ Запит не вдався: {e}")
        return None

    filename = f"raw_feed_{feed_id}.xml"
    with open(filename, "wb") as f:
        f.write(response.content)
    logging.info(f"💾 Фід збережено у файл: {filename}")

    return ET.fromstring(response.content)

# 💰 Парсинг ціни
def find_price(offer: ET.Element) -> str:
    for elem in offer:
        if elem.tag.lower() == "price":
            return elem.text.strip() if elem.text else ""
    return ""

# 📦 Перевірка наявності
def find_availability(offer: ET.Element) -> str:
    return offer.attrib.get("available", "").lower()

# 🧱 Побудова XML-структури
def build_xml(offers: List[Dict[str, str]]) -> ET.ElementTree:
    root = ET.Element("offers")
    for offer in offers:
        item = ET.SubElement(root, "offer")
        ET.SubElement(item, "price").text = offer["price"]
        ET.SubElement(item, "available").text = offer["available"]
    return ET.ElementTree(root)

# 🗜️ Збереження у .xml.gz
def save_gzipped_xml(tree: ET.ElementTree, filename: str) -> None:
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8")
    with gzip.open(filename, "wb") as f:
        f.write(xml_bytes)

# 🔁 Збір товарів з кількох фідів
def collect_all_available_items(feed_ids: List[int]) -> List[Dict[str, str]]:
    all_items = []
    for feed_id in feed_ids:
        logging.info(f"🚀 Обробляю фід {feed_id}")
        root = load_feed(feed_id)
        if root is None:
            continue

        offers = root.findall(".//offer")
        logging.info(f"→ Знайдено {len(offers)} товарів у фіді {feed_id}")

        for offer in offers:
            price = find_price(offer)
            availability = find_availability(offer)
            if availability == "true":
                all_items.append({
                    "price": price,
                    "available": availability
                })

    logging.info(f"✅ Загальна кількість доступних товарів: {len(all_items)}")
    return all_items

# 📤 Оновлення вихідних файлів
def update_all_outputs(feed_ids: List[int], output_files: List[str]) -> None:
    items = collect_all_available_items(feed_ids)
    tree = build_xml(items)
    for filename in output_files:
        save_gzipped_xml(tree, filename)
        logging.info(f"📦 Файл оновлено: {filename}")

# 🚀 Запуск
if __name__ == "__main__":
    logging.info("Запускаю main.py...")
    FEED_IDS = [1849, 1850, 1851, 1852]
    OUTPUT_FILES = ["b2b.prom.1.xml.gz", "b2b.prom.2.xml.gz"]
    update_all_outputs(FEED_IDS, OUTPUT_FILES)
