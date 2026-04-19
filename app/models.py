from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class Book(BaseModel):
    title: str
    price: str
    availability: str
    rating: Optional[str] = None
    product_url: Optional[str] = None


class ProductScrapeRequest(BaseModel):
    url: HttpUrl


class Product(BaseModel):
    brand: Optional[str] = None
    title: str
    price_current: Optional[str] = None
    price_old: Optional[str] = None
    discount: Optional[str] = None
    availability: Optional[str] = None
    sku: Optional[str] = None
    sizes: List[dict] = []
    source_url: str
    scraped_at: str