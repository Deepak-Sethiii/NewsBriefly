from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from models import NewsRequest
from utils import generate_broadcast_news
from news_scraper import NewsScraper
from reddit_scraper import scrape_reddit_topics
import logging

# ✅ Setup
app = FastAPI()
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

@app.post("/generate-news-summary")
async def generate_news_summary(request: NewsRequest):
    try:
        results = {}

        # ✅ Scrape news
        if request.source_type in ["news", "both"]:
            news_scraper = NewsScraper()
            results["news"] = await news_scraper.scrape_news(request.topics)

        # ✅ Scrape Reddit
        if request.source_type in ["reddit", "both"]:
            results["reddit"] = await scrape_reddit_topics(request.topics)

        # ✅ Prepare data
        news_data = results.get("news", {})
        reddit_data = results.get("reddit", {})

        # ✅ Generate summary using LLM
        summary_text = generate_broadcast_news(
            news_data=news_data,
            reddit_data=reddit_data,
            topics=request.topics
        )

        # ✅ Return as plain JSON
        return {"summary": summary_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Optional: for local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=1234, reload=True)
