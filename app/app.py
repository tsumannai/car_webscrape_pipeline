from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn

from scraper.web_scrape import run_scrape

class ScrapeRequest(BaseModel):
    url: HttpUrl

app = FastAPI()


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    try:
        result = run_scrape(str(request.url))
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------
# Allow running directly
# ------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app:app",     # <file>:<FastAPI instance>
        host="0.0.0.0",
        port=8000,
        reload=True
    )