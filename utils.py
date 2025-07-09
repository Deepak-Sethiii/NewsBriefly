from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
import os
from fastapi import HTTPException
from bs4 import BeautifulSoup
from datetime import datetime
from elevenlabs import ElevenLabs
from pathlib import Path
from gtts import gTTS
import ollama  # ✅ Ollama client

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Constants
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)


# ✅ Generate Google News URL for a given topic
def generate_valid_news_url(keyword: str) -> str:
    q = quote_plus(keyword)
    return f"https://news.google.com/search?q={q}&tbs=sbd:1"


def generate_news_urls_to_scrape(list_of_keywords):
    return {keyword: generate_valid_news_url(keyword) for keyword in list_of_keywords}


# ✅ Serper API Search
def google_search(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("organic", [])[:5]  # Top 5 results


# ✅ Clean HTML page to plain text
def clean_html_to_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n").strip()


# ✅ Extract first lines as potential headlines
def extract_headlines(cleaned_text: str) -> str:
    headlines, current_block = [], []
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    for line in lines:
        if line == "More":
            if current_block:
                headlines.append(current_block[0])
                current_block = []
        else:
            current_block.append(line)
    if current_block:
        headlines.append(current_block[0])
    return "\n".join(headlines)


# ✅ Summarize multiple news + reddit results into TTS-friendly news script (Ollama)
def generate_broadcast_news(news_data, reddit_data, topics):
    system_prompt = """
You are a professional news anchor assistant. Use the given news and Reddit content to create audio-ready news segments.

- Start each segment directly, no greetings or preambles.
- Use transitions like: "Meanwhile, Reddit users noted..."
- Present news first, then Reddit reactions.
- End each topic with a summarizing sentence like: "That wraps up this story on..."
- Avoid markdown, emojis, special formatting.

Create engaging, neutral-toned spoken paragraphs ready for audio use.
"""

    try:
        topic_blocks = []
        for topic in topics:
            news = news_data["news_analysis"].get(topic, '')
            reddit = reddit_data["reddit_analysis"].get(topic, '')
            context = []
            if news:
                context.append(f"OFFICIAL NEWS:\n{news}")
            if reddit:
                context.append(f"REDDIT DISCUSSION:\n{reddit}")
            if context:
                topic_blocks.append(f"TOPIC: {topic}\n" + "\n".join(context))

        user_prompt = "Generate spoken segments for:\n\n" + "\n\n--- NEW TOPIC ---\n\n".join(topic_blocks)

        # ✅ Use Ollama instead of OpenAI
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")


# ✅ Summarize single-source headlines into TTS script (Ollama)
def summarize_with_ollama_news_script(headlines: str) -> str:
    system_prompt = """
You are a podcast scriptwriter. Convert these headlines into a clean, spoken-style news script:

- Write in full spoken paragraphs.
- Avoid formatting symbols, emojis, or markdown.
- Use a formal, newsreader tone.
- No preamble, start with the story directly.
"""

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": headlines}
            ]
        )
        return response["message"]["content"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama summarization error: {str(e)}")


# ✅ ElevenLabs SDK for high-quality voice generation
def text_to_audio_elevenlabs_sdk(
        text: str,
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        output_dir: str = "audio",
        api_key: str = None
) -> str:
    try:
        api_key = api_key or os.getenv("ELEVEN_API_KEY")
        if not api_key:
            raise ValueError("Missing ElevenLabs API key.")

        client = ElevenLabs(api_key=api_key)
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format
        )

        os.makedirs(output_dir, exist_ok=True)
        filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return filepath

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


# ✅ gTTS fallback for basic TTS if ElevenLabs unavailable
def tts_to_audio(text: str, language: str = 'en') -> str:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = AUDIO_DIR / f"tts_{timestamp}.mp3"
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(filename))
        return str(filename)
    except Exception as e:
        print(f"gTTS Error: {str(e)}")
        return None
