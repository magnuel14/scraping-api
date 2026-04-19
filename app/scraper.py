import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def scrape_books_toscrape(base_url: str = "https://books.toscrape.com/"):
    response = requests.get(base_url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = []

    for article in soup.select("article.product_pod"):
        title_tag = article.select_one("h3 a")
        price_tag = article.select_one(".price_color")
        stock_tag = article.select_one(".availability")
        rating_tag = article.select_one("p.star-rating")

        title = title_tag["title"].strip() if title_tag else "N/A"
        price = price_tag.get_text(strip=True) if price_tag else "N/A"
        availability = stock_tag.get_text(strip=True) if stock_tag else "N/A"
        rating = None
        if rating_tag:
            classes = rating_tag.get("class", [])
            rating = next((c for c in classes if c != "star-rating"), None)

        product_url = None
        if title_tag and title_tag.get("href"):
            product_url = urljoin(base_url, title_tag["href"])

        books.append({
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating,
            "product_url": product_url
        })

    return books


def scrape_fitpoint_product(url: str):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Extracción flexible
    title = None
    title_tag = soup.select_one("h1")
    if title_tag:
        title = title_tag.get_text(" ", strip=True)

    brand = None
    possible_brand = soup.find(string=lambda s: s and s.strip().lower() == "asics")
    if possible_brand:
        brand = possible_brand.strip()

    price_current = None
    price_old = None
    discount = None
    availability = None
    sku = None

    # Buscar precios en texto
    price_box = soup.get_text("\n", strip=True)

    # Selectores probables
    current_price_tag = soup.select_one(".price") or soup.select_one("[data-price-type='finalPrice']")
    if current_price_tag:
        price_current = current_price_tag.get_text(" ", strip=True)

    old_price_tag = soup.select_one(".old-price") or soup.select_one(".price-wrapper .price")
    if old_price_tag:
        old_price_text = old_price_tag.get_text(" ", strip=True)
        if old_price_text != price_current:
            price_old = old_price_text

    discount_tag = soup.find(string=lambda s: s and "%" in s and "Ahorra" not in s)
    if discount_tag:
        discount = discount_tag.strip()

    # Disponibilidad
    available_tag = soup.find(string=lambda s: s and "Disponible" in s)
    if available_tag:
        availability = available_tag.strip()

    # SKU
    all_text_lines = [line.strip() for line in soup.get_text("\n").split("\n") if line.strip()]
    for i, line in enumerate(all_text_lines):
        if line.upper() == "SKU" and i + 1 < len(all_text_lines):
            sku = all_text_lines[i + 1]
            break

    # Tabla de tallas
    sizes = []
    lines = all_text_lines
    try:
        idx = lines.index("USA EC CM")
        size_lines = lines[idx + 1:]
        for row in size_lines:
            parts = row.split()
            if len(parts) == 3:
                usa, ec, cm = parts
                # cortar cuando ya no sea tabla
                try:
                    float(usa)
                    float(ec)
                    float(cm)
                    sizes.append({
                        "usa": usa,
                        "ec": ec,
                        "cm": cm
                    })
                except ValueError:
                    break
    except ValueError:
        pass

    return {
        "brand": brand,
        "title": title or "N/A",
        "price_current": price_current,
        "price_old": price_old,
        "discount": discount,
        "availability": availability,
        "sku": sku,
        "sizes": sizes,
        "source_url": url,
        "scraped_at": datetime.now(timezone.utc).isoformat()
    }