import xml.etree.ElementTree as ET
import gzip
import datetime
import requests
import difflib

FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000
BASE_URL = "https://api.dropshipping.ua/api/feeds/"
TARGET_VENDOR_CODE = "3184"

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
        shop = root.find("shop")
        if shop is None:
            return []
        offers_tag = shop.find("offers")
        if offers_tag is None:
            return []
        offers = offers_tag.findall("offer")
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

def find_similar_offers(offers, target_code):
    similar = []
    for offer in offers:
        vendor_code = offer.findtext("vendorCode", "")
        name = offer.findtext("name", "")
        if vendor_code != target_code:
            if target_code in name or difflib.SequenceMatcher(None, vendor_code, target_code).ratio() > 0.6:
                similar.append(offer)
    return similar

def merge_feeds(feed_ids):
    all_offers = []
    found_target = False
    similar_to_target = []

    for feed_id in feed_ids:
        offers = load_feed(feed_id)
        for offer in offers:
            cleaned = clean_offer(offer)
            vendor_code = cleaned.findtext("vendorCode", "")
            if vendor_code == TARGET_VENDOR_CODE:
                found_target = True
                print(f"✅ Товар з кодом {TARGET_VENDOR_CODE} знайдено: {cleaned.findtext('name')}")
            all_offers.append(cleaned)

        if not found_target:
            similar = find_similar_offers(offers, TARGET_VENDOR_CODE)
            similar_to_target.extend(similar)

    if not found_target:
        print(f"⚠️ Товар з кодом {TARGET_VENDOR_CODE} не знайдено у фідах.")
        if similar_to_target:
            print(f"🔍 Знайдено {len(similar_to_target)} схожих товарів:")
            for offer in similar_to_target[:5]:  # показати максимум 5
                print(f"→ {offer.findtext('name')} | Код: {offer.findtext('vendorCode')}")

    print(f"\n✅ Всього оброблено: {len(all_offers)} товарів\n")
    return all_offers

def create_output_xml(offers, file_index):
    root = ET.Element("yml_catalog")
    shop = ET.SubElement(root, "shop")
    offers_tag = ET.SubElement(shop, "offers")

    for offer in offers:
        offers_tag.append(offer)

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
