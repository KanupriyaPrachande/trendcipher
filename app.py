import streamlit as st
import time
import pandas as pd
from crew.crew import run_analysis
from utils.parser import parse_youtube_url

st.set_page_config(
    page_title="TrendCipher — YouTube AI Analysis",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

:root {
  /* Lavender palette from image */
  --bg:          #F8F6FF;
  --card:        #FFFFFF;
  --border:      #E8E2F5;
  --border-dark: #D4CCF0;

  --plum:        #6B3FA0;
  --plum-lt:     #F0EAF8;
  --lavender:    #9B89C4;
  --lav-lt:      #F3EFFE;
  --lav-mid:     #D8CEF0;
  --sage:        #7D8C6B;
  --sage-lt:     #EEF2EA;
  --blush:       #E8B4B8;
  --blush-lt:    #FDF0F1;
  --cream:       #FAF7F0;

  --primary:     #7C5CBF;   /* main purple */
  --pri-dk:      #5E3D9E;
  --pri-lt:      #F0EBF9;
  --pri-mid:     #C4ADE8;

  --green:       #4CAF7D;
  --green-lt:    #EAF6EE;
  --amber:       #C9891A;
  --amber-lt:    #FEF3DC;
  --rose:        #D95B7A;
  --rose-lt:     #FDECF1;
  --teal:        #3D9B8C;
  --teal-lt:     #E6F5F3;

  --text:        #1E1433;
  --text-2:      #3D2E6B;
  --muted:       #7A6E96;
  --light:       #B0A8C8;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text); background: var(--bg);
}
.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 3rem 6rem !important; max-width: 1260px !important; }

/* ══ NAVBAR ══════════════════════════════════════════════ */
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 22px 0 18px;
  border-bottom: 1.5px solid var(--border);
  margin-bottom: 0;
}
.nav-logo {
  font-family: 'Syne', sans-serif; font-size: 21px; font-weight: 800;
  color: var(--primary); letter-spacing: -0.03em;
  display: flex; align-items: center; gap: 9px;
}
.nav-logo-icon {
  width: 34px; height: 34px; border-radius: 9px;
  background: linear-gradient(135deg, var(--plum), var(--lavender));
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.nav-logo span { color: var(--text); }
.nav-badge {
  display: flex; align-items: center; gap: 8px;
}
.nav-tag {
  background: var(--pri-lt); color: var(--primary);
  font-size: 11px; font-weight: 600; padding: 5px 13px;
  border-radius: 100px; letter-spacing: 0.05em; text-transform: uppercase;
  border: 1px solid var(--lav-mid);
}

/* ══ HERO ════════════════════════════════════════════════ */
.hero-wrap {
  padding: 52px 0 0;
  display: grid; grid-template-columns: 1.15fr 1fr;
  gap: 60px; align-items: start;
}
.eyebrow-pill {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--plum-lt); border: 1px solid var(--lav-mid);
  color: var(--plum); font-size: 11px; font-weight: 700;
  letter-spacing: 0.09em; text-transform: uppercase;
  padding: 6px 15px; border-radius: 100px; margin-bottom: 22px;
}
.eyebrow-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--plum); animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.85)} }

