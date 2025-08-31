import requests
import xml.etree.ElementTree as ET
import csv

# 🌐 КРОК 1: URL фіду
FEED_URL = "https://api.dropshipping.ua/api/feeds/1849.xml"

# 🛡️ КРОК 2: Заголовки для обходу 403
headers = {
    "User-Agent": "Mozilla/5.0"
}

# 📥 КРОК 3: Завантаження фіду
response = requests.get(FEED_URL, headers=headers)
response.encoding = 'utf-8'

if response.status_code != 200:
    raise Exception(f"Не вдалося завантажити фід: {response.status_code}")

# 🧪 КРОК 4: Парсинг XML
root = ET.fromstring(response.text)
items = root.findall(".//item")
print(f"→ Фід 1849: знайдено {len(items)} товарів")

# 🧹 КРОК 5: Обробка товарів
products = []

for item in items:
    name = item.findtext("name", default="").strip()
    price = float(item.findtext("price", default="0").strip())
    quantity = float(item.findtext("quantity", default="0").strip())

    print(f"🧪 Товар: quantity='{quantity}', price='{price}'")

    # Пропускаємо лише товари з price <= 0
    if price <= 0:
        print(f"⚠️ Пропущено: quantity={quantity}, price={price}")
        continue

    products.append({
        "name": name,
        "price": price,
        "quantity": quantity
    })

# 📁 КРОК 6: Збереження у CSV
with open("products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "price", "quantity"])
    writer.writeheader()
    writer.writerows(products)

print(f"✅ Збережено: {len(products)} товарів у products.csv")
