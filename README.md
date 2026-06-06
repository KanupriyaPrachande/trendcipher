# 🎯 TrendCipher — YouTube Trend Analysis

> AI-powered YouTube video analysis. Paste any URL (any language) → get English summary, sentiment, trends, and engagement analytics.

---

## ✨ Features

- 🌐 **50+ Languages Supported** — Hindi, Marathi, Spanish, Korean, Turkish, French, and more. Output is always English.
- 🤖 **CrewAI Agents** — 3 specialized agents: Translator, Summarizer, Analyst
- 🧠 **Local AI (Ollama)** — runs llama3 or mistral locally, no OpenAI costs
- 📊 **Beautiful Dashboard** — light theme, metrics, charts, sentiment, trend score
- 🔍 **BrightData Scraper** — bypasses blocks, fetches real YouTube metadata

---

## 🗂️ Project Structure

```
trendcipher/
├── app.py                  # Streamlit UI (entry point)
├── crew/
│   ├── agents.py           # CrewAI agent definitions
│   ├── tasks.py            # CrewAI task definitions
│   └── crew.py             # Orchestrator & result builder
├── scraper/
│   └── brightdata.py       # BrightData + YouTube API scraper
├── utils/
│   └── parser.py           # URL validation
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Day 1 — Setup & Backend

### 1. Prerequisites

```bash
# Python 3.11+
python --version

# Install Ollama (Mac/Linux)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3          # or: ollama pull mistral

# Verify Ollama is running
ollama run llama3 "say hello"
```

### 2. Clone & Install

```bash
git clone <your-repo>
cd trendcipher

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. BrightData Setup

1. Sign up at [brightdata.com](https://brightdata.com)
2. Go to **Proxies** → **Web Unlocker** → Create a zone
3. Copy your `username` and `password` into `.env`

```
BRIGHTDATA_USER=brd-customer-XXXX-zone-XXXX
BRIGHTDATA_PASS=your_password
```

### 5. YouTube API Key (fallback)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Enable **YouTube Data API v3**
3. Create API Key → copy to `.env`

---

## 🚀 Day 2 — Run & Deploy

### Run Locally

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### Deploy to Streamlit Cloud (Recommended over Vercel for Python)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → set `app.py` as entry point
4. Add secrets in **Advanced settings** → paste your `.env` contents

> ⚠️ **Vercel does not support Python backends well.** Use **Streamlit Cloud** (free) or **Railway** instead.

### Deploy to Railway (alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

Add env vars in the Railway dashboard.

---

## 🧠 How the AI Pipeline Works

```
YouTube URL
    ↓
[BrightData Scraper] → title, description, stats
    ↓
[youtube-transcript-api] → raw transcript (any language)
    ↓
[CrewAI Agent 1: Translator]
  → Detects language
  → Translates everything to English
    ↓
[CrewAI Agent 2: Summarizer]
  → Reads English content
  → Writes 3-5 sentence summary
    ↓
[CrewAI Agent 3: Analyst]
  → Extracts key topics
  → Calculates trend score
  → Estimates sentiment
  → Generates insights
    ↓
[Streamlit Dashboard]
  → Metrics, charts, summary, sentiment bar
```

---

## 🔧 Customization

**Change the Ollama model:**
```bash
ollama pull mistral
# .env → OLLAMA_MODEL=mistral
```

**Change summary length:** Edit `tasks.py` → `summarize_task` description.

**Add more languages:** The translator agent handles them automatically — no config needed.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Frontend UI |
| `crewai` | Multi-agent orchestration |
| `langchain-ollama` | Ollama LLM integration |
| `youtube-transcript-api` | Transcript fetching |
| `requests` | BrightData HTTP requests |
| `pandas` | Chart data |
| `python-dotenv` | Env config |

---

## 🤝 Support

Built with ❤️ — TrendCipher — multilingual YouTube trend analysis in seconds.
