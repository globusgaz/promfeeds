import xml.etree.ElementTree as ET
import gzip
import datetime
import requests

FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000
BASE_URL = "https://api.dropshipping.ua/api/feeds/"

def load_feed(feed_id):
    url = f"{BASE_URL}{feed_id}.xml"
    print(f"📥 Завантажую: {url}")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Помилка завантаження {url}: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
        offers = root.find("shop").find("offers").findall("offer")
        print(f"→ Знайдено {len(offers)} товарів у фіді {feed_id}")
        return offers
    except ET.ParseError as e:
        print(f"❌ Помилка парсингу {url}: {e}")
        return []

def clean_offer(offer):
    for tag in ["oldprice", "discount", "bonus"]:
        elem = offer.find(tag)
        if elem is not None:
            offer.remove(elem)
    return offer

def merge_feeds(feed_ids):
    all_offers = []
    total_loaded = 0

    for feed_id in feed_ids:
        offers = load_feed(feed_id)
        total_loaded += len(offers)
        for offer in offers:
            cleaned = clean_offer(offer)
            all_offers.append(cleaned)

    print(f"\n✅ Всього оброблено: {total_loaded} товарів\n")
    return all_offers

def create_output_xml(offers, file_index):
    root = ET.Element("yml_catalog")
    shop = ET.SubElement(root, "shop")
    offers_tag = ET.SubElement(shop, "offers")

    for offer in offers:
        offers_tag.append(offer)

    # мітка часу щоб git бачив зміни
    timestamp = ET.SubElement(shop, "generated_at")
    timestamp.text = datetime.datetime.now().isoformat()

    tree = ET.ElementTree(root)
    filename = f"b2b.prom.{file_index}.xml.gz"

    with gzip.open(filename, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    print(f"📦 Створено: {filename} — {len(offers)} товарів")

if __name__ == "__main__":
    offers = merge_feeds(FEED_IDS)

    for i in range(0, len(offers), CHUNK_SIZE):
        chunk = offers[i:i + CHUNK_SIZE]
        file_index = i // CHUNK_SIZE + 1
        create_output_xml(chunk, file_index)