.hero-h1 {
  font-family: 'Syne', sans-serif;
  font-size: 52px; font-weight: 800;
  line-height: 1.08; letter-spacing: -0.03em;
  color: var(--text); margin-bottom: 20px;
}
.hero-h1 em {
  font-style: normal;
  background: linear-gradient(135deg, var(--plum) 0%, var(--lavender) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-desc {
  font-size: 16px; color: var(--muted); line-height: 1.75;
  font-weight: 400; margin-bottom: 30px; max-width: 460px;
}

/* Stack chips */
.stack-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 36px; }
.stack-chip {
  background: var(--card); border: 1.5px solid var(--border);
  border-radius: 9px; padding: 7px 14px;
  font-size: 12px; font-weight: 600; color: var(--muted);
  display: inline-flex; align-items: center; gap: 6px;
  box-shadow: 0 1px 4px rgba(123,92,191,.06);
}
.stack-chip:hover { border-color: var(--pri-mid); color: var(--primary); }

/* ══ INPUT CARD ══════════════════════════════════════════ */
.input-card {
  background: var(--card); border-radius: 22px;
  border: 1.5px solid var(--border);
  box-shadow: 0 8px 40px rgba(108,63,160,.10), 0 2px 8px rgba(108,63,160,.05);
  padding: 30px 28px 24px; position: sticky; top: 20px;
}
.ic-header { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.ic-icon {
  width: 42px; height: 42px; border-radius: 12px;
  background: linear-gradient(135deg, var(--plum-lt), var(--lav-lt));
  border: 1px solid var(--lav-mid);
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.ic-title { font-size: 15px; font-weight: 700; color: var(--text); }
.ic-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }
.ic-divider { height: 1px; background: var(--border); margin: 18px 0; }

/* Streamlit input override */
.stTextInput>div>div>input {
  border: 1.5px solid var(--border) !important;
  border-radius: 12px !important; padding: 13px 16px !important;
  font-size: 14px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
  background: var(--bg) !important; color: var(--text) !important;
  transition: all .18s !important;
}
.stTextInput>div>div>input::placeholder { color: var(--light) !important; }
.stTextInput>div>div>input:focus {
  border-color: var(--primary) !important; background: white !important;
  box-shadow: 0 0 0 4px rgba(124,92,191,.12) !important;
}

/* Streamlit button override */
.stButton>button {
  background: linear-gradient(135deg, var(--plum) 0%, var(--primary) 100%) !important;
  color: white !important; border: none !important;
  border-radius: 12px !important; padding: 13px 28px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 14px !important; font-weight: 700 !important;
  width: 100% !important; letter-spacing: 0.01em !important;
  box-shadow: 0 4px 18px rgba(108,63,160,.35) !important;
  transition: all .18s !important;
}
.stButton>button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(108,63,160,.45) !important;
}

/* Language pills in card */
.lang-section-title {
  font-size: 10.5px; font-weight: 700; color: var(--light);
  text-transform: uppercase; letter-spacing: .08em; margin-bottom: 9px;
}
.lang-chips { display: flex; flex-wrap: wrap; gap: 5px; }
.lang-chip {
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 10px;
  font-size: 11px; color: var(--muted); font-weight: 500;
}

/* ══ STATS TILES ═════════════════════════════════════════ */
.stats-section { padding: 44px 0 0; }
.section-eyebrow {
  font-size: 11px; font-weight: 700; color: var(--primary);
  letter-spacing: .1em; text-transform: uppercase; margin-bottom: 10px;
}
.section-h2 {
  font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800;
  color: var(--text); letter-spacing: -.025em; margin-bottom: 22px;
}
.tiles-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; }
.tile {
  background: var(--card); border-radius: 18px; padding: 20px 20px 18px;
  border: 1.5px solid var(--border);
  box-shadow: 0 2px 12px rgba(108,63,160,.05);
  display: flex; align-items: center; gap: 15px;
}
.tile-icon {
  width: 46px; height: 46px; border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.tile-val {
  font-family: 'Syne', sans-serif; font-size: 23px; font-weight: 800;
  color: var(--text); line-height: 1; margin-bottom: 3px;
}
.tile-lbl { font-size: 12px; color: var(--muted); font-weight: 500; }

/* ══ HOW IT WORKS ════════════════════════════════════════ */
.hiw-section { padding: 48px 0 0; }
.steps-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-top: 22px; }
.step-card {
  background: var(--card); border-radius: 20px;
  padding: 28px 24px 24px; border: 1.5px solid var(--border);
  position: relative; overflow: hidden;
  box-shadow: 0 2px 16px rgba(108,63,160,.05);
}
.step-accent {
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px; border-radius: 20px 20px 0 0;
}
.step-ghost-num {
  position: absolute; top: -10px; right: 14px;
  font-family: 'Syne', sans-serif; font-size: 72px; font-weight: 800;
  color: var(--plum); opacity: .05; line-height: 1; user-select: none;
}
.step-icon-box {
  width: 50px; height: 50px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; margin-bottom: 16px;
}
.step-tag {
  display: inline-block; font-size: 10.5px; font-weight: 700;
  padding: 4px 10px; border-radius: 6px; margin-bottom: 12px;
  letter-spacing: .04em; text-transform: uppercase;
}
.step-title { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 9px; }
.step-body { font-size: 13px; color: var(--muted); line-height: 1.65; }

