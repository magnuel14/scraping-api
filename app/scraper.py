import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "html.parser")


def build_page_url(base_url: str, page: int) -> str:
    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    query["p"] = [str(page)]
    new_query = urlencode(query, doseq=True)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

# =========================
# FITPOINT - CATALOGO
# =========================
def extract_catalog_page(url: str):
    soup = get_soup(url)
    products = []

    for item in soup.select(".product-item"):
        brand_tag = item.select_one(".ox-product-grid__category-link")
        name_tag = item.select_one(".product-item-name a, a.product-item-link")
        price_text_tag = item.select_one(".price-box .price")
        price_wrapper = item.select_one(".price-box .price-wrapper")

        brand = brand_tag.get_text(" ", strip=True) if brand_tag else None
        title = name_tag.get_text(" ", strip=True) if name_tag else None
        product_url = (
            urljoin(url, name_tag["href"])
            if name_tag and name_tag.get("href")
            else None
        )

        price = None
        if price_text_tag:
            price = price_text_tag.get_text(" ", strip=True)
        elif price_wrapper and price_wrapper.get("data-price-amount"):
            price = f"${price_wrapper['data-price-amount']}"

        if title and product_url:
            products.append({
                "brand": brand,
                "title": title,
                "price": price,
                "url": product_url
            })

    return products, soup


def get_total_pages_from_soup(soup: BeautifulSoup) -> int:
    max_page = 1

    for a in soup.select("a[href]"):
        href = a.get("href", "")
        text = a.get_text(" ", strip=True)

        match_text = re.search(r"Página\s+(\d+)", text, re.IGNORECASE)
        if match_text:
            max_page = max(max_page, int(match_text.group(1)))

        match_href = re.search(r"[?&]p=(\d+)", href)
        if match_href:
            max_page = max(max_page, int(match_href.group(1)))

    return max_page


def scrape_fitpoint_catalog(url: str, max_pages: int | None = None):
    """
    Extrae todo el catálogo recorriendo la paginación.
    Si max_pages es None, intenta detectar todas las páginas.
    """
    first_page_products, first_soup = extract_catalog_page(url)
    total_pages = get_total_pages_from_soup(first_soup)

    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    all_products = list(first_page_products)

    for page in range(2, total_pages + 1):
        page_url = build_page_url(url, page)
        page_products, _ = extract_catalog_page(page_url)
        all_products.extend(page_products)

    # quitar duplicados por URL
    unique_products = []
    seen_urls = set()

    for product in all_products:
        if product["url"] not in seen_urls:
            unique_products.append(product)
            seen_urls.add(product["url"])

    return unique_products


def scrape_fitpoint_catalog_with_details(
    url: str,
    limit: int = 5,
    max_pages: int | None = None
):
    catalog = scrape_fitpoint_catalog(url, max_pages=max_pages)
    detailed_products = []

    for product in catalog[:limit]:
        try:
            detail = scrape_fitpoint_product(product["url"])
            detailed_products.append(detail)
        except Exception as e:
            detailed_products.append({
                "source_url": product.get("url"),
                "title": product.get("title"),
                "error": f"No se pudo extraer el detalle: {str(e)}"
            })

    return detailed_products


# =========================
# FITPOINT - PRODUCTO INDIVIDUAL
# =========================
def scrape_fitpoint_product(url: str):
    soup = get_soup(url)
    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    joined = "\n".join(lines)

    title = None
    brand = None
    availability = None
    sku = None
    price_current = None
    price_old = None
    discount = None
    sizes = []

    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)

    known_brands = {
        "asics", "2xu", "champion", "ecco",
        "hydro flask", "fjallraven", "columbia"
    }

    for line in lines[:25]:
        if line.lower() in known_brands:
            brand = line
            break

    current_price_tag = (
        soup.select_one(".product-info-main .price-box .special-price .price") or
        soup.select_one(".product-info-main .price-box .price-final_price .price") or
        soup.select_one(".product-info-main .price-box .price")
    )

    if current_price_tag:
        price_current = current_price_tag.get_text(strip=True)

    old_price_tag = (
        soup.select_one(".product-info-main .price-box .old-price .price") or
        soup.select_one(".product-info-main .price-box .price-wrapper[data-price-type='oldPrice']")
    )

    if old_price_tag:
        if hasattr(old_price_tag, "get_text"):
            price_old = old_price_tag.get_text(strip=True)
        else:
            price_old = old_price_tag.get("data-price-amount")

    if not price_current or price_current == "$2.99":
        prices = re.findall(r"\$\d+\.\d{2}", joined)
        prices_filtrados = [p for p in prices if p != "$2.99"]
        if prices_filtrados:
            price_current = prices_filtrados[0]
        if len(prices_filtrados) > 1 and not price_old:
            price_old = prices_filtrados[1]

    if price_old and not str(price_old).startswith("$"):
        price_old = f"${price_old}"

    discount_match = re.search(r"Ahorra\s+(\d+%)", joined, re.IGNORECASE)
    if discount_match:
        discount = discount_match.group(1)

    if "Disponible" in joined:
        availability = "Disponible"

    for i, line in enumerate(lines):
        if line.upper() == "SKU" and i + 1 < len(lines):
            sku = lines[i + 1]
            break

    for row in soup.select("table tr"):
        cols = [c.get_text(" ", strip=True) for c in row.select("th, td")]
        if len(cols) == 3:
            if cols[0].upper() == "USA" and cols[1].upper() == "EC" and cols[2].upper() == "CM":
                continue
            try:
                float(cols[0])
                float(cols[1])
                float(cols[2])
                sizes.append({
                    "usa": cols[0],
                    "ec": cols[1],
                    "cm": cols[2]
                })
            except ValueError:
                pass

    return {
        "brand": brand,
        "title": title,
        "price_current": price_current,
        "price_old": price_old,
        "discount": discount,
        "availability": availability,
        "sku": sku,
        "sizes": sizes,
        "source_url": url,
        "scraped_at": datetime.now(timezone.utc).isoformat()
    }