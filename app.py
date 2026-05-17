import streamlit as st
from groq import Groq
import json
import re
from datetime import datetime
import pytz
from supabase import create_client, Client

st.set_page_config(page_title="AutoJournal · Cipher Ghost", page_icon="👁️", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Montserrat:wght@300;400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Oswald:wght@300;400;500;600&family=Dancing+Script:wght@600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #f8f5f0 !important;
    color: #1a1a2e !important;
  }
  .main .block-container { padding: 0 0.8rem 4rem 0.8rem; max-width: 480px; margin: 0 auto; }
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="collapsedControl"] { display: none; }

  /* ── HERO ── */
  .cg-hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2.5rem 1.5rem 2rem 1.5rem;
    text-align: center;
    margin: 0 -0.8rem 1.5rem -0.8rem;
    position: relative;
    overflow: hidden;
  }
  .cg-hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(212,175,55,0.2) 0%, transparent 70%);
  }
  .cg-hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem; font-weight: 900;
    color: #d4af37;
    letter-spacing: 0.12em;
    margin: 0; line-height: 1.1;
    text-shadow: 0 2px 20px rgba(212,175,55,0.4);
  }
  .cg-hero .sub {
    font-family: 'Oswald', sans-serif;
    font-size: 0.65rem; color: rgba(255,255,255,0.5);
    letter-spacing: 0.4em; margin-top: 0.4rem;
    text-transform: uppercase;
  }
  .cg-date-pill {
    display: inline-block;
    background: rgba(212,175,55,0.15);
    border: 1px solid rgba(212,175,55,0.4);
    border-radius: 30px; padding: 0.3rem 1.1rem;
    font-family: 'Oswald', sans-serif;
    font-size: 0.7rem; color: #d4af37;
    letter-spacing: 0.12em; margin-top: 0.8rem;
  }

  /* ── CARDS ── */
  .card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.3rem 1.2rem 1rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    border-top: 4px solid #ccc;
  }
  .card-general { border-top-color: #6c63ff; }
  .card-vision  { border-top-color: #d4af37; }
  .card-prayer  { border-top-color: #4a90d9; }
  .card-devotion{ border-top-color: #9b59b6; }
  .card-habit   { border-top-color: #27ae60; }
  .card-gratitude{ border-top-color: #e67e22; }
  .card-health  { border-top-color: #e74c3c; }
  .card-motivation{ border-top-color: #1abc9c; }

  /* ── CARD HEADERS ── */
  .card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem; font-weight: 700;
    margin: 0 0 1rem 0; letter-spacing: 0.02em;
  }
  .title-general  { color: #6c63ff; }
  .title-vision   { color: #d4af37; }
  .title-prayer   { color: #4a90d9; }
  .title-devotion { color: #9b59b6; }
  .title-habit    { color: #27ae60; }
  .title-gratitude{ color: #e67e22; }
  .title-health   { color: #e74c3c; }
  .title-motivation{ color: #1abc9c; }

  /* ── FIELD LABELS ── */
  .fl {
    font-family: 'Oswald', sans-serif;
    font-size: 0.62rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: #999;
    margin-bottom: 0.15rem; margin-top: 0.6rem;
  }
  .fv {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem; color: #2c3e50;
    line-height: 1.5; padding-left: 0.6rem;
    border-left: 3px solid #eee;
    margin-bottom: 0.3rem;
  }
  .fv-accent {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700;
    color: #1a1a2e; padding-left: 0.6rem;
    border-left: 3px solid #d4af37;
    margin-bottom: 0.3rem;
  }

  /* ── MOOD BADGE ── */
  .mood-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6c63ff, #a855f7);
    color: white; border-radius: 20px;
    padding: 0.3rem 1rem;
    font-family: 'Oswald', sans-serif;
    font-size: 0.85rem; letter-spacing: 0.1em;
    font-weight: 500;
  }

  /* ── VISION ── */
  .vision-quote {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem; font-style: italic;
    color: #2c3e50; line-height: 1.7;
    padding: 0.8rem 1rem;
    background: linear-gradient(135deg, #fffdf5, #fff9e6);
    border-left: 4px solid #d4af37;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.8rem;
  }
  .goal-item {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.82rem; color: #555;
    padding: 0.3rem 0 0.3rem 1rem;
    border-bottom: 1px solid #f5f5f5;
    display: flex; align-items: center; gap: 0.5rem;
  }
  .goal-dot { color: #d4af37; font-size: 0.6rem; }
  .affirmation-item {
    font-family: 'Dancing Script', cursive;
    font-size: 1.05rem; color: #6c63ff;
    padding: 0.2rem 0 0.2rem 0.5rem;
    border-left: 2px solid rgba(108,99,255,0.2);
    margin-bottom: 0.3rem;
  }

  /* ── VERSE ── */
  .verse-box {
    background: linear-gradient(135deg, #eef4fb, #e8f3ff);
    border-radius: 10px; padding: 0.9rem 1rem;
    border-left: 4px solid #4a90d9;
    margin-bottom: 0.7rem;
  }
  .verse-ref {
    font-family: 'Oswald', sans-serif;
    font-size: 0.75rem; color: #4a90d9;
    letter-spacing: 0.1em; margin-bottom: 0.3rem;
  }
  .verse-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem; font-style: italic;
    color: #1a3a5c; line-height: 1.6;
  }
  .prayer-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.98rem; color: #2c3e50;
    line-height: 1.7; font-style: italic;
    padding: 0.5rem 0;
  }

  /* ── SUNDAY BADGE ── */
  .sunday-badge {
    background: linear-gradient(135deg, #9b59b6, #8e44ad);
    color: white; border-radius: 6px;
    padding: 0.25rem 0.8rem;
    font-family: 'Oswald', sans-serif;
    font-size: 0.65rem; letter-spacing: 0.18em;
    display: inline-block; margin-bottom: 0.8rem;
  }

  /* ── HABITS ── */
  .habit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 0.5rem; }
  .habit-card {
    border-radius: 10px; padding: 0.7rem 0.8rem;
    display: flex; align-items: center; gap: 0.5rem;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.78rem; font-weight: 600;
    border: 2px solid transparent;
  }
  .habit-done-card { background: #eafaf1; border-color: #27ae60; color: #1e8449; }
  .habit-skip-card { background: #fdf2f2; border-color: #e74c3c; color: #c0392b; }
  .habit-na-card   { background: #f8f9fa; border-color: #ddd; color: #aaa; }
  .habit-icon { font-size: 1rem; }
  .habit-journal-area {
    background: #f8f9fa; border: 1px solid #e9ecef;
    border-radius: 8px; padding: 0.6rem 0.8rem;
    margin-top: 0.5rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.92rem; color: #555; line-height: 1.5;
  }
  .habit-journal-label {
    font-family: 'Oswald', sans-serif;
    font-size: 0.6rem; letter-spacing: 0.15em;
    color: #27ae60; text-transform: uppercase;
    margin-bottom: 0.3rem;
  }

  /* ── GRATITUDE ── */
  .grat-item {
    display: flex; gap: 0.8rem; align-items: flex-start;
    padding: 0.6rem 0; border-bottom: 1px solid #fef0e6;
  }
  .grat-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem; font-weight: 900; color: #e67e22;
    min-width: 1.5rem; line-height: 1;
  }
  .grat-text { font-family: 'Cormorant Garamond', serif; font-size: 1rem; color: #2c3e50; line-height: 1.4; }
  .word-box {
    background: linear-gradient(135deg, #fff8f0, #fff3e6);
    border-radius: 10px; padding: 0.8rem 1rem;
    border-left: 4px solid #e67e22; margin: 0.7rem 0;
  }
  .word-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem; font-weight: 700; color: #e67e22;
  }
  .word-def { font-family: 'Cormorant Garamond', serif; font-size: 0.95rem; color: #555; font-style: italic; }
  .lesson-box {
    background: #f8f5ff; border-radius: 10px;
    padding: 0.8rem 1rem; border-left: 4px solid #6c63ff;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem; color: #2c3e50; font-style: italic; line-height: 1.6;
  }

  /* ── HEALTH / FOOD ── */
  .food-rec {
    background: linear-gradient(135deg, #fef9f9, #fff0f0);
    border-radius: 10px; padding: 0.9rem 1rem;
    border-left: 4px solid #e74c3c; margin-bottom: 0.7rem;
  }
  .food-title {
    font-family: 'Oswald', sans-serif;
    font-size: 0.7rem; color: #e74c3c;
    letter-spacing: 0.15em; margin-bottom: 0.4rem;
  }
  .food-meal {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.82rem; color: #333; font-weight: 500;
    padding: 0.25rem 0; display: flex; align-items: center; gap: 0.4rem;
  }
  .health-stat {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.5rem 0.8rem; border-radius: 8px;
    background: #f8f9fa; margin-bottom: 0.4rem;
    font-family: 'Montserrat', sans-serif; font-size: 0.83rem;
  }
  .health-icon { font-size: 1.1rem; }

  /* ── MOTIVATION ── */
  .motivation-box {
    background: linear-gradient(135deg, #e8fdf8, #d5f5ee);
    border-radius: 12px; padding: 1.2rem 1.2rem;
    border-left: 5px solid #1abc9c; text-align: center;
  }
  .motivation-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem; font-style: italic;
    color: #0e6655; line-height: 1.6; font-weight: 600;
  }
  .motivation-dash { color: #1abc9c; font-size: 1.5rem; margin-bottom: 0.5rem; }

  /* ── INPUTS ── */
  textarea {
    background: #ffffff !important; color: #1a1a2e !important;
    border: 2px solid #e0e0e0 !important; border-radius: 12px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.95rem !important; line-height: 1.6 !important;
  }
  textarea:focus { border-color: #6c63ff !important; box-shadow: 0 0 0 3px rgba(108,99,255,0.1) !important; }

  /* ── BUTTONS ── */
  .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #1a1a2e, #0f3460) !important;
    color: #d4af37 !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 500 !important; letter-spacing: 0.2em !important;
    font-size: 0.9rem !important; border: none !important;
    border-radius: 10px !important; padding: 0.85rem !important;
    text-transform: uppercase !important;
  }
  .cg-success {
    background: #eafaf1; border: 1px solid #27ae60;
    border-radius: 10px; padding: 0.9rem 1rem;
    color: #1e8449; font-family: 'Oswald', sans-serif;
    font-size: 0.78rem; text-align: center; letter-spacing: 0.1em;
  }
  .cg-error {
    background: #fdf2f2; border: 1px solid #e74c3c;
    border-radius: 10px; padding: 0.9rem 1rem;
    color: #c0392b; font-family: 'Montserrat', sans-serif; font-size: 0.82rem;
  }
  .stSpinner > div { border-top-color: #6c63ff !important; }
  .stTabs [data-baseweb="tab-list"] { background: #f0eeff; border-radius: 10px; gap: 2px; padding: 4px; }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Oswald', sans-serif; font-weight: 400;
    font-size: 0.82rem; letter-spacing: 0.12em; color: #999;
    border-radius: 8px; padding: 0.4rem 0.8rem;
  }
  .stTabs [aria-selected="true"] { background: #6c63ff !important; color: white !important; }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #f8f5f0; }
  ::-webkit-scrollbar-thumb { background: #ddd; border-radius: 2px; }
  .stExpander { background: white !important; border-radius: 12px !important; border: 1px solid #eee !important; margin-bottom: 0.7rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Fixed Identity ──
CG_VISION = "I am a disciplined, patient, and consistently profitable trader living fully aligned with my purpose. I operate with clarity, faith, and emotional control. My life reflects financial freedom, stability, and impact, and I use my success to uplift my family, create opportunities, and leave a lasting legacy."
CG_GOALS = ["Achieve consistent trading profitability","Manage large trading capital ($500,000+)","Become financially independent","Support and uplift my family","Secure multiple income streams","Build a strong trading brand and mentorship platform","Own a professional trading setup","Travel freely and live with purpose","Mentor and guide other traders","Create lasting financial security and legacy"]
CG_AFFIRMATIONS = ["I am guided in my decisions.","I trade with discipline and patience.","I grow wiser every day.","I trust God's timing for my journey.","I am building a profitable and purposeful future.","I rest tonight with peace and clarity."]

EAT = pytz.timezone("Africa/Nairobi")
def get_eat_now(): return datetime.now(EAT)
def is_sunday(dt): return dt.weekday() == 6
def init_supabase(): return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def is_empty_entry(data):
    if not data: return True
    return not (data.get("verse_of_day") or data.get("daily_motivation") or data.get("gratitude_points"))

def generate_daily_content(user_text, dt, sunday):
    day = dt.strftime("%A, %d %B %Y")
    system = f"""You are AutoJournal AI for Cipher Ghost — a professional trader and Christian in East Africa.
Today is {day}. IS_SUNDAY: {sunday}.

Parse the entry and return COMPLETE JSON. Generate ALL missing fields.

ALWAYS GENERATE (never null):
- verse_of_day: Real Bible verse. Split into two fields: "reference" (e.g. "Psalm 23:1") and "text" (the verse)
- prayer: Personal heartfelt prayer for Cipher Ghost for this day (2-4 sentences)
- word_of_day: Powerful trading/growth word. Split: "word" and "definition"
- lesson_learned: Trading or life wisdom (1-2 sentences)
- daily_motivation: Strong mindset statement (1 sentence, powerful)
- gratitude_points: ALWAYS 3 strings. Extract from text first, generate rest if needed.
- food_recommendation: Suggest a full day's balanced low-budget meal plan for today. Include breakfast, lunch, dinner, snack. Be specific and practical for East Africa context. Format as object with keys: breakfast, lunch, dinner, snack, budget_note

HABITS — extract from text:
- daily_journal: "done"/"skipped"/null
- chart_analysis: "done"/"skipped"/null + "chart_notes": any chart analysis notes mentioned
- trades: "done"/"skipped"/null + "trade_notes": any trade details mentioned (entry, exit, result, lessons)
- clearness_brushing: "done"/"skipped"/null

IF IS_SUNDAY=True, ALWAYS generate full devotion:
- devotion: scripture, insight, reflection, prayer, application (all strings, never null on Sunday)

ONLY extract (never generate):
- mood (default "Focused")
- health.food_eaten (what they actually ate), health.meditation, health.budget
- monthly fields — only if mentioned

Return ONLY valid JSON:
{{
  "mood": null,
  "verse_of_day": {{"reference": null, "text": null}},
  "prayer": null,
  "devotion": {{"scripture": null,"insight": null,"reflection": null,"prayer": null,"application": null}},
  "habit_tracker": {{
    "daily_journal": null,
    "chart_analysis": null, "chart_notes": null,
    "trades": null, "trade_notes": null,
    "clearness_brushing": null
  }},
  "gratitude_points": [],
  "word_of_day": {{"word": null, "definition": null}},
  "lesson_learned": null,
  "food_recommendation": {{"breakfast": null,"lunch": null,"dinner": null,"snack": null,"budget_note": null}},
  "health": {{"food_eaten": null,"meditation": null,"budget": null}},
  "daily_motivation": null,
  "monthly": {{"top_3_grateful": [],"proud_of": null,"month_in_one_word": null,"next_month_objectives": []}}
}}"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_text}],
        temperature=0.3, max_tokens=2500,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)

def habit_card(icon, label, status, notes=None):
    if status is None: cls, mark = "habit-na-card", "○"
    elif str(status).lower() == "done": cls, mark = "habit-done-card", "✓"
    else: cls, mark = "habit-skip-card", "✗"
    html = f'<div class="habit-card {cls}"><span class="habit-icon">{icon}</span><span>{mark} {label}</span></div>'
    st.markdown(html, unsafe_allow_html=True)
    if notes and str(status or "").lower() == "done":
        st.markdown(f'<div class="habit-journal-area"><div class="habit-journal-label">Notes</div>{notes}</div>', unsafe_allow_html=True)

def render_entry(data, dt):
    sunday = is_sunday(dt)
    st.markdown(f'<div class="cg-date-pill">📅 {dt.strftime("%A, %d %B %Y")} · EAT</div>', unsafe_allow_html=True)
    if sunday:
        st.markdown('<div style="margin-top:0.5rem;"><span class="sunday-badge">✦ SUNDAY DEVOTION MODE</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── General ──
    st.markdown('<div class="card card-general"><div class="card-title title-general">✦ General Context</div>', unsafe_allow_html=True)
    mood = data.get("mood") or "Focused"
    st.markdown(f'<div class="fl">Today\'s Mood</div><div style="margin-top:0.3rem;"><span class="mood-badge">{mood}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Vision ──
    st.markdown('<div class="card card-vision"><div class="card-title title-vision">◈ Cipher Ghost · 5-Year Vision</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="vision-quote">{CG_VISION}</div>', unsafe_allow_html=True)
    st.markdown('<div class="fl">Goals & Manifestations</div>', unsafe_allow_html=True)
    for g in CG_GOALS:
        st.markdown(f'<div class="goal-item"><span class="goal-dot">◆</span>{g}</div>', unsafe_allow_html=True)
    st.markdown('<div class="fl" style="margin-top:0.8rem;">Daily Affirmations</div>', unsafe_allow_html=True)
    for a in CG_AFFIRMATIONS:
        st.markdown(f'<div class="affirmation-item">{a}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Prayer ──
    vod = data.get("verse_of_day", {}) or {}
    st.markdown('<div class="card card-prayer"><div class="card-title title-prayer">🙏 Cipher Ghost · Daily Prayer</div>', unsafe_allow_html=True)
    if vod.get("reference") or vod.get("text"):
        st.markdown(f'<div class="verse-box"><div class="verse-ref">{vod.get("reference","")}</div><div class="verse-text">{vod.get("text","")}</div></div>', unsafe_allow_html=True)
    elif isinstance(data.get("verse_of_day"), str):
        st.markdown(f'<div class="verse-box"><div class="verse-text">{data["verse_of_day"]}</div></div>', unsafe_allow_html=True)
    prayer = data.get("prayer")
    if prayer:
        st.markdown(f'<div class="fl">Prayer</div><div class="prayer-text">{prayer}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Devotion (Sunday only) ──
    if sunday:
        dev = data.get("devotion", {}) or {}
        st.markdown('<div class="card card-devotion"><div class="card-title title-devotion">✝ Sunday Devotion</div>', unsafe_allow_html=True)
        if dev.get("scripture"):
            st.markdown(f'<div class="fl">Scripture</div><div class="fv-accent">{dev["scripture"]}</div>', unsafe_allow_html=True)
        if dev.get("insight"):
            st.markdown(f'<div class="fl">Insight</div><div class="fv">{dev["insight"]}</div>', unsafe_allow_html=True)
        if dev.get("reflection"):
            st.markdown(f'<div class="fl">Reflection</div><div class="fv">{dev["reflection"]}</div>', unsafe_allow_html=True)
        if dev.get("prayer"):
            st.markdown(f'<div class="fl">Prayer</div><div class="prayer-text">{dev["prayer"]}</div>', unsafe_allow_html=True)
        if dev.get("application"):
            st.markdown(f'<div class="fl">Application</div><div class="fv">{dev["application"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Habits ──
    ht = data.get("habit_tracker", {}) or {}
    st.markdown('<div class="card card-habit"><div class="card-title title-habit">📋 Habit Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="habit-grid">', unsafe_allow_html=True)
    habit_card("📓", "Daily Journal", ht.get("daily_journal"))
    habit_card("📊", "Chart Analysis", ht.get("chart_analysis"))
    habit_card("💹", "Trades", ht.get("trades"))
    habit_card("🪥", "Clearness/Brushing", ht.get("clearness_brushing"))
    st.markdown("</div>", unsafe_allow_html=True)
    if ht.get("chart_notes"):
        st.markdown(f'<div class="habit-journal-area" style="margin-top:0.7rem;border-left:3px solid #27ae60;"><div class="habit-journal-label">📊 Chart Analysis Notes</div>{ht["chart_notes"]}</div>', unsafe_allow_html=True)
    if ht.get("trade_notes"):
        st.markdown(f'<div class="habit-journal-area" style="margin-top:0.5rem;border-left:3px solid #3498db;"><div class="habit-journal-label" style="color:#3498db;">💹 Trade Journal</div>{ht["trade_notes"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Gratitude Daily ──
    gpts = data.get("gratitude_points", [])
    wod = data.get("word_of_day", {}) or {}
    st.markdown('<div class="card card-gratitude"><div class="card-title title-gratitude">🙌 Gratitude · Daily</div>', unsafe_allow_html=True)
    for i, p in enumerate(gpts[:3], 1):
        if p:
            st.markdown(f'<div class="grat-item"><span class="grat-num">{i}</span><span class="grat-text">{p}</span></div>', unsafe_allow_html=True)
    if isinstance(wod, dict) and (wod.get("word") or wod.get("definition")):
        st.markdown(f'<div class="word-box"><div class="fl" style="color:#e67e22;">Word of the Day</div><div class="word-title">{wod.get("word","")}</div><div class="word-def">{wod.get("definition","")}</div></div>', unsafe_allow_html=True)
    elif isinstance(data.get("word_of_day"), str):
        st.markdown(f'<div class="word-box"><div class="fl" style="color:#e67e22;">Word of the Day</div><div class="word-title">{data["word_of_day"]}</div></div>', unsafe_allow_html=True)
    lesson = data.get("lesson_learned")
    if lesson:
        st.markdown(f'<div class="fl">Lesson Learned</div><div class="lesson-box">{lesson}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Monthly ──
    gm = data.get("monthly", {}) or {}
    has_monthly = any([gm.get("top_3_grateful"), gm.get("proud_of"), gm.get("month_in_one_word"), gm.get("next_month_objectives")])
    if has_monthly:
        st.markdown('<div class="card card-gratitude"><div class="card-title title-gratitude">🗓 Gratitude · Monthly</div>', unsafe_allow_html=True)
        for i, p in enumerate(gm.get("top_3_grateful", [])[:3], 1):
            if p: st.markdown(f'<div class="grat-item"><span class="grat-num">{i}</span><span class="grat-text">{p}</span></div>', unsafe_allow_html=True)
        if gm.get("proud_of"): st.markdown(f'<div class="fl">I Am Proud Of</div><div class="fv">{gm["proud_of"]}</div>', unsafe_allow_html=True)
        if gm.get("month_in_one_word"): st.markdown(f'<div class="fl">Month In One Word</div><div class="fv-accent">{gm["month_in_one_word"]}</div>', unsafe_allow_html=True)
        objs = gm.get("next_month_objectives", [])
        if objs:
            st.markdown('<div class="fl">Next Month — Looking Forward To</div>', unsafe_allow_html=True)
            for o in objs[:3]:
                if o: st.markdown(f'<div class="goal-item"><span class="goal-dot" style="color:#e67e22;">→</span>{o}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Health ──
    hth = data.get("health", {}) or {}
    food_rec = data.get("food_recommendation", {}) or {}
    st.markdown('<div class="card card-health"><div class="card-title title-health">❤️ Health Track</div>', unsafe_allow_html=True)
    if hth.get("food_eaten"):
        st.markdown(f'<div class="health-stat"><span class="health-icon">🍽️</span><span><b>Ate:</b> {hth["food_eaten"]}</span></div>', unsafe_allow_html=True)
    if hth.get("meditation"):
        st.markdown(f'<div class="health-stat"><span class="health-icon">🧘</span><span><b>Meditation:</b> {hth["meditation"]}</span></div>', unsafe_allow_html=True)
    if hth.get("budget"):
        st.markdown(f'<div class="health-stat"><span class="health-icon">💰</span><span><b>Budget:</b> {hth["budget"]}</span></div>', unsafe_allow_html=True)
    if food_rec.get("breakfast") or food_rec.get("lunch"):
        st.markdown('<div class="food-rec"><div class="food-title">🤖 AI Meal Recommendation · Today</div>', unsafe_allow_html=True)
        if food_rec.get("breakfast"): st.markdown(f'<div class="food-meal">🌅 <b>Breakfast:</b> {food_rec["breakfast"]}</div>', unsafe_allow_html=True)
        if food_rec.get("lunch"): st.markdown(f'<div class="food-meal">☀️ <b>Lunch:</b> {food_rec["lunch"]}</div>', unsafe_allow_html=True)
        if food_rec.get("dinner"): st.markdown(f'<div class="food-meal">🌙 <b>Dinner:</b> {food_rec["dinner"]}</div>', unsafe_allow_html=True)
        if food_rec.get("snack"): st.markdown(f'<div class="food-meal">🍎 <b>Snack:</b> {food_rec["snack"]}</div>', unsafe_allow_html=True)
        if food_rec.get("budget_note"): st.markdown(f'<div class="food-meal" style="color:#888;font-size:0.75rem;">💡 {food_rec["budget_note"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Motivation ──
    dm = data.get("daily_motivation")
    if dm:
        st.markdown(f'<div class="card card-motivation"><div class="card-title title-motivation">⚡ Daily Motivation</div><div class="motivation-box"><div class="motivation-dash">— —</div><div class="motivation-text">{dm}</div></div></div>', unsafe_allow_html=True)

def render_history(sb):
    try:
        result = sb.table("journal_entries").select("*").order("created_at", desc=True).limit(60).execute()
        entries = result.data
        valid = []
        for e in entries:
            raw = e.get("extracted_data", {})
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: raw = {}
            if not is_empty_entry(raw):
                e["_parsed"] = raw
                valid.append(e)
        if not valid:
            st.markdown('<div class="card"><p style="color:#aaa;font-size:0.85rem;text-align:center;margin:0;font-family:Montserrat;">No entries yet. Submit your first entry above.</p></div>', unsafe_allow_html=True)
            return
        for e in valid:
            raw = e["_parsed"]
            mood = raw.get("mood") or "—"
            date_str = e.get("entry_date", "")
            entry_id = e.get("id")
            with st.expander(f"📅 {date_str}  ·  {mood}"):
                try:
                    entry_dt = datetime.fromisoformat(date_str).replace(tzinfo=EAT) if date_str else get_eat_now()
                except: entry_dt = get_eat_now()
                render_entry(raw, entry_dt)
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([3,1])
                with col2:
                    if st.button("🗑 Delete", key=f"del_{entry_id}"):
                        st.session_state[f"confirm_{entry_id}"] = True
                if st.session_state.get(f"confirm_{entry_id}"):
                    st.warning("Delete this entry permanently?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✓ Yes", key=f"yes_{entry_id}"):
                            try:
                                sb.table("journal_entries").delete().eq("id", entry_id).execute()
                                st.session_state.pop(f"confirm_{entry_id}", None)
                                st.success("Deleted.")
                                st.rerun()
                            except Exception as ex: st.error(f"Error: {ex}")
                    with c2:
                        if st.button("✗ Cancel", key=f"no_{entry_id}"):
                            st.session_state.pop(f"confirm_{entry_id}", None)
                            st.rerun()
    except Exception as ex:
        st.markdown(f'<div class="cg-error">History error: {ex}</div>', unsafe_allow_html=True)

def main():
    now = get_eat_now()
    sunday = is_sunday(now)

    st.markdown(f"""
    <div class="cg-hero">
      <h1>AUTOJOURNAL</h1>
      <div class="sub">Cipher Ghost · Personal OS</div>
      <div class="cg-date-pill">{now.strftime("%A, %d %B %Y · %H:%M EAT")}</div>
    </div>
    """, unsafe_allow_html=True)

    tab_new, tab_history = st.tabs(["✦  New Entry", "◈  History"])

    with tab_new:
        st.markdown("<br>", unsafe_allow_html=True)
        if sunday:
            st.markdown('<span class="sunday-badge">✦ SUNDAY — Devotion fields active</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div style="font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;color:#1a1a2e;margin-bottom:0.3rem;">Dump Your Day</div>'
            '<div style="font-family:\'Montserrat\',sans-serif;font-size:0.8rem;color:#999;margin-bottom:0.8rem;line-height:1.5;">'
            'Type or use 🎤 voice-to-text. Include trades, charts, gratitude, mood — anything. AI builds everything else.</div>',
            unsafe_allow_html=True,
        )
        user_input = st.text_area(
            label="j", label_visibility="collapsed",
            placeholder="e.g. Good day. Grateful for family, my progress and God's grace. Did chart analysis on EURUSD — saw a clear CHoCH at 1.0850, potential long setup forming. Took a trade on Gold, entered at 2315, TP hit at 2325, +1.5R. Meditated 10 mins. Budget $35 today.",
            height=210,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.button("⚡  EXTRACT & SAVE JOURNAL")

        if submit:
            if not user_input.strip():
                st.markdown('<div class="cg-error">⚠ Write at least one sentence about your day.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Building your journal…"):
                    try:
                        extracted = generate_daily_content(user_input, now, sunday)
                        sb = init_supabase()
                        sb.table("journal_entries").insert({
                            "entry_date": now.strftime("%Y-%m-%d"),
                            "day_of_week": now.strftime("%A"),
                            "is_sunday": sunday,
                            "raw_text": user_input,
                            "extracted_data": json.dumps(extracted),
                            "created_at": now.isoformat(),
                        }).execute()
                        st.markdown('<div class="cg-success">✓ JOURNAL SAVED · CIPHER GHOST LOG UPDATED</div>', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        render_entry(extracted, now)
                    except json.JSONDecodeError as e:
                        st.markdown(f'<div class="cg-error">⚠ AI parse error. Try again.<br><small>{e}</small></div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="cg-error">⚠ {str(e)}</div>', unsafe_allow_html=True)

    with tab_history:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            sb = init_supabase()
            render_history(sb)
        except Exception as e:
            st.markdown(f'<div class="cg-error">⚠ {e}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
