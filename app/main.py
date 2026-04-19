from fastapi import FastAPI, HTTPException, Query
from app.scraper import scrape_books_toscrape, scrape_fitpoint_product
from app.storage import save_to_history, read_history

app = FastAPI(
    title="Scraping API",
    description="API para scraping de libros y productos web",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Scraping API activa",
        "endpoints": [
            "/health",
            "/books",
            "/product?url=...",
            "/history",
            "/save-product?url=..."
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/books")
def get_books():
    try:
        books = scrape_books_toscrape()
        return {
            "total": len(books),
            "source": "https://books.toscrape.com/",
            "items": books
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping books: {str(e)}")


@app.get("/product")
def get_product(url: str = Query(..., description="URL del producto a scrapear")):
    try:
        product = scrape_fitpoint_product(url)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping product: {str(e)}")


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