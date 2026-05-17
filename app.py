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
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
  html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #080c10 !important; color: #c8d6e5 !important; }
  .main .block-container { padding: 1rem 1.1rem 4rem 1.1rem; max-width: 480px; margin: 0 auto; }
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="collapsedControl"] { display: none; }
  .cg-hero { text-align: center; padding: 1.8rem 0 0.6rem 0; }
  .cg-hero h1 { font-family: 'Cinzel', serif; font-size: 1.55rem; font-weight: 900; letter-spacing: 0.18em; color: #e8d48b; text-shadow: 0 0 24px rgba(232,212,139,0.35); margin: 0; }
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
  .delete-btn > button { background: rgba(200,80,80,0.15) !important; color: #e57373 !important; border: 1px solid rgba(200,80,80,0.3) !important; font-size: 0.72rem !important; padding: 0.3rem 0.6rem !important; letter-spacing: 0.08em !important; border-radius: 6px !important; width: auto !important; }
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

# ── Fixed Identity ──
CG_VISION = "I am a disciplined, patient, and consistently profitable trader living fully aligned with my purpose. I operate with clarity, faith, and emotional control. My life reflects financial freedom, stability, and impact, and I use my success to uplift my family, create opportunities, and leave a lasting legacy."
CG_GOALS = ["Achieve consistent trading profitability","Manage large trading capital ($500,000+)","Become financially independent","Support and uplift my family","Secure multiple income streams","Build a strong trading brand and mentorship platform","Own a professional trading setup","Travel freely and live with purpose","Mentor and guide other traders","Create lasting financial security and legacy"]
CG_AFFIRMATIONS = ["I am guided in my decisions.","I trade with discipline and patience.","I grow wiser every day.","I trust God's timing for my journey.","I am building a profitable and purposeful future.","I rest tonight with peace and clarity."]

EAT = pytz.timezone("Africa/Nairobi")
def get_eat_now(): return datetime.now(EAT)
def is_sunday(dt): return dt.weekday() == 6
def get_groq(): return Groq(api_key=st.secrets["GROQ_API_KEY"])
def init_supabase(): return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def is_empty_entry(data: dict) -> bool:
    """Check if an entry has no meaningful generated content."""
    if not data: return True
    has_prayer = bool(data.get("verse_of_day") or data.get("prayer"))
    has_motivation = bool(data.get("daily_motivation"))
    has_gratitude = bool(data.get("gratitude_points"))
    return not (has_prayer or has_motivation or has_gratitude)

def generate_daily_content(user_text: str, dt: datetime, sunday: bool) -> dict:
    day = dt.strftime("%A, %d %B %Y")
    system = f"""You are AutoJournal AI for Cipher Ghost — a professional trader and Christian.
Today is {day}. IS_SUNDAY: {sunday}.

Parse the journal entry and return a COMPLETE JSON object. For ANY field not in the entry, GENERATE it.

ALWAYS GENERATE (never leave null):
- verse_of_day: Real Bible verse relevant to trading/discipline/faith/the day. Format: "Book Ch:V — verse text"
- prayer: Heartfelt personal prayer for Cipher Ghost for this day
- word_of_day: Powerful word for trading psychology. Format: "Word — definition"  
- lesson_learned: Trading or life wisdom lesson
- daily_motivation: Strong mindset or trading psychology statement
- gratitude_points: Always 3 items. Extract from text first, generate remainder if fewer than 3 mentioned

If IS_SUNDAY=True, ALWAYS generate full devotion (never null):
- devotion.scripture, devotion.insight, devotion.reflection, devotion.prayer, devotion.application

ONLY extract (never generate):
- mood (default "Focused" if not mentioned)
- habit_tracker fields: "done"/"skipped"/null — ONLY from explicit mentions
- health.food, health.meditation, health.budget — ONLY from explicit mentions
- monthly fields — ONLY if explicitly mentioned

Return ONLY valid JSON, no markdown:
{{
  "mood": null,
  "verse_of_day": null,
  "prayer": null,
  "devotion": {{"scripture": null,"insight": null,"reflection": null,"prayer": null,"application": null}},
  "habit_tracker": {{"daily_journal": null,"chart_analysis": null,"trades": null,"clearness_brushing": null}},
  "gratitude_points": [],
  "word_of_day": null,
  "lesson_learned": null,
  "health": {{"food": null,"meditation": null,"budget": null}},
  "daily_motivation": null,
  "monthly": {{"top_3_grateful": [],"proud_of": null,"month_in_one_word": null,"next_month_objectives": []}}
}}"""
    client = get_groq()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_text}],
        temperature=0.3, max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)

