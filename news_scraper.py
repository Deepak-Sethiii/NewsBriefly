import asyncio
from typing import Dict, List
from aiolimiter import AsyncLimiter
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import ollama  # Ollama client

from utils import (
    generate_news_urls_to_scrape,
    google_search,
    clean_html_to_text,
    extract_headlines
)

load_dotenv()


class NewsScraper:
    _rate_limiter = AsyncLimiter(5, 1)  # 5 requests per second

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def scrape_news(self, topics: List[str]) -> Dict[str, str]:
        """Scrape and summarize news articles using Ollama (local)"""
        results = {}

        system_prompt = """
You are a professional news editor and scriptwriter for a podcast.
Turn raw headlines into a clean, professional, and TTS-friendly news script.
Avoid markdown, emojis, or formatting. Use spoken-style language.
"""

        for topic in topics:
            async with self._rate_limiter:
                try:
                    # Step 1: Get news text
                    urls = generate_news_urls_to_scrape([topic])
                    search_html = google_search(urls[topic])
                    clean_text = clean_html_to_text(search_html)
                    headlines = extract_headlines(clean_text)

                    # Step 2: Summarize using Ollama (llama3)
                    response = ollama.chat(
                        model="llama3",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": headlines}
                        ]
                    )

                    results[topic] = response['message']['content']

                except Exception as e:
                    results[topic] = f"Error: {str(e)}"

                await asyncio.sleep(1)

        return {"news_analysis": results}
