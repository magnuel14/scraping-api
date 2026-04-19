from fastapi import FastAPI, HTTPException, Query
from app.scraper import (
    scrape_fitpoint_product,
    scrape_fitpoint_catalog,
    scrape_fitpoint_catalog_with_details
)
from app.storage import save_to_history, read_history

app = FastAPI(
    title="Scraping API",
    description="API para scraping de libros y productos web",
    version="3.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Scraping API activa",
        "endpoints": [
            "/health",
            "/books",
            "/product?url=...",
            "/catalog?url=...",
            "/catalog/details?url=...&limit=5",
            "/save-product?url=...",
            "/history"
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/product")
def get_product(url: str = Query(..., description="URL del producto a scrapear")):
    try:
        return scrape_fitpoint_product(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping product: {str(e)}")


@app.get("/catalog")
def get_catalog(
    url: str = Query(..., description="URL del catálogo a scrapear"),
    max_pages: int | None = Query(None, description="Máximo de páginas a recorrer", ge=1, le=50)
):
    try:
        items = scrape_fitpoint_catalog(url, max_pages=max_pages)
        return {
            "total": len(items),
            "source": url,
            "max_pages": max_pages,
            "items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping catalog: {str(e)}")


@app.get("/catalog/details")
def get_catalog_details(
    url: str = Query(..., description="URL del catálogo a scrapear"),
    limit: int = Query(5, description="Cantidad máxima de productos a procesar", ge=1, le=100),
    max_pages: int | None = Query(None, description="Máximo de páginas a recorrer", ge=1, le=50)
):
    try:
        items = scrape_fitpoint_catalog_with_details(url, limit=limit, max_pages=max_pages)
        return {
            "total": len(items),
            "source": url,
            "limit": limit,
            "max_pages": max_pages,
            "items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping catalog details: {str(e)}")


@app.get("/save-product")
def save_product(url: str = Query(..., description="URL del producto a scrapear y guardar")):
    try:
        product = scrape_fitpoint_product(url)
        save_to_history(product)
        return {
            "message": "Producto guardado en historial",
            "data": product
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving product: {str(e)}")


@app.get("/history")
def get_history():
    try:
        history = read_history()
        return {
            "total": len(history),
            "items": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading history: {str(e)}")