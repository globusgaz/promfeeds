import xml.etree.ElementTree as ET
import gzip
import os

FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000
FEED_DIR = "feeds"

def load_feed(feed_id):
    file_path = os.path.join(FEED_DIR, f"{feed_id}.xml")
    if not os.path.exists(file_path):
        print(f"⚠️ Файл не знайдено: {file_path}")
        return []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root.find("shop").find("offers").findall("offer")
    except ET.ParseError as e:
        print(f"❌ Помилка парсингу {file_path}: {e}")
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
        print(f"📥 Завантажую фід: {feed_id}")
        offers = load_feed(feed_id)
        print(f"→ Знайдено: {len(offers)} товарів")
        total_loaded += len(offers)

        for offer in offers:
            cleaned = clean_offer(offer)
            all_offers.append(cleaned)

    print(f"\n✅ Загалом оброблено: {total_loaded} товарів із {len(feed_ids)} фідів\n")
    return all_offers

def create_output_xml(offers, file_index):
    root = ET.Element("yml_catalog")
    shop = ET.SubElement(root, "shop")
    offers_tag = ET.SubElement(shop, "offers")

    for offer in offers:
        offers_tag.append(offer)

    tree = ET.ElementTree(root)
    filename = f"b2b.prom.{file_index}.xml.gz"

    with gzip.open(filename, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    print(f"📦 Ст
