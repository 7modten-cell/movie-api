from fastapi import FastAPI, HTTPException
from starlette.types import ASGIApp, Scope, Receive, Send
import requests
from bs4 import BeautifulSoup

# معالج وسيط لقراءة مسار Vercel الحقيقي تلقائياً
class VercelMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path")
            if matched_path:
                scope["path"] = matched_path.decode("utf-8").split("?")[0]
        await self.app(scope, receive, send)

app = FastAPI(title="Movie Scraper API")
app.add_middleware(VercelMiddleware)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.get("/")
def home():
    return {"status": "API is running successfully on Vercel!"}

@app.get("/search")
def search_movie(q: str):
    search_url = f"https://wecima.social/search/{q}/"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch source")
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
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