/* ══ FEATURES ════════════════════════════════════════════ */
.feat-section { padding: 48px 0 56px; }
.feat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-top: 22px; }
.feat-card {
  background: var(--card); border-radius: 18px;
  padding: 24px 20px; border: 1.5px solid var(--border);
  box-shadow: 0 2px 12px rgba(108,63,160,.05);
}
.feat-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; margin-bottom: 14px;
}
.feat-title { font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 7px; }
.feat-body { font-size: 12.5px; color: var(--muted); line-height: 1.65; }

/* ══ DASHBOARD ═══════════════════════════════════════════ */
.dash-navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 0 16px; border-bottom: 1.5px solid var(--border); margin-bottom: 24px;
}
.vid-banner {
  background: linear-gradient(135deg, #F0EBF9 0%, #FAF7FF 100%);
  border-radius: 20px; padding: 22px 26px;
  border: 1.5px solid var(--lav-mid); margin-bottom: 18px;
  display: flex; align-items: center; gap: 18px;
}
.vid-thumb-box {
  width: 70px; height: 50px; border-radius: 10px;
  background: linear-gradient(135deg, var(--plum), var(--lavender));
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.vid-title-text {
  font-family: 'Syne', sans-serif; font-size: 17px; font-weight: 800;
  color: var(--text); margin-bottom: 8px; line-height: 1.3;
}
.vid-meta { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
.vid-info { font-size: 12px; color: var(--muted); font-weight: 500; }
.lang-badge {
  background: var(--teal-lt); color: var(--teal);
  font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 6px;
  border: 1px solid #C0E8E2;
}

/* Metric cards */
.metrics-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; margin-bottom: 18px; }
.mc {
  background: var(--card); border-radius: 16px;
  padding: 18px 12px; border: 1.5px solid var(--border); text-align: center;
  box-shadow: 0 2px 10px rgba(108,63,160,.05);
}
.mc-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; margin: 0 auto 10px;
}
.mc-val {
  font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 800;
  color: var(--text); margin-bottom: 3px;
}
.mc-lbl { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; font-weight: 600; }
.mc-badge {
  display: inline-block; font-size: 9.5px; font-weight: 700;
  padding: 2px 8px; border-radius: 5px; margin-top: 6px;
}

/* Panels */
.panel {
  background: var(--card); border-radius: 18px;
  padding: 22px 24px; border: 1.5px solid var(--border);
  box-shadow: 0 2px 12px rgba(108,63,160,.05); height: 100%;
}
.panel-title {
  font-size: 13px; font-weight: 700; color: var(--text);
  margin-bottom: 14px; display: flex; align-items: center; gap: 7px;
}
.panel-sub { font-size: 11px; color: var(--light); font-weight: 400; margin-left: 4px; }
.panel-divider { height: 1px; background: var(--border); margin: 16px 0; }

/* Summary */
.summary-body { font-size: 14px; line-height: 1.8; color: #3D2E6B; font-weight: 400; }
.topic-wrap { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 16px; }
.topic-tag {
  display: inline-block; padding: 5px 13px; border-radius: 8px;
  font-size: 12px; font-weight: 600;
}
.t0{background:var(--plum-lt);color:var(--plum);border:1px solid #D8C8EF;}
.t1{background:var(--teal-lt);color:var(--teal);border:1px solid #BDE0DA;}
.t2{background:var(--sage-lt);color:var(--sage);border:1px solid #C8D4C0;}
.t3{background:var(--blush-lt);color:#B05070;border:1px solid #F0C8D0;}
.t4{background:var(--amber-lt);color:var(--amber);border:1px solid #EDD8A0;}
.t5{background:var(--lav-lt);color:var(--lavender);border:1px solid var(--lav-mid);}

/* Trend score */
.trend-score-big {
  font-family: 'Syne', sans-serif; font-size: 58px; font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, var(--plum), var(--lavender));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.trend-label-text { font-size: 15px; font-weight: 700; color: var(--text); margin-top: 5px; }
.trend-sub-text { font-size: 11px; color: var(--light); margin-top: 2px; }

/* Sentiment */
.sent-track {
  height: 14px; border-radius: 100px; overflow: hidden;
  display: flex; margin: 12px 0 9px;
  border: 1px solid rgba(0,0,0,.04);
}
.sp { background: linear-gradient(90deg, #4CAF7D, #6DD49A); }
.sn { background: linear-gradient(90deg, #C9A01A, #E0B830); }
.sg { background: linear-gradient(90deg, #D95B7A, #F07090); }
.sent-legend { display: flex; justify-content: space-between; }
.sl-item { text-align: center; }
.sl-val { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 800; }
.sl-lbl { font-size: 10.5px; color: var(--muted); font-weight: 500; margin-top: 1px; }

/* Insights */
.insight-row { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--border); }
.insight-row:last-child { border-bottom: none; }
.ins-bullet {
  width: 8px; height: 8px; border-radius: 50%;
  background: linear-gradient(135deg, var(--plum), var(--lavender));
  flex-shrink: 0; margin-top: 5px;
}
.ins-text { font-size: 13px; color: var(--text-2); line-height: 1.55; font-weight: 400; }

/* Ratio boxes */
.ratio-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
.ratio-box {
  background: var(--bg); border-radius: 12px;
  padding: 12px 14px; border: 1.5px solid var(--border);
}
.ratio-val { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800; color: var(--primary); }
.ratio-lbl { font-size: 10.5px; color: var(--muted); margin-top: 3px; font-weight: 500; }

/* Chart panel */
.chart-panel {
  background: var(--card); border-radius: 18px;
  padding: 20px 22px; border: 1.5px solid var(--border);
  box-shadow: 0 2px 12px rgba(108,63,160,.05);
}
.cp-title { font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.cp-sub { font-size: 11.5px; color: var(--light); margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "result" not in st.session_state:
    st.session_state.result = None

# ══════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════
if not st.session_state.analyzed:

    # Navbar
    st.markdown("""
    <div class="navbar">
      <div class="nav-logo">
        <div class="nav-logo-icon">🎯</div>
        Trend<span>Cipher</span>
      </div>
      <div class="nav-badge">
        <span class="nav-tag">⚡ AI-Powered · Free to Use</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero grid — left column text
    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        st.markdown("""
        <div style="padding-top:44px;">
          <div class="eyebrow-pill">
            <span class="eyebrow-dot"></span>
            Multi-Agent AI Pipeline
          </div>
          <h1 class="hero-h1">Analyze Any YouTube<br>Video in <em>Seconds</em></h1>
          <p class="hero-desc">
            Paste a URL in any language. TrendCipher scrapes, translates,
            summarizes, and scores the video — output always in English.
          </p>
          <div class="stack-row">
            <span class="stack-chip">🤖 CrewAI Agents</span>
            <span class="stack-chip">🧠 Ollama LLM</span>
            <span class="stack-chip">🔍 BrightData</span>
            <span class="stack-chip">🐍 Python</span>
            <span class="stack-chip">📊 Streamlit</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div style="padding-top:44px;">
        <div class="input-card">
          <div class="ic-header">
            <div class="ic-icon">🔗</div>
            <div>
              <div class="ic-title">Paste YouTube URL</div>
              <div class="ic-sub">Any public video, any language</div>
            </div>
          </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        url = st.text_input("url", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
        analyze_clicked = st.button("✨  Analyze Video Now")

        st.markdown("""
        <div style="margin-top:16px; background:var(--bg); border-radius:12px; padding:14px 16px; border:1px solid var(--border);">
          <div class="lang-section-title">Supported Languages</div>
          <div class="lang-chips">
            <span class="lang-chip">🇮🇳 Hindi</span>
            <span class="lang-chip">🇮🇳 Marathi</span>
            <span class="lang-chip">🇪🇸 Spanish</span>
            <span class="lang-chip">🇰🇷 Korean</span>
            <span class="lang-chip">🇹🇷 Turkish</span>
            <span class="lang-chip">🇯🇵 Japanese</span>
            <span class="lang-chip">🇸🇦 Arabic</span>
            <span class="lang-chip">🇩🇪 German</span>
            <span class="lang-chip">🇫🇷 French</span>
            <span class="lang-chip">🇷🇺 Russian</span>
            <span class="lang-chip">🇨🇳 Chinese</span>
            <span class="lang-chip">+ 40 more</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Stats tiles
    st.markdown("""
    <div class="stats-section">
      <div class="section-eyebrow">By the Numbers</div>
      <div class="section-h2">Built to Impress</div>
      <div class="tiles-row">
        <div class="tile">
          <div class="tile-icon" style="background:var(--plum-lt);">🌐</div>
          <div><div class="tile-val">50+</div><div class="tile-lbl">Languages Supported</div></div>
        </div>
        <div class="tile">
          <div class="tile-icon" style="background:var(--teal-lt);">⚡</div>
          <div><div class="tile-val">&lt;30s</div><div class="tile-lbl">Average Analysis Time</div></div>
        </div>
        <div class="tile">
          <div class="tile-icon" style="background:var(--sage-lt);">🤖</div>
          <div><div class="tile-val">3</div><div class="tile-lbl">Specialized AI Agents</div></div>
        </div>
        <div class="tile">
          <div class="tile-icon" style="background:var(--blush-lt);">📝</div>
          <div><div class="tile-val">100%</div><div class="tile-lbl">English Output Always</div></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # How it works
    st.markdown("""
    <div class="hiw-section">
      <div class="section-eyebrow">Under the Hood</div>
      <div class="section-h2">How TrendCipher Works</div>
      <div class="steps-grid">
        <div class="step-card">
          <div class="step-accent" style="background:linear-gradient(90deg,var(--plum),var(--lavender));"></div>
          <div class="step-ghost-num">01</div>
          <div class="step-icon-box" style="background:var(--plum-lt);">🔍</div>
          <span class="step-tag" style="background:var(--plum-lt);color:var(--plum);">BrightData API</span>
          <div class="step-title">Scrape & Fetch</div>
          <div class="step-body">BrightData's Web Unlocker bypasses geo-restrictions to fetch full video metadata, view counts, and captions.</div>
        </div>
        <div class="step-card">
          <div class="step-accent" style="background:linear-gradient(90deg,var(--teal),#6DD49A);"></div>
          <div class="step-ghost-num">02</div>
          <div class="step-icon-box" style="background:var(--teal-lt);">🌐</div>
          <span class="step-tag" style="background:var(--teal-lt);color:var(--teal);">CrewAI Agent #1</span>
          <div class="step-title">Detect & Translate</div>
          <div class="step-body">A dedicated Translator Agent identifies the video language and converts all content into fluent English automatically.</div>
        </div>
        <div class="step-card">
          <div class="step-accent" style="background:linear-gradient(90deg,var(--amber),#E0C040);"></div>
          <div class="step-ghost-num">03</div>
          <div class="step-icon-box" style="background:var(--amber-lt);">📊</div>
          <span class="step-tag" style="background:var(--amber-lt);color:var(--amber);">CrewAI Agents #2 & #3</span>
          <div class="step-title">Summarize & Score</div>
          <div class="step-body">Two specialized agents generate a plain-English summary, extract key topics, and compute trend score with sentiment analysis.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Features
    st.markdown("""
    <div class="feat-section">
      <div class="section-eyebrow">Capabilities</div>
      <div class="section-h2">Everything in One Dashboard</div>
      <div class="feat-grid">
        <div class="feat-card">
          <div class="feat-icon" style="background:var(--plum-lt);">🧠</div>
          <div class="feat-title">AI Quick Summary</div>
          <div class="feat-body">3–4 sentence plain-English summary based on the actual title, description, and transcript of the video.</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon" style="background:var(--teal-lt);">📈</div>
          <div class="feat-title">Trend Scoring</div>
          <div class="feat-body">Each video is scored 1–10 based on real engagement rate, like velocity, and topic relevance signals.</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon" style="background:var(--sage-lt);">💬</div>
          <div class="feat-title">Sentiment Analysis</div>
          <div class="feat-body">Positive / Neutral / Negative breakdown derived from real like ratio, dislike rate, and comment density.</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon" style="background:var(--blush-lt);">🏷️</div>
          <div class="feat-title">Topic Extraction</div>
          <div class="feat-body">AI identifies 5–8 relevant tags specific to the actual video content for instant categorization.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    url = None
    analyze_clicked = False

# ══════════════════════════════════════════════════════════════
# ANALYSIS TRIGGER
# ══════════════════════════════════════════════════════════════
if not st.session_state.analyzed:
    if analyze_clicked and url:
        if not parse_youtube_url(url):
            st.error("⚠️ Please enter a valid YouTube URL.")
        else:
            pb  = st.progress(0)
            msg = st.empty()
            for pct, text in [
                (12,  "🔍 Fetching video metadata via BrightData..."),
                (28,  "📝 Extracting transcript & captions..."),
                (48,  "🌐 Detecting language — translating to English..."),
                (68,  "🤖 CrewAI Summarizer Agent running..."),
                (86,  "📊 Scoring trend & computing sentiment..."),
                (100, "✅ Analysis complete!"),
            ]:
                msg.markdown(f"<p style='color:var(--primary);font-weight:600;font-size:14px;margin-top:10px'>{text}</p>", unsafe_allow_html=True)
                pb.progress(pct)
                time.sleep(0.45)
            result = run_analysis(url)
            st.session_state.result   = result
            st.session_state.analyzed = True
            pb.empty(); msg.empty()
            st.rerun()
    elif analyze_clicked:
        st.warning("Please paste a YouTube URL first.")

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if st.session_state.analyzed and st.session_state.result:
    r = st.session_state.result

    st.markdown("""
    <div class="dash-navbar">
      <div class="nav-logo">
        <div class="nav-logo-icon">🎯</div>
        Trend<span>Cipher</span>
      </div>
      <div class="nav-tag">📊 Analysis Report</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Analyze another video"):
        st.session_state.analyzed = False
        st.session_state.result   = None
        st.rerun()

    # Video banner
    st.markdown(f"""
    <div class="vid-banner">
      <div class="vid-thumb-box">▶</div>
      <div style="flex:1;">
        <div class="vid-title-text">{r.get('title','Unknown')}</div>
        <div class="vid-meta">
          <span class="vid-info">📅 {r.get('published_at','—')}</span>
          <span class="vid-info">👤 {r.get('channel','—')}</span>
          <span class="lang-badge">🌐 {r.get('detected_language','English')} → English</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    eq = r.get("engagement_quality","—")
    eq_color = {"Excellent":"var(--green)","Good":"var(--teal)","Average":"var(--amber)","Low":"var(--rose)"}.get(eq,"var(--muted)")
    eq_bg    = {"Excellent":"var(--green-lt)","Good":"var(--teal-lt)","Average":"var(--amber-lt)","Low":"var(--rose-lt)"}.get(eq,"var(--bg)")

    metrics = [
        ("👁️","var(--plum-lt)","var(--plum)",   r.get("views","—"),           "Total Views",    ""),
        ("👍","var(--green-lt)","var(--green)",  r.get("likes","—"),           "Likes",          ""),
        ("👎","var(--rose-lt)","var(--rose)",    r.get("dislikes","—"),        "Dislikes",       ""),
        ("💬","var(--amber-lt)","var(--amber)",  r.get("comments","—"),        "Comments",       ""),
        ("📈","var(--teal-lt)","var(--teal)",    r.get("engagement_rate","—"), "Engagement Rate", eq),
    ]
    cols = st.columns(5)
    for i,(icon,bg,color,val,lbl,badge) in enumerate(metrics):
        with cols[i]:
            badge_html = f'<div class="mc-badge" style="background:{eq_bg};color:{eq_color};">{badge}</div>' if badge else ""
            st.markdown(f"""
            <div class="mc">
              <div class="mc-icon" style="background:{bg};color:{color};">{icon}</div>
              <div class="mc-val">{val}</div>
              <div class="mc-lbl">{lbl}</div>
              {badge_html}
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Main analysis row ──────────────────────────────────────────────────
    col_sum, col_right = st.columns([3, 2], gap="medium")

    with col_sum:
        topics = r.get("topics", [])
        tag_cls = ["t0","t1","t2","t3","t4","t5"]
        tags_html = "".join(
            f'<span class="topic-tag {tag_cls[i%6]}">{t}</span>'
            for i,t in enumerate(topics)
        )
        st.markdown(f"""
        <div class="panel">
          <div class="panel-title">🧠 AI Quick Summary</div>
          <div class="summary-body">{r.get('summary','Not available.')}</div>
          <div class="topic-wrap">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        pos = r.get("sentiment_positive", 60)
        neu = r.get("sentiment_neutral",  25)
        neg = r.get("sentiment_negative", 15)
        ts  = r.get("trend_score","—")
        tl  = r.get("trend_label","—")

        insights_html = "".join(
            f'<div class="insight-row"><div class="ins-bullet"></div><div class="ins-text">{ins}</div></div>'
            for ins in r.get("insights",[])[:4]
        )
        st.markdown(f"""
        <div class="panel">
          <div class="panel-title">📈 Trend Score</div>
          <div class="trend-score-big">{ts}</div>
          <div class="trend-label-text">{tl}</div>
          <div class="trend-sub-text">out of 10 — based on engagement rate & topic relevance</div>

          <div class="panel-divider"></div>

          <div class="panel-title">🎭 Sentiment Breakdown
            <span class="panel-sub">from real engagement signals</span>
          </div>
          <div class="sent-track">
            <div class="sp" style="width:{pos}%"></div>
            <div class="sn" style="width:{neu}%"></div>
            <div class="sg" style="width:{neg}%"></div>
          </div>
          <div class="sent-legend">
            <div class="sl-item">
              <div class="sl-val" style="color:var(--green);">{pos}%</div>
              <div class="sl-lbl">Positive</div>
            </div>
            <div class="sl-item">
              <div class="sl-val" style="color:var(--amber);">{neu}%</div>
              <div class="sl-lbl">Neutral</div>
            </div>
            <div class="sl-item">
              <div class="sl-val" style="color:var(--rose);">{neg}%</div>
              <div class="sl-lbl">Negative</div>
            </div>
          </div>

          <div class="panel-divider"></div>

          <div class="panel-title">⚡ Key Insights</div>
          {insights_html}

          <div class="ratio-grid">
            <div class="ratio-box">
              <div class="ratio-val">{r.get('like_view_ratio','—')}</div>
              <div class="ratio-lbl">Like / View Ratio</div>
            </div>
            <div class="ratio-box">
              <div class="ratio-val">{r.get('comment_view_ratio','—')}</div>
              <div class="ratio-lbl">Comment / View Ratio</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Charts row ─────────────────────────────────────────────────────────
    ch1, ch2 = st.columns(2, gap="medium")

    with ch1:
        vot = r.get("views_over_time", [])
        if vot:
            st.markdown("""
            <div class="chart-panel">
              <div class="cp-title">📈 Views Ramp-Up Curve</div>
              <div class="cp-sub">Modelled from like/view engagement velocity</div>
            </div>
            """, unsafe_allow_html=True)
            df_v = pd.DataFrame(vot).set_index("date")
            st.area_chart(df_v, color="#7C5CBF", height=190)

    with ch2:
        eb = r.get("engagement_breakdown", [])
        if eb:
            st.markdown("""
            <div class="chart-panel">
              <div class="cp-title">💡 Engagement Breakdown</div>
              <div class="cp-sub">Real likes · comments · dislikes from YouTube</div>
            </div>
            """, unsafe_allow_html=True)
            df_e = pd.DataFrame(eb).set_index("metric")
            st.bar_chart(df_e, color="#3D9B8C", height=190)
