import json, re, os
from scraper.brightdata import scrape_youtube_video, fetch_transcript


def _get(key):
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, ""))
    except:
        return os.getenv(key, "")


def call_groq(prompt: str, system: str = "") -> str:
    """Call Groq API directly — no CrewAI needed."""
    from groq import Groq
    client = Groq(api_key=_get("GROQ_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def fmt(n):
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    if n >= 1_000:         return f"{n/1_000:.1f}K"
    return str(n)


def derive_sentiment(likes, dislikes, comments, views, title=""):
    if views == 0:
        return 60, 25, 15
    like_rate = (likes / views) * 100
    dislike_rate = (dislikes / views) * 100 if dislikes > 0 else 0
    comment_rate = (comments / views) * 100
    if like_rate > 5:     pos = 80
    elif like_rate > 3:   pos = 72
    elif like_rate > 1.5: pos = 63
    elif like_rate > 0.8: pos = 55
    else:                 pos = 45
    if dislike_rate > 2:   pos -= 20
    elif dislike_rate > 1: pos -= 12
    elif dislike_rate > 0.3: pos -= 6
    if comment_rate > 0.1: pos = min(pos + 5, 90)
    title_lower = title.lower()
    neg_words = ["sad","died","death","crying","heartbreak","broke","fail","worst","hate","exposed"]
    pos_words = ["amazing","winning","love","best","top","awesome","great","incredible","viral"]
    if any(w in title_lower for w in neg_words): pos = max(pos - 10, 30)
    if any(w in title_lower for w in pos_words): pos = min(pos + 8, 88)
    pos = max(30, min(88, pos))
    neg = max(5, min(35, 100 - pos - 20))
    neu = 100 - pos - neg
    return int(pos), int(neu), int(neg)


def derive_views_curve(views, likes):
    if views == 0: return []
    virality = (likes / views) if views > 0 else 0.01
    if virality > 0.04:    weights = [0.02,0.08,0.30,0.60,0.80,0.93,1.0]
    elif virality > 0.02:  weights = [0.03,0.12,0.28,0.48,0.68,0.87,1.0]
    elif virality > 0.008: weights = [0.05,0.18,0.35,0.52,0.70,0.88,1.0]
    else:                  weights = [0.10,0.25,0.42,0.58,0.74,0.88,1.0]
    labels = ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"]
    return [{"date": labels[i], "views": int(views * w)} for i,w in enumerate(weights)]


def run_analysis(url: str) -> dict:
    # ── Scrape ────────────────────────────────────────────
    metadata  = scrape_youtube_video(url)
    video_id  = metadata["video_id"]
    views     = int(metadata.get("view_count", 0))
    likes     = int(metadata.get("like_count", 0))
    dislikes  = int(metadata.get("dislike_count", 0))
    comments  = int(metadata.get("comment_count", 0))
    title     = metadata.get("title", "")
    channel   = metadata.get("channel", "")
    desc      = metadata.get("description", "")

    transcript = fetch_transcript(video_id)
    has_transcript = bool(transcript and len(transcript.strip()) > 100)

    content = f"""
VIDEO TITLE: {title}
CHANNEL: {channel}
DESCRIPTION: {desc[:800] if desc else 'Not available'}
TRANSCRIPT: {transcript[:3000] if has_transcript else 'Not available'}
VIEWS: {views:,} | LIKES: {likes:,} | COMMENTS: {comments:,}
"""

    # ── Agent 1: Detect & Translate ───────────────────────
    lang_result = call_groq(
        prompt=f"Detect the language of this YouTube video content and return ONLY the language name (e.g. English, Hindi, Spanish):\n\nTITLE: {title}\nDESCRIPTION: {desc[:300]}",
        system="You are a language detection expert. Return only the language name, nothing else."
    )
    detected_language = lang_result.strip().split("\n")[0][:30]

    # ── Agent 2: Summarize ────────────────────────────────
    summary = call_groq(
        prompt=(
            f"Write a 3-4 sentence plain English summary of this YouTube video.\n\n{content}\n\n"
            "RULES:\n"
            "- Use ONLY the information provided above\n"
            "- Do NOT invent content\n"
            "- Do NOT add disclaimers or notes\n"
            "- Write directly, no preamble\n"
            "- If transcript is not available, summarize based on title and description only"
        ),
        system="You are a YouTube video summarizer. Write concise, accurate English summaries based only on provided data. Never hallucinate."
    )
    # Clean up any meta-commentary
    lines = [l for l in summary.splitlines()
             if not any(l.lower().startswith(x) for x in ["note:","based on","as provided","i am","here's","here is"])]
    summary = " ".join(lines).strip() or summary.strip()

    # ── Agent 3: Analyze ──────────────────────────────────
    analysis_raw = call_groq(
        prompt=(
            f"Analyze this YouTube video and return ONLY a valid JSON object.\n\n"
            f"TITLE: {title}\nCHANNEL: {channel}\nVIEWS: {views:,}\nLIKES: {likes:,}\n\n"
            "Return this exact JSON structure with no markdown, no explanation:\n"
            '{"topics":["topic1","topic2","topic3","topic4","topic5"],'
            '"trend_score":7.5,'
            '"trend_label":"Trending 🔥",'
            '"sentiment_positive":70,'
            '"sentiment_neutral":20,'
            '"sentiment_negative":10,'
            '"insights":["insight 1","insight 2","insight 3"]}'
        ),
        system="You are a YouTube analytics expert. Return only valid JSON. Base topics and insights on the actual video title provided."
    )

    analysis = {}
    try:
        clean = re.sub(r"```json|```", "", analysis_raw).strip()
        analysis = json.loads(clean)
    except:
        m = re.search(r"\{.*\}", analysis_raw, re.DOTALL)
        if m:
            try: analysis = json.loads(m.group(0))
            except: analysis = {}

    # ── Sentiment ─────────────────────────────────────────
    ai_pos = analysis.get("sentiment_positive")
    ai_neu = analysis.get("sentiment_neutral")
    ai_neg = analysis.get("sentiment_negative")
    if ai_pos and ai_neu and ai_neg and (int(ai_pos)+int(ai_neu)+int(ai_neg)) > 50:
        total = int(ai_pos)+int(ai_neu)+int(ai_neg)
        pos = round(int(ai_pos)*100/total)
        neu = round(int(ai_neu)*100/total)
        neg = 100-pos-neu
    else:
        pos, neu, neg = derive_sentiment(likes, dislikes, comments, views, title)

    # ── Trend Score ───────────────────────────────────────
    trend_score = analysis.get("trend_score")
    if not trend_score:
        eng = ((likes+comments)/views*100) if views > 0 else 0
        if eng > 5:     trend_score = round(8.5+min(eng-5,5)*0.1,1)
        elif eng > 3:   trend_score = round(7.0+(eng-3)*0.5,1)
        elif eng > 1.5: trend_score = round(5.5+(eng-1.5)*0.7,1)
        elif eng > 0.5: trend_score = round(4.0+(eng-0.5)*1.2,1)
        else:           trend_score = round(max(2.0,eng*4),1)

    trend_label = analysis.get("trend_label") or (
        "Viral 🚀" if float(trend_score)>=8.5 else
        "Trending 🔥" if float(trend_score)>=6.5 else
        "Growing 📈" if float(trend_score)>=4.5 else "Steady 📊"
    )

    eng_rate = round(((likes+comments)/views*100),2) if views>0 else 0
    eng_quality = ("Excellent" if eng_rate>5 else "Good" if eng_rate>3 else "Average" if eng_rate>1 else "Low")

    return {
        "title": title, "channel": channel,
        "published_at": metadata.get("published_at",""),
        "url": url, "detected_language": detected_language,
        "views_raw": views, "likes_raw": likes,
        "dislikes_raw": dislikes, "comments_raw": comments,
        "views": fmt(views), "likes": fmt(likes),
        "dislikes": fmt(dislikes), "comments": fmt(comments),
        "engagement_rate": f"{eng_rate}%",
        "engagement_quality": eng_quality,
        "summary": summary,
        "topics": analysis.get("topics",[]),
        "insights": analysis.get("insights",[]),
        "trend_score": trend_score,
        "trend_label": trend_label,
        "sentiment_positive": pos,
        "sentiment_neutral": neu,
        "sentiment_negative": neg,
        "views_over_time": derive_views_curve(views, likes),
        "engagement_breakdown": [
            {"metric":"Likes","value":likes},
            {"metric":"Comments","value":comments},
            {"metric":"Dislikes","value":max(dislikes,0)},
        ],
        "like_view_ratio": f"{round(likes/views*100,2)}%" if views else "—",
        "comment_view_ratio": f"{round(comments/views*100,3)}%" if views else "—",
    }