def field(label, value, accent=False, italic=False):
    if not value and value != 0: return
    if isinstance(value, list): value = " · ".join([str(v) for v in value if v])
    css = "field-value" + (" accent" if accent else "") + (" italic" if italic else "")
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
            num = "→" if arrow else f"{i}."
            html += f'<div class="grat-point"><span class="grat-num">{num}</span><span class="grat-text">{p}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_entry(data: dict, dt: datetime):
    sunday = is_sunday(dt)
    st.markdown(f'<div class="cg-date-pill">📅 {dt.strftime("%A, %d %B %Y")} · EAT</div>', unsafe_allow_html=True)
    if sunday:
        st.markdown('<div style="margin-top:0.5rem;"><span class="sunday-badge">✦ SUNDAY DEVOTION MODE</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # General
    st.markdown('<div class="cg-card"><h3>◈ General Context</h3>', unsafe_allow_html=True)
    field("Mood", data.get("mood"), accent=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Vision (always fixed)
    st.markdown('<div class="cg-card"><h3>◈ Cipher Ghost · 5-Year Vision</h3>', unsafe_allow_html=True)
    st.markdown(f'<div class="vision-text">{CG_VISION}</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label">Goals & Manifestations</div>', unsafe_allow_html=True)
    for g in CG_GOALS:
        st.markdown(f'<div class="goal-item">◦ {g}</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-label" style="margin-top:0.8rem;">Daily Affirmations</div>', unsafe_allow_html=True)
    for a in CG_AFFIRMATIONS:
        st.markdown(f'<div class="affirmation-item">{a}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Prayer (always generated)
    st.markdown('<div class="cg-card"><h3>◈ Cipher Ghost · Daily Prayer</h3>', unsafe_allow_html=True)
    field("Verse of the Day", data.get("verse_of_day"), accent=True)
    field("Prayer", data.get("prayer"), italic=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Devotion — ONLY on Sundays, shown ONCE
    if sunday:
        dev = data.get("devotion", {}) or {}
        st.markdown('<div class="cg-card"><h3>◈ Cipher Ghost · Sunday Devotion</h3>', unsafe_allow_html=True)
        field("Scripture", dev.get("scripture"), accent=True)
        field("Insight", dev.get("insight"))
        field("Reflection", dev.get("reflection"))
        field("Prayer", dev.get("prayer"), italic=True)
        field("Application", dev.get("application"))
        st.markdown("</div>", unsafe_allow_html=True)

    # Habits
    ht = data.get("habit_tracker", {}) or {}
    st.markdown('<div class="cg-card"><h3>◈ Habit Tracker</h3>', unsafe_allow_html=True)
    badges = (habit_badge("Daily Journal", ht.get("daily_journal"))
              + habit_badge("Chart Analysis", ht.get("chart_analysis"))
              + habit_badge("Trades", ht.get("trades"))
              + habit_badge("Clearness/Brushing", ht.get("clearness_brushing")))
    st.markdown(f'<div class="habit-row">{badges}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Gratitude Daily
    st.markdown('<div class="cg-card"><h3>◈ Gratitude · Daily</h3>', unsafe_allow_html=True)
    grat_list(data.get("gratitude_points", []))
    field("Word of the Day", data.get("word_of_day"), accent=True)
    field("Lesson Learned", data.get("lesson_learned"), italic=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Gratitude Monthly
    gm = data.get("monthly", {}) or {}
    has_monthly = any([gm.get("top_3_grateful"), gm.get("proud_of"), gm.get("month_in_one_word"), gm.get("next_month_objectives")])
    if has_monthly:
        st.markdown('<div class="cg-card"><h3>◈ Gratitude · Monthly</h3>', unsafe_allow_html=True)
        grat_list(gm.get("top_3_grateful", []))
        field("I Am Proud Of", gm.get("proud_of"))
        field("Month In One Word", gm.get("month_in_one_word"), accent=True)
        if gm.get("next_month_objectives"):
            st.markdown('<div class="field-label">Next Month · Looking Forward To</div>', unsafe_allow_html=True)
            grat_list(gm.get("next_month_objectives", []), arrow=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Health
    hth = data.get("health", {}) or {}
    st.markdown('<div class="cg-card"><h3>◈ Health Track</h3>', unsafe_allow_html=True)
    field("Food", hth.get("food"))
    field("Meditation", hth.get("meditation"))
    field("Budget", hth.get("budget"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Motivation
    dm = data.get("daily_motivation")
    if dm:
        st.markdown(f'<div class="cg-card"><h3>◈ Daily Motivation</h3><div class="motivation-text">{dm}</div></div>', unsafe_allow_html=True)

def render_history(sb):
    try:
        result = sb.table("journal_entries").select("*").order("created_at", desc=True).limit(60).execute()
        entries = result.data
        if not entries:
            st.markdown('<div class="cg-card"><p style="color:#4a6175;font-size:0.85rem;text-align:center;margin:0;">No entries yet.</p></div>', unsafe_allow_html=True)
            return

        # Filter out empty entries automatically
        valid_entries = []
        for e in entries:
            raw = e.get("extracted_data", {})
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: raw = {}
            if not is_empty_entry(raw):
                e["_parsed"] = raw
                valid_entries.append(e)

        if not valid_entries:
            st.markdown('<div class="cg-card"><p style="color:#4a6175;font-size:0.85rem;text-align:center;margin:0;">No complete entries yet. Submit a new entry above.</p></div>', unsafe_allow_html=True)
            return

        for e in valid_entries:
            raw = e["_parsed"]
            mood = raw.get("mood") or "—"
            date_str = e.get("entry_date", "")
            entry_id = e.get("id")

            with st.expander(f"📅 {date_str}  ·  {mood}"):
                try:
                    entry_dt = datetime.fromisoformat(date_str).replace(tzinfo=EAT) if date_str else get_eat_now()
                except:
                    entry_dt = get_eat_now()
                render_entry(raw, entry_dt)

                # Delete button
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col2:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🗑 Delete", key=f"del_{entry_id}"):
                        st.session_state[f"confirm_{entry_id}"] = True
                    st.markdown("</div>", unsafe_allow_html=True)

                # Confirm delete
                if st.session_state.get(f"confirm_{entry_id}"):
                    st.warning("Are you sure you want to delete this entry?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✓ Yes, Delete", key=f"yes_{entry_id}"):
                            try:
                                sb.table("journal_entries").delete().eq("id", entry_id).execute()
                                st.session_state.pop(f"confirm_{entry_id}", None)
                                st.success("Entry deleted.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Delete failed: {ex}")
                    with c2:
                        if st.button("✗ Cancel", key=f"no_{entry_id}"):
                            st.session_state.pop(f"confirm_{entry_id}", None)
                            st.rerun()

    except Exception as ex:
        st.markdown(f'<div class="cg-error">History error: {ex}</div>', unsafe_allow_html=True)

def main():
    now = get_eat_now()
    sunday = is_sunday(now)

    st.markdown('<div class="cg-hero"><h1>AUTOJOURNAL</h1><div class="sub">CIPHER GHOST · PERSONAL OS</div></div>', unsafe_allow_html=True)

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
            'Even one sentence works. AI generates verse, prayer, word of day, lesson & motivation automatically.</div>',
            unsafe_allow_html=True,
        )
        user_input = st.text_area(
            label="journal_input", label_visibility="collapsed",
            placeholder="e.g. Good day. Grateful for family, health and progress. Did chart analysis, no trades. Ate clean, meditated 10 mins.\n\nOr just: 'Tough day but stayed disciplined.' — AI fills the rest ✦",
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
                        st.markdown(f'<div class="cg-error">⚠ AI returned malformed data. Try again.<br><small>{e}</small></div>', unsafe_allow_html=True)
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
