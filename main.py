import os
import sys
import time
import gzip
import logging
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional

# 🔧 Логування
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
    headers = {"User-Agent": "Mozilla/5.0"}
    logging.info(f"📥 Завантажую: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            logging.error(f"❌ Помилка завантаження: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"❌ Запит не вдався: {e}")
        return None

    return ET.fromstring(response.content)

# 📤 Збір валідних товарів
def collect_valid_offers(feed_ids: List[int]) -> List[ET.Element]:
    all_valid = []
    for feed_id in feed_ids:
        root = load_feed(feed_id)
        if root is None:
            continue

        offers = root.findall(".//offer")
        total = len(offers)
        skipped = 0

        for offer in offers:
            if offer.attrib.get("available", "false") != "true":
                skipped += 1
                continue
            if not offer.findtext("price") or not offer.findtext("name"):
                skipped += 1
                continue
            all_valid.append(offer)

        logging.info(f"📊 Фід {feed_id}: знайдено {total}, валідних {len(offers)-skipped}, пропущено {skipped}")
    return all_valid

# 🧱 Побудова XML у форматі Prom.ua
def build_prom_xml(offers: List[ET.Element]) -> ET.ElementTree:
    root = ET.Element("offers")
    for offer in offers:
        new_offer = ET.SubElement(root, "offer", {
            "id": offer.attrib.get("id", ""),
            "available": "true",
            "selling_type": offer.attrib.get("selling_type", "r")
        })

        def copy(tag):
            val = offer.findtext(tag)
            if val:
                ET.SubElement(new_offer, tag).text = val.strip()

        # Основні поля
        for tag in [
            "url", "price", "currencyId", "categoryId", "minimum_order_quantity",
            "quantity_in_stock", "vendorCode", "vendor", "name", "name_ua",
            "description", "description_ua"
        ]:
            copy(tag)

        # Картинки
        for pic in offer.findall("picture"):
            if pic.text:
                ET.SubElement(new_offer, "picture").text = pic.text.strip()

    return ET.ElementTree(root)

# 🗜️ Збереження у .xml.gz
def save_gzipped(tree: ET.ElementTree, filename: str):
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8")
    with gzip.open(filename, "wb") as f:
        f.write(xml_bytes)
    logging.info(f"📦 Файл збережено: {filename}")

# 📤 Основна функція
def update_outputs(feed_ids: List[int], output_files: List[str]):
    offers = collect_valid_offers(feed_ids)
    if not offers:
        logging.warning("⚠️ Немає валідних товарів")
        return

    half = len(offers) // 2
    chunks = [offers[:half], offers[half:]]

    for i, filename in enumerate(output_files):
        tree = build_prom_xml(chunks[i])
        save_gzipped(tree, filename)

# 🚀 Запуск
if __name__ == "__main__":
    start = time.time()
    logging.info("🚀 Запускаю main.py...")

    FEED_IDS = [1849, 1850, 1851, 1852]
    OUTPUT_FILES = ["b2b.prom.1.xml.gz", "b2b.prom.2.xml.gz"]
    update_outputs(FEED_IDS, OUTPUT_FILES)

    logging.info(f"✅ Готово за {time.time() - start:.2f} сек")
