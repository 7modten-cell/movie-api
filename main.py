from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Movie Scraper API")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.get("/")
def home():
    return {"status": "API is running successfully"}

@app.get("/search")
def search_movie(q: str):
    search_url = f"https://wecima.social/search/{q}/"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch source")
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # استخراج كروت الأفلام من الصفحة (حسب هيكل القالب)
        items = soup.select(".GridItem, .Thumb--GridItem, .media-block")
        for item in items:
            title_elem = item.select_one(".Title, h3, a.title")
            img_elem = item.select_one("img")
            link_elem = item.select_one("a")
            
            title = title_elem.text.strip() if title_elem else "No Title"
            img = img_elem.get("data-src") or img_elem.get("src") if img_elem else ""
            link = link_elem.get("href") if link_elem else ""
            
            if link:
                results.append({
                    "title": title,
                    "poster": img,
                    "url": link
                })
                
        return {"query": q, "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

