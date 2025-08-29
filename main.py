import xml.etree.ElementTree as ET
import gzip

FEED_IDS = [1849, 1850, 1851, 1852]
CHUNK_SIZE = 20000

def load_feed(feed_id):
    file_path = f"feeds/{feed_id}.xml"
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root.find("shop").find("offers").findall("offer")

def clean_offer(offer):
    # видаляємо зайві теги
    for tag in ["oldprice", "discount", "bonus"]:
        elem = offer.find(tag)
        if elem is not None:
            offer.remove(elem)
    return offer

def merge_feeds(feed_ids):
    all_offers = []
    for feed_id in feed_ids:
        print(f"Завантажую: {feed_id}")
        offers = load_feed(feed_id)
        print(f"→ Знайдено {len(offers)} товарів у фіді {feed_id}")
        for offer in offers:
            cleaned = clean_offer(offer)
            all_offers.append(cleaned)
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

    print(f"✅ Створено: {filename} ({len(offers)} товарів)")

def split_and_save(offers, chunk_size):
    chunks = [offers[i:i + chunk_size] for i in range(0, len(offers), chunk_size)]
    for idx, chunk in enumerate(chunks, start=1):
        create_output_xml(chunk, idx)

if __name__ == "__main__":
    offers = merge_feeds(FEED_IDS)
    split_and_save(offers, CHUNK_SIZE)
