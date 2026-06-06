import os, re, requests
from typing import Optional

def _get_env(key):
    """Read from Streamlit secrets if available, else os.environ."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, ""))
    except Exception:
        return os.getenv(key, "")

BRIGHTDATA_HOST = "brd.superproxy.io"
BRIGHTDATA_PORT = 22225

PROXIES = {
    "http":  f"http://{_get_env('BRIGHTDATA_USER')}:{_get_env('BRIGHTDATA_PASS')}@{BRIGHTDATA_HOST}:{BRIGHTDATA_PORT}",
    "https": f"http://{_get_env('BRIGHTDATA_USER')}:{_get_env('BRIGHTDATA_PASS')}@{BRIGHTDATA_HOST}:{BRIGHTDATA_PORT}",
}

def extract_video_id(url: str) -> Optional[str]:
    patterns = [r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})"]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None

def scrape_youtube_video(url: str) -> dict:
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from: {url}")
    user = _get_env("BRIGHTDATA_USER")
    if user and user != "placeholder" and "your_" not in user:
        try:
            resp = requests.get(
                f"https://www.youtube.com/watch?v={video_id}",
                proxies=PROXIES, verify=False, timeout=30,
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
            )
            resp.raise_for_status()
            return parse_html_metadata(resp.text, video_id)
        except Exception as e:
            print(f"[BrightData] {e} — falling back to YouTube API")
    return fetch_via_youtube_api(video_id)

def parse_html_metadata(html: str, video_id: str) -> dict:
    import json
    title = channel = description = published_at = ""
    view_count = like_count = 0
    m = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            primary = (data.get("contents",{})
                          .get("twoColumnWatchNextResults",{})
                          .get("results",{}).get("results",{})
                          .get("contents",[]))
            for item in primary:
                vp = item.get("videoPrimaryInfoRenderer",{})
                if vp:
                    title = vp.get("title",{}).get("runs",[{}])[0].get("text","")
                    vt = vp.get("viewCount",{}).get("videoViewCountRenderer",{}).get("viewCount",{}).get("simpleText","0")
                    view_count = int(re.sub(r"[^\d]","",vt) or 0)
                    published_at = vp.get("dateText",{}).get("simpleText","")
                vs = item.get("videoSecondaryInfoRenderer",{})
                if vs:
                    channel = (vs.get("owner",{}).get("videoOwnerRenderer",{})
                                 .get("title",{}).get("runs",[{}])[0].get("text",""))
                    description = vs.get("attributedDescription",{}).get("content","")[:1000]
        except Exception as e:
            print(f"[Parser] {e}")
    return {"video_id":video_id,"title":title or f"Video {video_id}","description":description,
            "channel":channel,"view_count":view_count,"like_count":like_count,
            "dislike_count":0,"comment_count":0,"published_at":published_at,
            "url":f"https://www.youtube.com/watch?v={video_id}"}

def fetch_via_youtube_api(video_id: str) -> dict:
    api_key = _get_env("YOUTUBE_API_KEY")
    if not api_key or api_key in ("placeholder","your_youtube_api_key","") or "your_" in api_key:
        return {"video_id":video_id,"title":f"YouTube Video ({video_id})",
                "description":"Add a real YouTube API key to fetch actual data.",
                "channel":"Unknown","view_count":1000000,"like_count":50000,
                "dislike_count":1000,"comment_count":5000,"published_at":"2024-01-01",
                "url":f"https://www.youtube.com/watch?v={video_id}"}
    resp = requests.get("https://www.googleapis.com/youtube/v3/videos",
                        params={"part":"snippet,statistics","id":video_id,"key":api_key},timeout=15)
    resp.raise_for_status()
    items = resp.json().get("items",[])
    if not items:
        raise ValueError(f"No video found for ID: {video_id}")
    item = items[0]
    s, st2 = item.get("snippet",{}), item.get("statistics",{})
    return {"video_id":video_id,"title":s.get("title",""),"description":s.get("description","")[:1000],
            "channel":s.get("channelTitle",""),"view_count":int(st2.get("viewCount",0)),
            "like_count":int(st2.get("likeCount",0)),"dislike_count":0,
            "comment_count":int(st2.get("commentCount",0)),
            "published_at":s.get("publishedAt","")[:10],
            "url":f"https://www.youtube.com/watch?v={video_id}"}

def fetch_transcript(video_id: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        tl = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        langs = ["en","hi","mr","es","ko","tr","fr","de","pt","ar","ja","zh"]
        try:    transcript = tl.find_manually_created_transcript(langs)
        except: 
            try: transcript = tl.find_generated_transcript(langs)
            except:
                for t in tl: transcript = t; break
        if not transcript: return ""
        return " ".join(seg.get("text","") for seg in transcript.fetch())[:8000]
    except Exception as e:
        print(f"[Transcript] {e}")
        return ""
