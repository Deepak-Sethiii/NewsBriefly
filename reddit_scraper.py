from dotenv import load_dotenv
from typing import List, Dict
import os
import requests
import asyncio
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, SystemMessage
import ollama

# Load environment variables
load_dotenv()

# Constants
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Use posts from last 14 days only
two_weeks_ago = datetime.today() - timedelta(days=14)
two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')


def google_search_reddit(topic: str) -> List[Dict]:
    """Search Reddit posts about the topic using Serper.dev"""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": f"{topic} site:reddit.com after:{two_weeks_ago_str}"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 429:
        raise RuntimeError("Serper API rate limit exceeded.")
    response.raise_for_status()

    results = response.json()
    return results.get("organic", [])[:3]  # top 3 Reddit posts


async def summarize_posts_with_ollama(posts: List[dict], topic: str) -> str:
    if not posts:
        return "❌ No Reddit posts found for this topic."

    content = f"📌 Topic: {topic}\n\n"
    for i, post in enumerate(posts, 1):
        title = post.get("title", "No Title")
        snippet = post.get("snippet", "No Snippet")
        link = post.get("link", "No Link")
        content += f"🔹 Post {i}:\nTitle: {title}\nSnippet: {snippet}\nLink: {link}\n\n"

    system_prompt = """
You are a Reddit analyst bot.

Your job is to summarize Reddit discussions into:
- Main discussion points
- Key opinions expressed
- Overall sentiment (positive / neutral / negative)
- No usernames or markdown

Write in clean, natural language. Output should sound like a news analyst explaining Reddit discourse.
"""

    try:
        result = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )
        return result["message"]["content"]
    except Exception as e:
        return f"❌ Ollama error: {str(e)}"


async def process_topic(topic: str) -> str:
    """Scrape and summarize one topic"""
    try:
        posts = google_search_reddit(topic)
        return await summarize_posts_with_ollama(posts, topic)
    except Exception as e:
        return f"⚠️ Error processing topic '{topic}': {e}"


async def scrape_reddit_topics(topics: List[str]) -> Dict[str, str]:
    """Process multiple topics"""
    all_summaries = {}

    for topic in topics:
        print(f"🔍 Processing topic: {topic}")
        try:
            posts = google_search_reddit(topic)
            summary = await summarize_posts_with_ollama(posts, topic)
            all_summaries[topic] = summary
        except Exception as e:
            all_summaries[topic] = f"⚠️ Error processing topic '{topic}': {str(e)}"

    return {"reddit_analysis": all_summaries}
