import streamlit as st
from groq import Groq
import json
import re
from datetime import datetime
import pytz
from supabase import create_client, Client

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AutoJournal · Cipher Ghost",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
  html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #080c10 !important;
    color: #c8d6e5 !important;
  }
  .main .block-container { padding: 1rem 1.1rem 4rem 1.1rem; max-width: 480px; margin: 0 auto; }
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="collapsedControl"] { display: none; }
  .cg-hero { text-align: center; padding: 1.8rem 0 0.6rem 0; }
  .cg-hero h1 { font-family: 'Cinzel', serif; font-size: 1.55rem; font-weight: 900; letter-spacing: 0.18em; color: #e8d48b; text-shadow: 0 0 24px rgba(232,212,139,0.35); margin: 0; line-height: 1.2; }
  .cg-hero .sub { font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #4a6175; letter-spacing: 0.3em; margin-top: 0.35rem; }
  .cg-date-pill { display: inline-block; background: rgba(232,212,139,0.08); border: 1px solid rgba(232,212,139,0.22); border-radius: 20px; padding: 0.22rem 0.9rem; font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #e8d48b; letter-spacing: 0.08em; margin-top: 0.7rem; }
  .cg-card { background: linear-gradient(145deg, #0e1520, #101925); border: 1px solid #1e2e3e; border-left: 3px solid #e8d48b; border-radius: 10px; padding: 1.1rem 1rem 0.8rem 1rem; margin-bottom: 1.1rem; }
  .cg-card h3 { font-family: 'Cinzel', serif; font-size: 0.8rem; letter-spacing: 0.2em; color: #e8d48b; margin: 0 0 0.7rem 0; text-transform: uppercase; }
  .field-label { font-size: 0.72rem; color: #4a6175; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.18rem; font-family: 'Share Tech Mono', monospace; }
  .field-value { font-size: 0.92rem; color: #c8d6e5; line-height: 1.45; margin-bottom: 0.7rem; padding-left: 0.5rem; border-left: 2px solid #1e3a50; }
  .field-value.accent { color: #e8d48b; font-weight: 600; }
  .field-value.italic { font-style: italic; }
  .habit-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem; }
  .habit-badge { font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; padding: 0.22rem 0.6rem; border-radius: 4px; letter-spacing: 0.06em; }
  .habit-done { background: rgba(80,200,100,0.15); border: 1px solid rgba(80,200,100,0.4); color: #58d68d; }
  .habit-skip { background: rgba(200,80,80,0.15); border: 1px solid rgba(200,80,80,0.4); color: #e57373; }
  .habit-na { background: rgba(100,100,120,0.15); border: 1px solid #1e2e3e; color: #4a6175; }
  .grat-point { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem; }
  .grat-num { font-family: 'Cinzel', serif; font-size: 0.75rem; color: #e8d48b; min-width: 1.1rem; padding-top: 0.05rem; }
  .grat-text { font-size: 0.9rem; color: #c8d6e5; line-height: 1.4; }
  .vision-text { font-size: 0.88rem; color: #c8d6e5; line-height: 1.6; font-style: italic; padding: 0.5rem 0.7rem; border-left: 3px solid #e8d48b; margin-bottom: 0.7rem; }
  .goal-item { font-size: 0.85rem; color: #c8d6e5; padding: 0.2rem 0 0.2rem 0.5rem; border-left: 2px solid #1e3a50; margin-bottom: 0.3rem; }
  .affirmation-item { font-size: 0.88rem; color: #a8c4d8; padding: 0.18rem 0 0.18rem 0.5rem; border-left: 2px solid rgba(232,212,139,0.3); margin-bottom: 0.3rem; font-style: italic; }
  .sunday-badge { background: rgba(155,89,182,0.15); border: 1px solid rgba(155,89,182,0.4); border-radius: 6px; padding: 0.3rem 0.7rem; color: #c39bd3; font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; letter-spacing: 0.12em; display: inline-block; margin-bottom: 0.8rem; }
  .motivation-text { font-size: 0.95rem; font-style: italic; color: #e8d48b; border-left: 3px solid #e8d48b; padding-left: 0.6rem; line-height: 1.5; }
  textarea { background: #0e1520 !important; color: #c8d6e5 !important; border: 1px solid #1e2e3e !important; border-radius: 10px !important; font-family: 'Rajdhani', sans-serif !important; font-size: 1rem !important; line-height: 1.5 !important; caret-color: #e8d48b !important; }
  textarea:focus { border-color: #e8d48b !important; box-shadow: 0 0 0 2px rgba(232,212,139,0.12) !important; }
  .stButton > button { width: 100%; background: linear-gradient(135deg, #e8d48b, #c9a84c) !important; color: #080c10 !important; font-family: 'Cinzel', serif !important; font-weight: 700 !important; letter-spacing: 0.15em !important; font-size: 0.85rem !important; border: none !important; border-radius: 8px !important; padding: 0.75rem !important; text-transform: uppercase !important; }
  .cg-success { background: rgba(80,200,100,0.1); border: 1px solid rgba(80,200,100,0.3); border-radius: 8px; padding: 0.8rem 1rem; color: #58d68d; font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; text-align: center; letter-spacing: 0.08em; }
  .cg-error { background: rgba(200,80,80,0.1); border: 1px solid rgba(200,80,80,0.3); border-radius: 8px; padding: 0.8rem 1rem; color: #e57373; font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; }
  .stSpinner > div { border-top-color: #e8d48b !important; }
  .stTabs [data-baseweb="tab-list"] { background: #0e1520; border-radius: 8px; gap: 2px; padding: 4px; }
  .stTabs [data-baseweb="tab"] { font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 0.8rem; letter-spacing: 0.1em; color: #4a6175; border-radius: 6px; padding: 0.4rem 0.6rem; }
  .stTabs [aria-selected="true"] { background: rgba(232,212,139,0.12) !important; color: #e8d48b !important; }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #080c10; }
  ::-webkit-scrollbar-thumb { background: #1e3a50; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CIPHER GHOST FIXED IDENTITY CONTENT
# ─────────────────────────────────────────────
CG_VISION = "I am a disciplined, patient, and consistently profitable trader living fully aligned with my purpose. I operate with clarity, faith, and emotional control. My life reflects financial freedom, stability, and impact, and I use my success to uplift my family, create opportunities, and leave a lasting legacy."

CG_GOALS = [
    "Achieve consistent trading profitability",
    "Manage large trading capital ($500,000+)",
    "Become financially independent",
    "Support and uplift my family",
    "Secure multiple income streams",
    "Build a strong trading brand and mentorship platform",
    "Own a professional trading setup",
    "Travel freely and live with purpose",
    "Mentor and guide other traders",
    "Create lasting financial security and legacy",
]

CG_AFFIRMATIONS = [
    "I am guided in my decisions.",
    "I trade with discipline and patience.",
    "I grow wiser every day.",
    "I trust God's timing for my journey.",
    "I am building a profitable and purposeful future.",
    "I rest tonight with peace and clarity.",
]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
EAT = pytz.timezone("Africa/Nairobi")

def get_eat_now(): return datetime.now(EAT)
def is_sunday(dt): return dt.weekday() == 6
def get_groq(): return Groq(api_key=st.secrets["GROQ_API_KEY"])
def init_supabase(): return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ─────────────────────────────────────────────
# AI CALLS
# ─────────────────────────────────────────────
def ai_call(system: str, user: str, max_tokens: int = 1500) -> str:
    client = get_groq()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def generate_daily_content(user_text: str, dt: datetime, sunday: bool) -> dict:
    """Single AI call that extracts journal data AND auto-generates missing fields."""
    day = dt.strftime("%A, %d %B %Y")

    system = f"""You are AutoJournal AI for Cipher Ghost — a professional trader and man of faith.
Today is {day}. IS_SUNDAY: {sunday}.

Your job: Parse the journal entry and return a complete JSON object.
For ANY field not mentioned in the entry, GENERATE appropriate content based on:
- The day of the week and date
- Cipher Ghost's identity as a trader and Christian
- The mood/tone of the entry if detectable

GENERATION RULES:
- verse_of_day: Always provide a real Bible verse relevant to trading, discipline, faith, or the day's theme. Format: "Book Chapter:Verse — actual verse text"
- prayer: Generate a personal, heartfelt prayer for Cipher Ghost relevant to the day
- word_of_day: Pick a powerful word relevant to trading psychology or personal growth. Format: "Word — definition"
- lesson_learned: Generate a trading/life wisdom lesson if not mentioned
- daily_motivation: Generate a strong trading psychology or mindset statement
- mood: Extract from text or default to "Focused"
- If sunday=True, generate full devotion (scripture, insight, reflection, prayer, application) relevant to trading and faith
- habit fields: "done", "skipped", or null (only from explicit mentions)
- gratitude points: Extract from text (up to 3). If fewer than 3 mentioned, generate relevant ones based on entry tone
- health food/meditation/budget: Extract only, do not generate

Return ONLY valid JSON, no markdown, no explanation:

{{
  "mood": null,
  "verse_of_day": null,
  "prayer": null,
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
  "gratitude_points": [],
  "word_of_day": null,
  "lesson_learned": null,
  "health": {{
    "food": null,
    "meditation": null,
    "budget": null
  }},
  "daily_motivation": null,
  "monthly": {{
    "top_3_grateful": [],
    "proud_of": null,
    "month_in_one_word": null,
    "next_month_objectives": []
  }}
}}"""

    raw = ai_call(system, user_text, max_tokens=2000)
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ─────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────
def field(label, value, accent=False, italic=False):
    if not value and value != 0: return
    if isinstance(value, list): value = " · ".join([str(v) for v in value if v])
    css = "field-value"
    if accent: css += " accent"
    if italic: css += " italic"
    st.markdown(f'<div class="field-label">{label}</div><div class="{css}">{value}</div>', unsafe_allow_html=True)

def habit_badge(label, status):
    if status is None: cls, icon = "habit-na", "○"
    elif str(status).lower() == "done": cls, icon = "habit-done", "✓"
    else: cls, icon = "habit-skip", "✗"
    return f'<span class="habit-badge {cls}">{icon} {label}</span>'

def grat_list(items, arrow=False):
    if not items: return
    html = ""
    for i, p in enumerate(items[:3], 1):
        if p:
            num = "→" if arrow else str(i) + "."
            html += f'<div class="grat-point"><span class="grat-num">{num}</span><span class="grat-text">{p}</span></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_entry(data: dict, dt: datetime):
    sunday = is_sunday(dt)

    # Date pill
    st.markdown(f'<div class="cg-date-pill">📅 {dt.strftime("%A, %d %B %Y")} · EAT</div>', unsafe_allow_html=True)
    if sunday:
        st.markdown('<div style="margin-top:0.5rem;"><span class="sunday-badge">✦ SUNDAY DEVOTION MODE</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── 0. General Context ──
    st.markdown('<div class="cg-card"><h3>◈ General Context</h3>', unsafe_allow_html=True)
    field("Mood", data.get("mood"), accent=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 1. CG 5-Year Vision (always shown, fixed) ──
    st.markdown('<div class="cg-card"><h3>◈ Cipher Ghost · 5-Year Vision</h3>', unsafe_allow_html=True)
    st.markdown(f'<div class="vision-text">{CG_VISION}</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label">Goals & Manifestations</div>', unsafe_allow_html=True)
    for g in CG_GOALS:
        st.markdown(f'<div class="goal-item">◦ {g}</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label" style="margin-top:0.8rem;">Daily Affirmations</div>', unsafe_allow_html=True)
    for a in CG_AFFIRMATIONS:
        st.markdown(f'<div class="affirmation-item">{a}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 2. Daily Prayer (always generated) ──
    st.markdown('<div class="cg-card"><h3>◈ Cipher Ghost · Daily Prayer</h3>', unsafe_allow_html=True)
    field("Verse of the Day", data.get("verse_of_day"), accent=True)
    field("Prayer", data.get("prayer"), italic=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Sunday Devotion ──
    if sunday:
        dev = data.get("devotion", {})
        st.markdown('<div class="cg-card"><h3>◈ Cipher Ghost · Sunday Devotion</h3>', unsafe_allow_html=True)
        field("Scripture", dev.get("scripture"), accent=True)
        field("Insight", dev.get("insight"))
        field("Reflection", dev.get("reflection"))
        field("Prayer", dev.get("prayer"), italic=True)
        field("Application", dev.get("application"))
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 4. Habit Tracker ──
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

    # ── 5a. Gratitude Daily ──
    st.markdown('<div class="cg-card"><h3>◈ Gratitude · Daily</h3>', unsafe_allow_html=True)
    grat_list(data.get("gratitude_points", []))
    field("Word of the Day", data.get("word_of_day"), accent=True)
    field("Lesson Learned", data.get("lesson_learned"), italic=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 5b. Gratitude Monthly (if data present) ──
    gm = data.get("monthly", {})
    has_monthly = any([gm.get("top_3_grateful"), gm.get("proud_of"), gm.get("month_in_one_word"), gm.get("next_month_objectives")])
    if has_monthly:
        st.markdown('<div class="cg-card"><h3>◈ Gratitude · Monthly</h3>', unsafe_allow_html=True)
        grat_list(gm.get("top_3_grateful", []))
        field("I Am Proud Of", gm.get("proud_of"))
        field("Month In One Word", gm.get("month_in_one_word"), accent=True)
        objs = gm.get("next_month_objectives", [])
        if objs:
            st.markdown('<div class="field-label">Next Month · I Am Looking Forward To</div>', unsafe_allow_html=True)
            grat_list(objs, arrow=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 6. Health Track ──
    hth = data.get("health", {})
    st.markdown('<div class="cg-card"><h3>◈ Health Track</h3>', unsafe_allow_html=True)
    field("Food", hth.get("food"))
    field("Meditation", hth.get("meditation"))
    field("Budget", hth.get("budget"))
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 7. Daily Motivation (always generated) ──
    dm = data.get("daily_motivation")
    if dm:
        st.markdown(f'<div class="cg-card"><h3>◈ Daily Motivation</h3><div class="motivation-text">{dm}</div></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────
def render_history(sb):
    try:
        result = sb.table("journal_entries").select("*").order("created_at", desc=True).limit(30).execute()
        entries = result.data
        if not entries:
            st.markdown('<div class="cg-card"><p style="color:#4a6175;font-size:0.85rem;text-align:center;margin:0;">No entries yet.</p></div>', unsafe_allow_html=True)
            return
        for e in entries:
            raw = e.get("extracted_data", {})
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: raw = {}
            mood = raw.get("mood") or "—"
            date_str = e.get("entry_date", "")
            with st.expander(f"📅 {date_str}  ·  {mood}"):
                try:
                    entry_dt = datetime.fromisoformat(date_str).replace(tzinfo=EAT) if date_str else get_eat_now()
                except:
                    entry_dt = get_eat_now()
                render_entry(raw, entry_dt)
    except Exception as ex:
        st.markdown(f'<div class="cg-error">History error: {ex}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    now = get_eat_now()
    sunday = is_sunday(now)

    st.markdown("""
    <div class="cg-hero">
      <h1>AUTOJOURNAL</h1>
      <div class="sub">CIPHER GHOST · PERSONAL OS</div>
    </div>
    """, unsafe_allow_html=True)

    tab_new, tab_history = st.tabs(["✦  New Entry", "◈  History"])

    with tab_new:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="cg-date-pill">{now.strftime("%A, %d %b %Y · %H:%M EAT")}</div>', unsafe_allow_html=True)
        if sunday:
            st.markdown('<div style="margin-top:0.5rem;"><span class="sunday-badge">✦ SUNDAY — Devotion active</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'Cinzel\',serif;font-size:0.72rem;letter-spacing:0.18em;color:#e8d48b;margin-bottom:0.4rem;">DUMP YOUR DAY</div>'
            '<div style="font-size:0.82rem;color:#4a6175;margin-bottom:0.7rem;line-height:1.45;">'
            'Even a single sentence works. The AI fills in everything else automatically — verse, prayer, word of the day, lesson, motivation.</div>',
            unsafe_allow_html=True,
        )

        user_input = st.text_area(
            label="journal_input",
            label_visibility="collapsed",
            placeholder=(
                "e.g. Today was a good day. Grateful for my family and a clean trade setup. "
                "Did chart analysis, no live trades. Ate well, meditated. Budget on track."
                "\n\nOr even just: 'Tough day. Missed my entries but stayed disciplined mentally.'"
                "\n\nThe AI generates the rest ✦"
            ),
            height=200,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.button("⚡  EXTRACT & SAVE JOURNAL")

        if submit:
            if not user_input.strip():
                st.markdown('<div class="cg-error">⚠ Write at least one sentence about your day.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Cipher Ghost AI is building your journal…"):
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
                        st.markdown('<div style="font-family:\'Cinzel\',serif;font-size:0.72rem;letter-spacing:0.18em;color:#e8d48b;margin-bottom:0.8rem;">YOUR JOURNAL FOR TODAY</div>', unsafe_allow_html=True)
                        render_entry(extracted, now)

                    except json.JSONDecodeError as e:
                        st.markdown(f'<div class="cg-error">⚠ AI returned malformed JSON. Try again.<br><small>{e}</small></div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="cg-error">⚠ {str(e)}</div>', unsafe_allow_html=True)

    with tab_history:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            sb = init_supabase()
            render_history(sb)
        except Exception as e:
            st.markdown(f'<div class="cg-error">⚠ Database error: {e}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
