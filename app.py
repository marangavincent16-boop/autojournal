import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime
import pytz
from supabase import create_client, Client

# ─────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AutoJournal · Cipher Ghost",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# GLOBAL CSS — dark, mobile-first
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');

  html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #080c10 !important;
    color: #c8d6e5 !important;
  }
  .main .block-container {
    padding: 1rem 1.1rem 4rem 1.1rem;
    max-width: 480px;
    margin: 0 auto;
  }
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="collapsedControl"] { display: none; }

  .cg-hero {
    text-align: center;
    padding: 1.8rem 0 0.6rem 0;
  }
  .cg-hero h1 {
    font-family: 'Cinzel', serif;
    font-size: 1.55rem;
    font-weight: 900;
    letter-spacing: 0.18em;
    color: #e8d48b;
    text-shadow: 0 0 24px rgba(232,212,139,0.35);
    margin: 0;
    line-height: 1.2;
  }
  .cg-hero .sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #4a6175;
    letter-spacing: 0.3em;
    margin-top: 0.35rem;
  }
  .cg-date-pill {
    display: inline-block;
    background: rgba(232,212,139,0.08);
    border: 1px solid rgba(232,212,139,0.22);
    border-radius: 20px;
    padding: 0.22rem 0.9rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #e8d48b;
    letter-spacing: 0.08em;
    margin-top: 0.7rem;
  }
  .cg-card {
    background: linear-gradient(145deg, #0e1520, #101925);
    border: 1px solid #1e2e3e;
    border-left: 3px solid #e8d48b;
    border-radius: 10px;
    padding: 1.1rem 1rem 0.8rem 1rem;
    margin-bottom: 1.1rem;
  }
  .cg-card h3 {
    font-family: 'Cinzel', serif;
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    color: #e8d48b;
    margin: 0 0 0.7rem 0;
    text-transform: uppercase;
  }
  .field-label {
    font-size: 0.72rem;
    color: #4a6175;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.18rem;
    font-family: 'Share Tech Mono', monospace;
  }
  .field-value {
    font-size: 0.92rem;
    color: #c8d6e5;
    line-height: 1.45;
    margin-bottom: 0.7rem;
    padding-left: 0.5rem;
    border-left: 2px solid #1e3a50;
  }
  .field-value.accent { color: #e8d48b; font-weight: 600; }

  .habit-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem; }
  .habit-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    padding: 0.22rem 0.6rem;
    border-radius: 4px;
    letter-spacing: 0.06em;
  }
  .habit-done { background: rgba(80,200,100,0.15); border: 1px solid rgba(80,200,100,0.4); color: #58d68d; }
  .habit-skip { background: rgba(200,80,80,0.15); border: 1px solid rgba(200,80,80,0.4); color: #e57373; }
  .habit-na   { background: rgba(100,100,120,0.15); border: 1px solid #1e2e3e; color: #4a6175; }

  .grat-point {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  .grat-num {
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    color: #e8d48b;
    min-width: 1.1rem;
    padding-top: 0.05rem;
  }
  .grat-text { font-size: 0.9rem; color: #c8d6e5; line-height: 1.4; }

  textarea {
    background: #0e1520 !important;
    color: #c8d6e5 !important;
    border: 1px solid #1e2e3e !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    line-height: 1.5 !important;
    caret-color: #e8d48b !important;
  }
  textarea:focus {
    border-color: #e8d48b !important;
    box-shadow: 0 0 0 2px rgba(232,212,139,0.12) !important;
  }

  .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #e8d48b, #c9a84c) !important;
    color: #080c10 !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    text-transform: uppercase !important;
  }
  .cg-success {
    background: rgba(80,200,100,0.1);
    border: 1px solid rgba(80,200,100,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #58d68d;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    text-align: center;
    letter-spacing: 0.08em;
  }
  .cg-error {
    background: rgba(200,80,80,0.1);
    border: 1px solid rgba(200,80,80,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #e57373;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
  }
  .cg-sunday-badge {
    background: rgba(155,89,182,0.15);
    border: 1px solid rgba(155,89,182,0.4);
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    color: #c39bd3;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    display: inline-block;
    margin-bottom: 0.8rem;
  }
  .stSpinner > div { border-top-color: #e8d48b !important; }
  .stTabs [data-baseweb="tab-list"] {
    background: #0e1520;
    border-radius: 8px;
    gap: 2px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    color: #4a6175;
    border-radius: 6px;
    padding: 0.4rem 0.6rem;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(232,212,139,0.12) !important;
    color: #e8d48b !important;
  }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #080c10; }
  ::-webkit-scrollbar-thumb { background: #1e3a50; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
EAT = pytz.timezone("Africa/Nairobi")


def get_eat_now() -> datetime:
    return datetime.now(EAT)


def is_sunday(dt: datetime) -> bool:
    return dt.weekday() == 6


def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def save_to_supabase(client: Client, data: dict):
    return client.table("journal_entries").insert(data).execute()


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT_TEMPLATE = """You are AutoJournal AI — a personal journaling assistant for a professional trader named Cipher Ghost.
Parse the free-form end-of-day journal entry below and extract structured data into strict JSON.

TODAY: {date_str} ({day_of_week}) | IS_SUNDAY: {is_sunday}

RULES:
- Extract every field you can find. Use null if not mentioned.
- Habit fields: "done", "skipped", or null.
- Mood: "Excellent", "Good", "Neutral", "Tired", "Stressed", "Low", or short custom phrase.
- If IS_SUNDAY is true, prioritize extracting devotion fields (scripture, insight, reflection, prayer, application).
- gratitude points and monthly top3/objectives: arrays of strings, max 3 items each.
- daily_motivation: trading psychology or mindset insight from the entry.
- Return ONLY valid JSON. No markdown fences, no explanation, no preamble.

JSON SCHEMA:
{{
  "general": {{
    "date": "{date_str}",
    "day_of_week": "{day_of_week}",
    "mood": null,
    "identity_vision": null,
    "goals_manifestation": null,
    "daily_affirmations": null
  }},
  "vision": {{
    "five_year_alignment_note": null
  }},
  "daily_prayer": {{
    "verse_of_day": null,
    "prayer": null
  }},
  "devotion": {{
    "scripture": null,
    "insight": null,
    "reflection": null,
    "prayer": null,
    "application": null
  }},
  "habit_tracker": {{
    "daily_journal": null,
    "chart_analysis": null,
    "trades": null,
    "clearness_brushing": null
  }},
  "gratitude_daily": {{
    "points": [],
    "word_of_day": null,
    "word_explanation": null,
    "lesson_learned": null
  }},
  "gratitude_monthly": {{
    "top_3_grateful": [],
    "proud_of": null,
    "month_in_one_word": null,
    "next_month_objectives": []
  }},
  "health_track": {{
    "food": null,
    "meditation": null,
    "budget": null
  }},
  "daily_motivation": null
}}"""


def build_system_prompt(dt: datetime) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        date_str=dt.strftime("%Y-%m-%d"),
        day_of_week=dt.strftime("%A"),
        is_sunday=str(is_sunday(dt)),
    )


# ─────────────────────────────────────────────
# AI EXTRACTION
# ─────────────────────────────────────────────
def extract_journal(user_text: str, dt: datetime) -> dict:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=build_system_prompt(dt),
    )
    response = model.generate_content(user_text)
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ─────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────
def field(label: str, value, accent: bool = False):
    if value is None or value == "" or value == []:
        return
    css = "field-value accent" if accent else "field-value"
    if isinstance(value, list):
        value = " · ".join([str(v) for v in value if v])
    st.markdown(
        f'<div class="field-label">{label}</div><div class="{css}">{value}</div>',
        unsafe_allow_html=True,
    )


def habit_badge(label: str, status) -> str:
    if status is None:
        cls, icon = "habit-na", "○"
    elif str(status).lower() == "done":
        cls, icon = "habit-done", "✓"
    else:
        cls, icon = "habit-skip", "✗"
    return f'<span class="habit-badge {cls}">{icon} {label}</span>'


def grat_list(items: list):
    if not items:
        return
    html = ""
    for i, p in enumerate(items[:3], 1):
        if p:
            html += f'<div class="grat-point"><span class="grat-num">{i}.</span><span class="grat-text">{p}</span></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_results(data: dict, dt: datetime):
    g = data.get("general", {})
    sunday = is_sunday(dt)

    st.markdown(
        f'<div class="cg-date-pill">📅 {dt.strftime("%A, %d %B %Y")} · EAT</div>',
        unsafe_allow_html=True,
    )
    if sunday:
        st.markdown('<div style="margin-top:0.5rem;"><span class="cg-sunday-badge">✦ SUNDAY DEVOTION MODE</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # General
    st.markdown('<div class="cg-card"><h3>◈ General Context</h3>', unsafe_allow_html=True)
    field("Mood", g.get("mood"), accent=True)
    field("5-Year Identity Vision", g.get("identity_vision"))
    field("Goals & Manifestation", g.get("goals_manifestation"))
    field("Daily Affirmations", g.get("daily_affirmations"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Vision
    v = data.get("vision", {})
    if v.get("five_year_alignment_note"):
        st.markdown('<div class="cg-card"><h3>◈ CG 5-Year Vision</h3>', unsafe_allow_html=True)
        field("Alignment Note", v["five_year_alignment_note"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Prayer
    dp = data.get("daily_prayer", {})
    if dp.get("verse_of_day") or dp.get("prayer"):
        st.markdown('<div class="cg-card"><h3>◈ CG Daily Prayer</h3>', unsafe_allow_html=True)
        field("Verse of the Day", dp.get("verse_of_day"), accent=True)
        field("Prayer", dp.get("prayer"))
        st.markdown("</div>", unsafe_allow_html=True)

    # Devotion (Sunday only)
    if sunday:
        dev = data.get("devotion", {})
        st.markdown('<div class="cg-card"><h3>◈ Sunday Devotion</h3>', unsafe_allow_html=True)
        field("Scripture", dev.get("scripture"), accent=True)
        field("Insight", dev.get("insight"))
        field("Reflection", dev.get("reflection"))
        field("Prayer", dev.get("prayer"))
        field("Application", dev.get("application"))
        st.markdown("</div>", unsafe_allow_html=True)

    # Habits
    ht = data.get("habit_tracker", {})
    st.markdown('<div class="cg-card"><h3>◈ Habit Tracker</h3>', unsafe_allow_html=True)
    badges = (
        habit_badge("Daily Journal", ht.get("daily_journal"))
        + habit_badge("Chart Analysis", ht.get("chart_analysis"))
        + habit_badge("Trades", ht.get("trades"))
        + habit_badge("Clearness/Brushing", ht.get("clearness_brushing"))
    )
    st.markdown(f'<div class="habit-row">{badges}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Gratitude Daily
    gd = data.get("gratitude_daily", {})
    st.markdown('<div class="cg-card"><h3>◈ Gratitude · Daily</h3>', unsafe_allow_html=True)
    grat_list(gd.get("points", []))
    field("Word of the Day", gd.get("word_of_day"), accent=True)
    field("Meaning", gd.get("word_explanation"))
    field("Lesson Learned", gd.get("lesson_learned"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Gratitude Monthly (conditional)
    gm = data.get("gratitude_monthly", {})
    has_monthly = any([gm.get("top_3_grateful"), gm.get("proud_of"),
                       gm.get("month_in_one_word"), gm.get("next_month_objectives")])
    if has_monthly:
        st.markdown('<div class="cg-card"><h3>◈ Gratitude · Monthly</h3>', unsafe_allow_html=True)
        grat_list(gm.get("top_3_grateful", []))
        field("Proud Of", gm.get("proud_of"))
        field("Month In One Word", gm.get("month_in_one_word"), accent=True)
        objs = gm.get("next_month_objectives", [])
        if objs:
            st.markdown('<div class="field-label">Next Month · Objectives</div>', unsafe_allow_html=True)
            for o in objs[:3]:
                if o:
                    st.markdown(
                        f'<div class="grat-point"><span class="grat-num">→</span>'
                        f'<span class="grat-text">{o}</span></div>',
                        unsafe_allow_html=True,
                    )
        st.markdown("</div>", unsafe_allow_html=True)

    # Health
    hth = data.get("health_track", {})
    st.markdown('<div class="cg-card"><h3>◈ Health Track</h3>', unsafe_allow_html=True)
    field("Food", hth.get("food"))
    field("Meditation", hth.get("meditation"))
    field("Budget", hth.get("budget"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Motivation
    dm = data.get("daily_motivation")
    if dm:
        st.markdown(
            f'<div class="cg-card"><h3>◈ Daily Motivation</h3>'
            f'<div class="field-value" style="font-style:italic;color:#e8d48b;'
            f'border-left:3px solid #e8d48b;padding-left:0.6rem;">{dm}</div></div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# HISTORY TAB
# ─────────────────────────────────────────────
def render_history(sb: Client):
    try:
        result = (
            sb.table("journal_entries")
            .select("*")
            .order("created_at", desc=True)
            .limit(30)
            .execute()
        )
        entries = result.data
        if not entries:
            st.markdown(
                '<div class="cg-card"><p style="color:#4a6175;font-size:0.85rem;'
                'text-align:center;margin:0;">No entries yet.</p></div>',
                unsafe_allow_html=True,
            )
            return
        for e in entries:
            raw_data = e.get("extracted_data", {})
            if isinstance(raw_data, str):
                try:
                    raw_data = json.loads(raw_data)
                except Exception:
                    raw_data = {}
            g = raw_data.get("general", {})
            mood = g.get("mood") or "—"
            date_str = e.get("entry_date", "")
            label = f"📅 {date_str}  ·  {mood}" if date_str else f"📅 Entry · {mood}"
            with st.expander(label):
                try:
                    entry_dt = (
                        datetime.fromisoformat(date_str).replace(tzinfo=EAT)
                        if date_str
                        else get_eat_now()
                    )
                except Exception:
                    entry_dt = get_eat_now()
                render_results(raw_data, entry_dt)
    except Exception as ex:
        st.markdown(
            f'<div class="cg-error">History load error: {ex}</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    now = get_eat_now()

    st.markdown("""
    <div class="cg-hero">
      <h1>AUTOJOURNAL</h1>
      <div class="sub">CIPHER GHOST · PERSONAL OS</div>
    </div>
    """, unsafe_allow_html=True)

    tab_new, tab_history = st.tabs(["✦  New Entry", "◈  History"])

    with tab_new:
        st.markdown("<br>", unsafe_allow_html=True)

        sunday = is_sunday(now)
        st.markdown(
            f'<div class="cg-date-pill">{now.strftime("%A, %d %b %Y · %H:%M EAT")}</div>',
            unsafe_allow_html=True,
        )
        if sunday:
            st.markdown(
                '<div style="margin-top:0.5rem;">'
                '<span class="cg-sunday-badge">✦ SUNDAY — Devotion fields active</span>'
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'Cinzel\',serif;font-size:0.72rem;letter-spacing:0.18em;'
            'color:#e8d48b;margin-bottom:0.4rem;">DUMP YOUR DAY</div>'
            '<div style="font-size:0.82rem;color:#4a6175;margin-bottom:0.7rem;line-height:1.45;">'
            "Type freely or use 🎤 voice-to-text. Include your mood, gratitude, trades, habits, "
            "prayers — anything. The AI structures it all.</div>",
            unsafe_allow_html=True,
        )

        user_input = st.text_area(
            label="journal_input",
            label_visibility="collapsed",
            placeholder=(
                "e.g. Today was solid. Grateful for my family, health, and a clean 2R trade on EU. "
                "Read Proverbs 3:5, prayed for discernment and patience. Did chart analysis, "
                "no live trades. Word of the day: Equanimity — mental calmness under pressure. "
                "Ate clean, meditated 10 mins, stayed within budget $47. Lesson: let the setup "
                "come to you. Identity: I am a disciplined, profitable futures trader..."
            ),
            height=230,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.button("⚡  EXTRACT & SAVE JOURNAL")

        if submit:
            if not user_input.strip():
                st.markdown(
                    '<div class="cg-error">⚠ Please write something before submitting.</div>',
                    unsafe_allow_html=True,
                )
            else:
                with st.spinner("Cipher Ghost AI is parsing your day…"):
                    try:
                        extracted = extract_journal(user_input, now)

                        sb = init_supabase()
                        save_to_supabase(sb, {
                            "entry_date": now.strftime("%Y-%m-%d"),
                            "day_of_week": now.strftime("%A"),
                            "is_sunday": sunday,
                            "raw_text": user_input,
                            "extracted_data": json.dumps(extracted),
                            "created_at": now.isoformat(),
                        })

                        st.markdown(
                            '<div class="cg-success">✓ ENTRY SAVED · CIPHER GHOST LOG UPDATED</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(
                            '<div style="font-family:\'Cinzel\',serif;font-size:0.72rem;'
                            'letter-spacing:0.18em;color:#e8d48b;margin-bottom:0.8rem;">STRUCTURED ENTRY</div>',
                            unsafe_allow_html=True,
                        )
                        render_results(extracted, now)

                    except json.JSONDecodeError as e:
                        st.markdown(
                            f'<div class="cg-error">⚠ AI returned malformed JSON. Try rephrasing your entry.'
                            f"<br><small>{e}</small></div>",
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.markdown(
                            f'<div class="cg-error">⚠ {str(e)}</div>',
                            unsafe_allow_html=True,
                        )

    with tab_history:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            sb = init_supabase()
            render_history(sb)
        except Exception as e:
            st.markdown(
                f'<div class="cg-error">⚠ Database connection error: {e}</div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
