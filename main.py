import xml.etree.ElementTree as ET
import gzip
import os
import datetime
import requests

FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000
FEED_DIR = "feeds"
BASE_URL = "https://api.dropshipping.ua/api/feeds"

def load_feed(feed_id):
    url = f"{BASE_URL}/{feed_id}.xml"
    try:
        print(f"📥 Завантажую: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        offers = root.find("shop").find("offers").findall("offer")
        print(f"→ {len(offers)} товарів у фіді {feed_id}")
        return offers
    except Exception as e:
        print(f"❌ Помилка завантаження {url}: {e}")
        return []

def clean_offer(offer):
    for tag in ["oldprice", "discount", "bonus"]:
        elem = offer.find(tag)
        if elem is not None:
            offer.remove(elem)
    return offer

def merge_feeds(feed_ids):
    all_offers = []
    for feed_id in feed_ids:
        offers = load_feed(feed_id)
        for offer in offers:
            cleaned = clean_offer(offer)
            all_offers.append(cleaned)
    print(f"\n✅ Всього зібрано: {len(all_offers)} товарів")
    return all_offers

def create_output_xml(offers, file_index):
    root = ET.Element("yml_catalog")
    shop = ET.SubElement(root, "shop")
    offers_tag = ET.SubElement(shop, "offers")

    for offer in offers:
        offers_tag.append(offer)

    # додаємо мітку часу (щоб Git бачив зміни)
    timestamp = ET.SubElement(shop, "generated_at")
    timestamp.text = datetime.datetime.now().isoformat()

    tree = ET.ElementTree(root)
    filename = f"b2b.prom.{file_index}.xml.gz"

    with gzip.open(filename, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    print(f"📦 Створено: {filename} ({len(offers)} товарів)")

def split_and_save(offers, chunk_size):
    for i in range(0, len(offers), chunk_size):
        chunk = offers[i:i + chunk_size]
        file_index = i // chunk_size + 1
        create_output_xml(chunk, file_index)

if __name__ == "__main__":
    print("🚀 Скрипт стартував...")
    offers = merge_feeds(FEED_IDS)
    split_and_save(offers, CHUNK_SIZE)
    print("✅ Робота завершена")import xml.etree.ElementTree as ET
import gzip
import os
import datetime
import requests

FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000
FEED_DIR = "feeds"
BASE_URL = "https://api.dropshipping.ua/api/feeds"

def load_feed(feed_id):
    url = f"{BASE_URL}/{feed_id}.xml"
    try:
        print(f"📥 Завантажую: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        offers = root.find("shop").find("offers").findall("offer")
        print(f"→ {len(offers)} товарів у фіді {feed_id}")
        return offers
    except Exception as e:
        print(f"❌ Помилка завантаження {url}: {e}")
        return []

def clean_offer(offer):
    for tag in ["oldprice", "discount", "bonus"]:
        elem = offer.find(tag)
        if elem is not None:
            offer.remove(elem)
    return offer

def merge_feeds(feed_ids):
    all_offers = []
    for feed_id in feed_ids:
        offers = load_feed(feed_id)
        for offer in offers:
            cleaned = clean_offer(offer)
            all_offers.append(cleaned)
    print(f"\n✅ Всього зібрано: {len(all_offers)} товарів")
    return all_offers

def create_output_xml(offers, file_index):
    root = ET.Element("yml_catalog")
    shop = ET.SubElement(root, "shop")
    offers_tag = ET.SubElement(shop, "offers")

    for offer in offers:
        offers_tag.append(offer)

    # додаємо мітку часу (щоб Git бачив зміни)
    timestamp = ET.SubElement(shop, "generated_at")
    timestamp.text = datetime.datetime.now().isoformat()

    tree = ET.ElementTree(root)
    filename = f"b2b.prom.{file_index}.xml.gz"

    with gzip.open(filename, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    print(f"📦 Створено: {filename} ({len(offers)} товарів)")

def split_and_save(offers, chunk_size):
    for i in range(0, len(offers), chunk_size):
        chunk = offers[i:i + chunk_size]
        file_index = i // chunk_size + 1
        create_output_xml(chunk, file_index)

if __name__ == "__main__":
    print("🚀 Скрипт стартував...")
    offers = merge_feeds(FEED_IDS)
    split_and_save(offers, CHUNK_SIZE)
    print("✅ Робота завершена")
