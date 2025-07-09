# NewsBriefly — Real-Time News & Reddit Summarizer using Open Source LLMs

NewsBriefly is a powerful full-stack AI application that automatically scrapes the latest news headlines and Reddit discussions, summarizes them using local LLMs (like LLaMA 3 via Ollama), and presents them in a clean, podcast-ready format.

⚡ Built completely on **free, local, open-source models** — no API fees, no cloud lock-in.  
🎙️ Originally designed for audio TTS, now focused on **text-based summarization** from real-time data.

---

## 🚀 Live Demo (Optional GIF Preview)

![NewsBriefly Demo](demo.gif)

---

## 📌 What This Project Does

-  **Scrapes real-time news** from Google News for user-selected topics
-  **Searches and summarizes top Reddit discussions**
-  **Generates human-like summaries** using LLaMA 3 (via Ollama) on your own machine
-  Provides everything via a sleek **Streamlit frontend** and **FastAPI backend**
-  **No paid APIs** like OpenAI or Anthropic — 100% open-source or free alternatives

---

## 🧠 Skills and Technologies Showcased

| Domain | Tools / Concepts |
|--------|------------------|
| **Frontend** | Streamlit, UI state management, modular layout |
| **Backend** | FastAPI, async APIs, REST design |
| **AI/ML** | LLM-based summarization using [LLaMA 3](https://ollama.com/library/llama3), prompt engineering |
| **Scraping** | Google News (custom query), Reddit via `serper.dev`, `BeautifulSoup` |
| **Environment** | `.env`, dotenv, modular codebase |
| **Deployment Ready** | Clean architecture with `utils.py`, `models.py`, `news_scraper.py`, `reddit_scraper.py` |
| **Open Source Stack** | Ollama, LangChain, gTTS/ElevenLabs (optional), Python 3.10+, Serper API |

---
##  Author
Made with passion by Deepak Sethi
 B.Tech in ECE | AI/ML + NLP Enthusiast | FastAPI & LLMs Explorer
 dpksethiii@gmail.com

## 🏗️ Project Structure

```bash
NewsNinja/
├── backend.py              # FastAPI server
├── frontend_app.py         # Streamlit app
├── utils.py                # Core logic: scraping, summarization, TTS
├── news_scraper.py         # News scraping logic
├── reddit_scraper.py       # Reddit scraping + summarization
├── models.py               # Pydantic schema
├── .env                    # API keys
├── requirements.txt
├── README.md
└── demo.gif

