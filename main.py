import requests
import xml.etree.ElementTree as ET

FEED_URL = "https://api.dropshipping.ua/api/feeds/1849.xml"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(FEED_URL, headers=headers)
response.encoding = 'utf-8'

if response.status_code != 200:
    raise Exception(f"Не вдалося завантажити фід: {response.status_code}")

root = ET.fromstring(response.text)

# 🔍 Знаходимо всі товари
offers = root.find("shop").find("offers").findall("offer")

print(f"\n🔎 Знайдено {len(offers)} товарів. Ось перші 5:\n")

for offer in offers[:5]:
    name = offer.findtext("name", default="(немає назви)")
    price = offer.findtext("price", default="(немає ціни)")
    category_id = offer.findtext("categoryId", default="(немає категорії)")
    description = offer.findtext("description", default="(немає опису)")

    print(f"📦 Назва: {name}")
    print(f"💰 Ціна: {price}")
    print(f"📂 Категорія ID: {category_id}")
    print(f"📝 Опис: {description[:100]}...\n")  # обрізаємо опис до 100 символів
