import xml.etree.ElementTree as ET
import gzip
import datetime
import requests

# 🔧 Налаштування
FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000
BASE_URL = "https://api.dropshipping.ua/api/feeds/"
OUTPUT_PREFIX = "b2b.prom"

# 📥 Завантаження одного фіду
def load_feed(feed_id):
    url = f"{BASE_URL}{feed_id}.xml"
    print(f"📥 Завантажую: {url}")
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        shop = root.find("shop")
        offers_tag = shop.find("offers") if shop is not None else None
        return offers_tag.findall("offer") if offers_tag is not None else []
    except Exception as e:
        print(f"❌ Помилка з фідом {feed_id}: {e}")
        return []

# 🧹 Очищення зайвих тегів
def clean_offer(offer):
    for tag in ["oldprice", "discount", "bonus"]:
        elem = offer.find(tag)
        if elem is not None:
            offer.remove(elem)
    return offer

# 🔄 Об'єднання всіх фідів
def merge_feeds(feed_ids):
    all_offers = []
    for feed_id in feed_ids:
        offers = load_feed(feed_id)
        for offer in offers:
            quantity = offer.findtext("quantity", "0")
            price = offer.findtext("price", "")
            if int(quantity) == 0 or not price:
                continue  # Пропустити недоступні товари

            cleaned = clean_offer(offer)
            all_offers.append(cleaned)
        print(f"→ Фід {feed_id}: додано {len(offers)} товарів")
    print(f"\n✅ Всього актуальних товарів: {len(all_offers)}\n")
    return all_offers

# 📦 Створення вихідного XML
def create_output_xml(offers, file_index):
    root = ET.Element("yml_catalog")
    shop = ET.SubElement(root, "shop")
    offers_tag = ET.SubElement(shop, "offers")

    for offer in offers:
        offers_tag.append(offer)

    timestamp = ET.SubElement(shop, "generated_at")
    timestamp.text = datetime.datetime.now().isoformat()

    tree = ET.ElementTree(root)
    filename = f"{OUTPUT_PREFIX}.{file_index}.xml.gz"
    with gzip.open(filename, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    print(f"📦 Створено: {filename} — {len(offers)} товарів")

# 🚀 Основний запуск
if __name__ == "__main__":
    offers = merge_feeds(FEED_IDS)
    for i in range(0, len(offers), CHUNK_SIZE):
        chunk = offers[i:i + CHUNK_SIZE]
        file_index = i // CHUNK_SIZE + 1
        create_output_xml(chunk, file_index)
