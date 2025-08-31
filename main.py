import requests
import xml.etree.ElementTree as ET

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

# 🧾 КРОК 4: Вивести перші 1000 символів XML
print("\n🔍 Перші 1000 символів XML:")
print(response.text[:1000])

# 🧪 КРОК 5: Парсинг XML
root = ET.fromstring(response.text)

# 🧩 КРОК 6: Вивести всі назви тегів
print("\n📦 Список тегів у XML:")
for elem in root.iter():
    print("→", elem.tag)
