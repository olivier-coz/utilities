import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import os

# Configuration
BASE_URL = ""
SEARCH_URL = BASE_URL + ""
CSV_FILE = "laptops.csv"
HTML_CACHE = "cache"

TARGET_GPU = ""  # Set to "" to disable filtering
TARGET_CPU = ""  # Set to "" to disable filtering
MAX_PRICE = 1000.0 

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Ensure cache directory exists
os.makedirs(HTML_CACHE, exist_ok=True)

def fetch_page(page_number):
    cache_file = os.path.join(HTML_CACHE, f"page_{page_number}.html")

    if os.path.exists(cache_file):
        last_modified = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - last_modified < timedelta(hours=1):
            print(f"Using cached HTML for page {page_number}")
            with open(cache_file, 'r', encoding='utf-8') as file:
                return file.read()

    print(f"Downloading page {page_number}")
    response = requests.get(SEARCH_URL.format(page_number), headers=HEADERS)

    if response.url.strip("/") == BASE_URL.strip("/"):
        return None

    with open(cache_file, 'w', encoding='utf-8') as file:
        file.write(response.text)

    return response.text


def parse_product(card):
    try:
        name_tag = card.select_one("div.p-y-10 h3 a")
        if not name_tag:
            return None

        name = name_tag.get("title").strip()
        link = BASE_URL.rstrip("/") + name_tag.get("href").strip()

        specs = [li.get_text(strip=True).replace("\xa0", " ") for li in card.select("ul.specs li")]
        if len(specs) < 7:
            return None

        cpu, gpu = specs[3], specs[4]
        if TARGET_GPU and TARGET_GPU not in gpu:
            return None
        if TARGET_CPU and TARGET_CPU not in cpu:
            return None

        price_tag = card.select_one("a.btn-success.price")
        if not price_tag:
            return None

        price_text = price_tag.get_text(strip=True)
        price_clean = price_text.replace("€", "").replace(",", ".").replace(" ", "")
        price = float(price_clean)

        if price > MAX_PRICE:
            return None

        return {
            "name": name,
            "link": link,
            "screen": specs[0],
            "resolution": specs[1],
            "os": specs[2],
            "cpu": cpu,
            "gpu": gpu,
            "ram": specs[5],
            "storage": specs[6],
            "price": price,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    except Exception as e:
        print(f"Error parsing product: {e}")
        return None


def scrape_all():
    page = 1
    results = []

    while True:
        html = fetch_page(page)
        if html is None:
            print("No more pages.")
            break

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.card.product")

        if not cards:
            print("No products on page.")
            break

        for card in cards:
            product = parse_product(card)
            if product:
                results.append(product)

        page += 1

    return results


def save_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    fields = ["name", "link", "screen", "resolution", "os", "cpu", "gpu", "ram", "storage", "price", "date"]
    
    write_header = not os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    laptops = scrape_all()
    save_csv(laptops, CSV_FILE)

    if laptops:
        print(f"{len(laptops)} laptops saved to {CSV_FILE}")
    else:
        print("No matching laptops found.")
