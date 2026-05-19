# AutoJournal v5 — Cipher Ghost Personal OS
import streamlit as st
from groq import Groq
import json, re, io, base64
from datetime import datetime, timedelta
import pytz
from supabase import create_client
from fpdf import FPDF

st.set_page_config(page_title="AutoJournal · Cipher Ghost", page_icon="👁️", layout="centered", initial_sidebar_state="collapsed")

# ── Dark mode state ──
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

DM = st.session_state.dark_mode
BG     = "#0d0d1a" if DM else "#f4f1eb"
BG2    = "#141428" if DM else "#ffffff"
BG3    = "#1a1a2e" if DM else "#f8f6f2"
TEXT   = "#e8e8f0" if DM else "#1a1a2e"
TEXT2  = "#a0a0c0" if DM else "#555555"
BORDER = "#2a2a4a" if DM else "#e0e0e0"
CARD_SHADOW = "0 2px 12px rgba(0,0,0,0.4)" if DM else "0 2px 12px rgba(0,0,0,0.07)"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Montserrat:wght@300;400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Oswald:wght@300;400;500;600&family=Dancing+Script:wght@600;700&display=swap');
  html,body,[class*="css"]{{font-family:'Montserrat',sans-serif;background-color:{BG}!important;color:{TEXT}!important;}}
  .stApp,.stAppViewContainer,section[data-testid="stAppViewContainer"],.stAppViewBlockContainer{{background-color:{BG}!important;}}
  .main .block-container{{padding:0 0.8rem 4rem 0.8rem;max-width:480px;margin:0 auto;background:{BG}!important;}}
  #MainMenu,footer,header{{visibility:hidden;}}
  [data-testid="collapsedControl"]{{display:none;}}
  .cg-hero{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:2rem 1.5rem 1.8rem;text-align:center;margin:0 -0.8rem 1.5rem -0.8rem;position:relative;overflow:hidden;}}
  .cg-hero::before{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,0.2) 0%,transparent 70%);}}
  .cg-hero h1{{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;color:#d4af37;letter-spacing:0.12em;margin:0;line-height:1.1;text-shadow:0 2px 20px rgba(212,175,55,0.4);}}
  .cg-hero .sub{{font-family:'Oswald',sans-serif;font-size:0.65rem;color:rgba(255,255,255,0.5);letter-spacing:0.4em;margin-top:0.3rem;}}
  .cg-date-pill{{display:inline-block;background:rgba(212,175,55,0.15);border:1px solid rgba(212,175,55,0.4);border-radius:30px;padding:0.25rem 1rem;font-family:'Oswald',sans-serif;font-size:0.68rem;color:#d4af37;letter-spacing:0.12em;margin-top:0.6rem;}}
  .card{{background:{BG2};border-radius:14px;padding:1.2rem 1.1rem 1rem;margin-bottom:1rem;box-shadow:{CARD_SHADOW};border-top:4px solid #ccc;border:1px solid {BORDER};border-top-width:4px;}}
  .card-general{{border-top-color:#4834d4!important;}} .card-vision{{border-top-color:#b8860b!important;}} .card-prayer{{border-top-color:#1a5fa8!important;}}
  .card-devotion{{border-top-color:#7d3c98!important;}} .card-habit{{border-top-color:#1e8449!important;}} .card-gratitude{{border-top-color:#d35400!important;}}
  .card-health{{border-top-color:#c0392b!important;}} .card-motivation{{border-top-color:#0e8c74!important;}} .card-stats{{border-top-color:#2980b9!important;}}
  .card-title{{font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:900;margin:0 0 1rem 0;letter-spacing:0.02em;}}
  .title-general{{color:#4834d4;}} .title-vision{{color:#b8860b;}} .title-prayer{{color:#1a5fa8;}} .title-devotion{{color:#7d3c98;}}
  .title-habit{{color:#1e8449;}} .title-gratitude{{color:#d35400;}} .title-health{{color:#c0392b;}} .title-motivation{{color:#0e8c74;}} .title-stats{{color:#2980b9;}}
  .fl{{font-family:'Oswald',sans-serif;font-size:0.62rem;letter-spacing:0.18em;text-transform:uppercase;color:{TEXT2};margin-bottom:0.15rem;margin-top:0.6rem;}}
  .fv{{font-family:'Cormorant Garamond',serif;font-size:1rem;color:{TEXT};line-height:1.5;padding-left:0.6rem;border-left:3px solid {BORDER};margin-bottom:0.3rem;font-weight:600;}}
  .fv-accent{{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:{TEXT};padding-left:0.6rem;border-left:3px solid #d4af37;margin-bottom:0.3rem;}}
  .mood-badge{{display:inline-block;background:linear-gradient(135deg,#4834d4,#7c3aed);color:white;border-radius:20px;padding:0.3rem 1rem;font-family:'Oswald',sans-serif;font-size:0.85rem;letter-spacing:0.1em;font-weight:500;}}
  .vision-quote{{font-family:'Cormorant Garamond',serif;font-size:1.05rem;font-style:italic;color:{TEXT};line-height:1.7;padding:0.8rem 1rem;background:{"rgba(212,175,55,0.08)" if DM else "linear-gradient(135deg,#fffdf5,#fff9e6)"};border-left:4px solid #d4af37;border-radius:0 8px 8px 0;margin-bottom:0.8rem;}}
  .goal-item{{font-family:'Montserrat',sans-serif;font-size:0.82rem;color:{TEXT};padding:0.3rem 0 0.3rem 1rem;border-bottom:1px solid {BORDER};display:flex;align-items:center;gap:0.5rem;font-weight:500;}}
  .affirmation-item{{font-family:'Dancing Script',cursive;font-size:1.05rem;color:#4c3fbf;padding:0.2rem 0 0.2rem 0.5rem;border-left:2px solid rgba(108,99,255,0.3);margin-bottom:0.3rem;}}
  .verse-box{{background:{"rgba(26,95,168,0.15)" if DM else "linear-gradient(135deg,#eef4fb,#e8f3ff)"};border-radius:10px;padding:0.9rem 1rem;border-left:4px solid #1a5fa8;margin-bottom:0.7rem;}}
  .verse-ref{{font-family:'Oswald',sans-serif;font-size:0.75rem;color:#1a5fa8;letter-spacing:0.1em;margin-bottom:0.3rem;font-weight:600;}}
  .verse-text{{font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-style:italic;color:{TEXT};line-height:1.6;font-weight:600;}}
  .prayer-text{{font-family:'Cormorant Garamond',serif;font-size:1rem;color:{TEXT};line-height:1.7;font-style:italic;font-weight:600;}}
  .sunday-badge{{background:linear-gradient(135deg,#7d3c98,#6c3483);color:white;border-radius:6px;padding:0.25rem 0.8rem;font-family:'Oswald',sans-serif;font-size:0.65rem;letter-spacing:0.18em;display:inline-block;margin-bottom:0.8rem;}}
  .habit-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.5rem;}}
  .habit-card{{border-radius:10px;padding:0.7rem 0.8rem;display:flex;align-items:center;gap:0.5rem;font-family:'Montserrat',sans-serif;font-size:0.78rem;font-weight:700;border:2px solid transparent;}}
  .habit-done-card{{background:{"rgba(30,132,73,0.2)" if DM else "#eafaf1"};border-color:#27ae60;color:{"#58d68d" if DM else "#145a32"};}}
  .habit-skip-card{{background:{"rgba(192,57,43,0.2)" if DM else "#fdf2f2"};border-color:#e74c3c;color:{"#e57373" if DM else "#922b21"};}}
  .habit-na-card{{background:{"rgba(100,100,120,0.2)" if DM else "#f0f0f0"};border-color:{BORDER};color:{TEXT2};}}
  .habit-journal-area{{background:{"rgba(30,132,73,0.1)" if DM else "#f0f7f0"};border:1px solid {"rgba(39,174,96,0.3)" if DM else "#c8e6c9"};border-radius:8px;padding:0.6rem 0.8rem;margin-top:0.5rem;font-family:'Cormorant Garamond',serif;font-size:0.98rem;color:{TEXT};line-height:1.5;font-weight:600;}}
  .habit-journal-label{{font-family:'Oswald',sans-serif;font-size:0.6rem;letter-spacing:0.15em;color:#1e8449;text-transform:uppercase;margin-bottom:0.3rem;}}
  .grat-item{{display:flex;gap:0.8rem;align-items:flex-start;padding:0.6rem 0;border-bottom:1px solid {BORDER};}}
  .grat-num{{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:900;color:#d35400;min-width:1.5rem;line-height:1;}}
  .grat-text{{font-family:'Cormorant Garamond',serif;font-size:1rem;color:{TEXT};line-height:1.4;font-weight:600;}}
  .word-box{{background:{"rgba(211,84,0,0.1)" if DM else "linear-gradient(135deg,#fff8f0,#fff3e6)"};border-radius:10px;padding:0.8rem 1rem;border-left:4px solid #d35400;margin:0.7rem 0;}}
  .word-title{{font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:700;color:#d35400;}}
  .word-def{{font-family:'Cormorant Garamond',serif;font-size:1rem;color:{TEXT};font-style:italic;font-weight:600;}}
  .lesson-box{{background:{"rgba(72,52,212,0.1)" if DM else "#f8f5ff"};border-radius:10px;padding:0.8rem 1rem;border-left:4px solid #4834d4;font-family:'Cormorant Garamond',serif;font-size:1rem;color:{TEXT};font-style:italic;line-height:1.6;font-weight:600;}}
  .food-rec{{background:{"rgba(192,57,43,0.1)" if DM else "linear-gradient(135deg,#fef9f9,#fff0f0)"};border-radius:10px;padding:0.9rem 1rem;border-left:4px solid #c0392b;margin-bottom:0.7rem;}}
  .food-title{{font-family:'Oswald',sans-serif;font-size:0.7rem;color:#c0392b;letter-spacing:0.15em;margin-bottom:0.4rem;font-weight:600;}}
  .food-meal{{font-family:'Montserrat',sans-serif;font-size:0.84rem;color:{TEXT};font-weight:600;padding:0.25rem 0;display:flex;align-items:center;gap:0.4rem;}}
  .health-stat{{display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0.8rem;border-radius:8px;background:{BG3};margin-bottom:0.4rem;font-family:'Montserrat',sans-serif;font-size:0.85rem;font-weight:600;color:{TEXT};}}
  .motivation-box{{background:{"rgba(14,140,116,0.1)" if DM else "linear-gradient(135deg,#e8fdf8,#d5f5ee)"};border-radius:12px;padding:1.2rem;border-left:5px solid #0e8c74;text-align:center;}}
  .motivation-text{{font-family:'Playfair Display',serif;font-size:1.1rem;font-style:italic;color:{"#1abc9c" if DM else "#0a4d3d"};line-height:1.6;font-weight:700;}}
  .stat-box{{background:{BG3};border-radius:12px;padding:1rem;text-align:center;border:1px solid {BORDER};}}
  .stat-num{{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:900;color:#2980b9;line-height:1;}}
  .stat-label{{font-family:'Oswald',sans-serif;font-size:0.62rem;color:{TEXT2};letter-spacing:0.15em;margin-top:0.2rem;text-transform:uppercase;}}
  .week-summary-box{{background:{"rgba(41,128,185,0.1)" if DM else "#eef6fc"};border-radius:12px;padding:1rem 1.1rem;border-left:4px solid #2980b9;font-family:'Cormorant Garamond',serif;font-size:1rem;color:{TEXT};line-height:1.7;font-weight:600;}}
  .history-card{{background:white;border-radius:14px;border:1px solid #e0e0e0;box-shadow:0 3px 12px rgba(0,0,0,0.08);margin-bottom:0.5rem;overflow:hidden;}}
  .history-header{{background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:0.9rem 1.1rem;display:flex;justify-content:space-between;align-items:center;}}
  textarea{{background:{BG2}!important;color:{TEXT}!important;border:2px solid {BORDER}!important;border-radius:12px!important;font-family:'Montserrat',sans-serif!important;font-size:0.95rem!important;line-height:1.6!important;}}
  textarea:focus{{border-color:#4834d4!important;box-shadow:0 0 0 3px rgba(72,52,212,0.1)!important;}}
  .stButton>button{{width:100%;background:linear-gradient(135deg,#1a1a2e,#0f3460)!important;color:#d4af37!important;font-family:'Oswald',sans-serif!important;font-weight:500!important;letter-spacing:0.2em!important;font-size:0.9rem!important;border:none!important;border-radius:10px!important;padding:0.85rem!important;text-transform:uppercase!important;}}
  .cg-success{{background:{"rgba(30,132,73,0.15)" if DM else "#eafaf1"};border:1px solid #27ae60;border-radius:10px;padding:0.9rem 1rem;color:{"#58d68d" if DM else "#1e8449"};font-family:'Oswald',sans-serif;font-size:0.78rem;text-align:center;letter-spacing:0.1em;}}
  .cg-error{{background:{"rgba(192,57,43,0.15)" if DM else "#fdf2f2"};border:1px solid #e74c3c;border-radius:10px;padding:0.9rem 1rem;color:{"#e57373" if DM else "#c0392b"};font-family:'Montserrat',sans-serif;font-size:0.82rem;}}
  .stTabs [data-baseweb="tab-list"]{{background:{"#1a1a2e" if DM else "#e8e4f0"};border-radius:10px;gap:2px;padding:4px;border:1px solid {BORDER};}}
  .stTabs [data-baseweb="tab"]{{font-family:'Oswald',sans-serif;font-weight:400;font-size:0.78rem;letter-spacing:0.1em;color:{"#aaa" if DM else "#555"};border-radius:8px;padding:0.35rem 0.5rem;}}
  .stTabs [aria-selected="true"]{{background:#4834d4!important;color:white!important;}}
  ::-webkit-scrollbar{{width:4px;}} ::-webkit-scrollbar-track{{background:{BG};}} ::-webkit-scrollbar-thumb{{background:{"#2a2a4a" if DM else "#ccc"};border-radius:2px;}}
</style>
""", unsafe_allow_html=True)

# ── Constants ──
CG_VISION = "I am a disciplined, patient, and consistently profitable trader living fully aligned with my purpose. I operate with clarity, faith, and emotional control. My life reflects financial freedom, stability, and impact, and I use my success to uplift my family, create opportunities, and leave a lasting legacy."
CG_GOALS = ["Achieve consistent trading profitability","Manage large trading capital ($500,000+)","Become financially independent","Support and uplift my family","Secure multiple income streams","Build a strong trading brand and mentorship platform","Own a professional trading setup","Travel freely and live with purpose","Mentor and guide other traders","Create lasting financial security and legacy"]
CG_AFFIRMATIONS = ["I am guided in my decisions.","I trade with discipline and patience.","I grow wiser every day.","I trust God's timing for my journey.","I am building a profitable and purposeful future.","I rest tonight with peace and clarity."]

EAT = pytz.timezone("Africa/Nairobi")
def get_eat_now(): return datetime.now(EAT)
def is_sunday(dt): return dt.weekday() == 6
def init_supabase(): return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
def is_empty_entry(data): return not (data.get("verse_of_day") or data.get("daily_motivation") or data.get("gratitude_points")) if isinstance(data, dict) else True

def safe_parse(raw):
    if isinstance(raw, dict): return raw
    if isinstance(raw, str):
        try: return json.loads(raw)
        except: return {}
    return {}

# ── AI ──
def ai_call(system, user, max_tokens=2000):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.3, max_tokens=max_tokens,
    )
    raw = r.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*","",raw); raw = re.sub(r"\s*```$","",raw)
    return raw

def generate_daily_content(user_text, dt, sunday):
    day = dt.strftime("%A, %d %B %Y")
    system = f"""You are AutoJournal AI for Cipher Ghost — professional trader and Christian in East Africa.
Today: {day}. IS_SUNDAY: {sunday}.

ALWAYS GENERATE (never null):
- verse_of_day: {{"reference":"Book Ch:V","text":"verse text"}}
- prayer: heartfelt 2-4 sentence prayer for Cipher Ghost
- word_of_day: {{"word":"Word","definition":"meaning"}}
- lesson_learned: 1-2 sentence trading/life wisdom
- daily_motivation: 1 powerful mindset statement
- gratitude_points: always 3 strings (extract then generate)
- food_recommendation: {{"breakfast":"...","lunch":"...","dinner":"...","snack":"...","budget_note":"..."}} — balanced low-budget East Africa meals

IF IS_SUNDAY=True ALWAYS generate devotion fully.

EXTRACT ONLY:
- mood (default "Focused"), habit_tracker fields ("done"/"skipped"/null),
  health.food_eaten, health.meditation, health.budget, monthly fields,
  trade stats: trade_result ("win"/"loss"/"be"), trade_rr (number like 1.5), trade_pair (e.g. "XAUUSD")

Return ONLY valid JSON:
{{"mood":null,"verse_of_day":{{"reference":null,"text":null}},"prayer":null,
"devotion":{{"scripture":null,"insight":null,"reflection":null,"prayer":null,"application":null}},
"habit_tracker":{{"daily_journal":null,"chart_analysis":null,"chart_notes":null,"trades":null,"trade_notes":null,"clearness_brushing":null}},
"trade_stats":{{"result":null,"rr":null,"pair":null}},
"gratitude_points":[],"word_of_day":{{"word":null,"definition":null}},"lesson_learned":null,
"food_recommendation":{{"breakfast":null,"lunch":null,"dinner":null,"snack":null,"budget_note":null}},
"health":{{"food_eaten":null,"meditation":null,"budget":null}},
"daily_motivation":null,
"monthly":{{"top_3_grateful":[],"proud_of":null,"month_in_one_word":null,"next_month_objectives":[]}}}}"""
    return json.loads(ai_call(system, user_text))

def generate_weekly_summary(entries_text, week_range):
    system = f"""You are AutoJournal AI reviewing Cipher Ghost's week ({week_range}).
Analyze the journal entries and write a rich, personal weekly summary covering:
1. Overall mood trend and emotional arc of the week
2. Trading performance highlights (wins, losses, patterns noticed)
3. Spiritual/faith highlights
4. Gratitude themes that kept appearing
5. Key lessons learned this week
6. What to focus on next week
Write in second person ("You..."), warm, motivating, honest. 3-4 paragraphs. Plain text only."""
    return ai_call(system, entries_text, max_tokens=800)

# ── Trading Stats ──
def compute_stats(entries):
    wins = losses = be = total_rr = streak = current_streak = max_streak = 0
    last_result = None
    journal_days = 0
    for e in entries:
        data = e.get("_parsed", {})
        if not isinstance(data, dict): continue
        journal_days += 1
        ts = data.get("trade_stats", {}) or {}
        result = ts.get("result")
        rr = ts.get("rr")
        if result == "win": wins += 1
        elif result == "loss": losses += 1
        elif result == "be": be += 1
        if rr:
            try: total_rr += float(rr)
            except: pass
        # Streak
        if result in ("win","be"):
            if last_result in ("win","be","none",None): current_streak += 1
            else: current_streak = 1
        elif result == "loss":
            current_streak = 0
        max_streak = max(max_streak, current_streak)
        last_result = result
    total_trades = wins + losses + be
    win_rate = round((wins / total_trades * 100)) if total_trades else 0
    avg_rr = round(total_rr / total_trades, 2) if total_trades else 0
    return {
        "wins": wins, "losses": losses, "be": be,
        "total_trades": total_trades, "win_rate": win_rate,
        "avg_rr": avg_rr, "current_streak": current_streak,
        "max_streak": max_streak, "journal_days": journal_days,
    }


# ── PDF Export ──
class JournalPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(180, 140, 50)
        self.cell(0, 12, "AUTOJOURNAL", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 140)
        self.cell(0, 6, "CIPHER GHOST  ·  PERSONAL OS", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_draw_color(212, 175, 55)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(160, 160, 180)
        self.cell(0, 10, f"Page {self.page_no()} — Cipher Ghost Personal OS", align="C")

def section_title(pdf, title, color):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*color)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

def add_field(pdf, label, value):
    if not value: return
    if isinstance(value, list): value = "  ·  ".join([str(v) for v in value if v])
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(100, 100, 120)
    pdf.cell(0, 5, label.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 50)
    pdf.multi_cell(0, 5, str(value))
    pdf.ln(1)

def generate_pdf(data, dt, raw_text=""):
    pdf = JournalPDF()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=15)
    sunday = is_sunday(dt)

    # Date header
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 10, dt.strftime("%A, %d %B %Y  ·  EAT"), new_x="LMARGIN", new_y="NEXT")
    if data.get("mood"):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 80, 200)
        pdf.cell(0, 6, f"Mood: {data['mood']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Vision
    section_title(pdf, "CIPHER GHOST · 5-YEAR VISION", (180, 140, 50))
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(50, 50, 80)
    pdf.multi_cell(0, 5, CG_VISION)
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(100,100,120)
    pdf.cell(0, 5, "GOALS & MANIFESTATIONS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(30,30,50)
    for g in CG_GOALS:
        pdf.cell(0, 4.5, f"  ◆  {g}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(100,100,120)
    pdf.cell(0, 5, "DAILY AFFIRMATIONS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(76,63,191)
    for a in CG_AFFIRMATIONS:
        pdf.cell(0, 4.5, f"  {a}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Prayer
    section_title(pdf, "DAILY PRAYER", (26, 95, 168))
    vod = data.get("verse_of_day") or {}
    if isinstance(vod, str): vod = {"reference":"", "text": vod}
    if vod.get("reference"): add_field(pdf, "Verse of the Day", f'{vod.get("reference","")} — {vod.get("text","")}')
    add_field(pdf, "Prayer", data.get("prayer"))
    pdf.ln(2)

    # Devotion
    if sunday:
        section_title(pdf, "SUNDAY DEVOTION", (125, 60, 152))
        dev = data.get("devotion") or {}
        add_field(pdf, "Scripture", dev.get("scripture"))
        add_field(pdf, "Insight", dev.get("insight"))
        add_field(pdf, "Reflection", dev.get("reflection"))
        add_field(pdf, "Prayer", dev.get("prayer"))
        add_field(pdf, "Application", dev.get("application"))
        pdf.ln(2)

    # Habits
    section_title(pdf, "HABIT TRACKER", (30, 132, 73))
    ht = data.get("habit_tracker") or {}
    def status_str(s): return "✓ Done" if str(s or "").lower()=="done" else ("✗ Skipped" if s else "○ N/A")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30,30,50)
    pdf.cell(45, 5, f"Journal: {status_str(ht.get('daily_journal'))}")
    pdf.cell(50, 5, f"Chart Analysis: {status_str(ht.get('chart_analysis'))}")
    pdf.cell(40, 5, f"Trades: {status_str(ht.get('trades'))}", new_x="LMARGIN", new_y="NEXT")
    if ht.get("chart_notes"): add_field(pdf, "Chart Notes", ht["chart_notes"])
    if ht.get("trade_notes"): add_field(pdf, "Trade Journal", ht["trade_notes"])
    pdf.ln(2)

    # Gratitude
    section_title(pdf, "GRATITUDE · DAILY", (211, 84, 0))
    gpts = data.get("gratitude_points") or []
    for i,p in enumerate(gpts[:3],1):
        if p:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(211,84,0)
            pdf.cell(8, 5, str(i)+".")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30,30,50)
            pdf.multi_cell(0, 5, str(p))
    wod = data.get("word_of_day") or {}
    if isinstance(wod, str): wod = {"word": wod}
    if wod.get("word"): add_field(pdf, "Word of the Day", f'{wod["word"]} — {wod.get("definition","")}')
    add_field(pdf, "Lesson Learned", data.get("lesson_learned"))
    pdf.ln(2)

    # Health
    section_title(pdf, "HEALTH TRACK", (192, 57, 43))
    hth = data.get("health") or {}
    fr = data.get("food_recommendation") or {}
    add_field(pdf, "Food Eaten", hth.get("food_eaten"))
    add_field(pdf, "Meditation", hth.get("meditation"))
    add_field(pdf, "Budget", hth.get("budget"))
    if fr.get("breakfast"):
        add_field(pdf, "AI Meal Plan", f'Breakfast: {fr.get("breakfast","")} | Lunch: {fr.get("lunch","")} | Dinner: {fr.get("dinner","")} | Snack: {fr.get("snack","")}')
    pdf.ln(2)

    # Motivation
    if data.get("daily_motivation"):
        section_title(pdf, "DAILY MOTIVATION", (14, 140, 116))
        pdf.set_font("Helvetica", "BI", 10)
        pdf.set_text_color(14, 77, 61)
        pdf.multi_cell(0, 6, f'"{data["daily_motivation"]}"')
        pdf.ln(2)

    # Raw entry
    if raw_text:
        section_title(pdf, "ORIGINAL JOURNAL ENTRY", (100, 100, 120))
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(80, 80, 100)
        pdf.multi_cell(0, 5, raw_text)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()

# ── Render Entry ──
def render_entry(data, dt):
    DM = st.session_state.dark_mode
    TEXT = "#e8e8f0" if DM else "#1a1a2e"
    sunday = is_sunday(dt)
    st.markdown(f'<div class="cg-date-pill">📅 {dt.strftime("%A, %d %B %Y")} · EAT</div>', unsafe_allow_html=True)
    if sunday:
        st.markdown('<div style="margin-top:0.4rem;"><span class="sunday-badge">✦ SUNDAY DEVOTION MODE</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # General
    st.markdown(f'<div class="card card-general"><div class="card-title title-general">✦ General Context</div>', unsafe_allow_html=True)
    mood = data.get("mood") or "Focused"
    st.markdown(f'<div class="fl">Mood</div><div style="margin-top:0.3rem;"><span class="mood-badge">{mood}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Vision
    st.markdown(f'<div class="card card-vision"><div class="card-title title-vision">◈ Cipher Ghost · 5-Year Vision</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="vision-quote">{CG_VISION}</div>', unsafe_allow_html=True)
    st.markdown('<div class="fl">Goals & Manifestations</div>', unsafe_allow_html=True)
    for g in CG_GOALS:
        st.markdown(f'<div class="goal-item"><span style="color:#d4af37;font-size:0.6rem;">◆</span>{g}</div>', unsafe_allow_html=True)
    st.markdown('<div class="fl" style="margin-top:0.8rem;">Daily Affirmations</div>', unsafe_allow_html=True)
    for a in CG_AFFIRMATIONS:
        st.markdown(f'<div class="affirmation-item">{a}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Prayer
    vod = data.get("verse_of_day") or {}
    if isinstance(vod, str): vod = {"reference": "", "text": vod}
    st.markdown(f'<div class="card card-prayer"><div class="card-title title-prayer">🙏 CG Daily Prayer</div>', unsafe_allow_html=True)
    if vod.get("text"):
        st.markdown(f'<div class="verse-box"><div class="verse-ref">{vod.get("reference","")}</div><div class="verse-text">{vod.get("text","")}</div></div>', unsafe_allow_html=True)
    if data.get("prayer"):
        st.markdown(f'<div class="fl">Prayer</div><div class="prayer-text">{data["prayer"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Devotion
    if sunday:
        dev = data.get("devotion") or {}
        st.markdown(f'<div class="card card-devotion"><div class="card-title title-devotion">✝ Sunday Devotion</div>', unsafe_allow_html=True)
        if dev.get("scripture"): st.markdown(f'<div class="fl">Scripture</div><div class="fv-accent">{dev["scripture"]}</div>', unsafe_allow_html=True)
        if dev.get("insight"): st.markdown(f'<div class="fl">Insight</div><div class="fv">{dev["insight"]}</div>', unsafe_allow_html=True)
        if dev.get("reflection"): st.markdown(f'<div class="fl">Reflection</div><div class="fv">{dev["reflection"]}</div>', unsafe_allow_html=True)
        if dev.get("prayer"): st.markdown(f'<div class="fl">Prayer</div><div class="prayer-text">{dev["prayer"]}</div>', unsafe_allow_html=True)
        if dev.get("application"): st.markdown(f'<div class="fl">Application</div><div class="fv">{dev["application"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Habits
    ht = data.get("habit_tracker") or {}
    st.markdown(f'<div class="card card-habit"><div class="card-title title-habit">📋 Habit Tracker</div>', unsafe_allow_html=True)
    def hc(icon, label, status):
        if status is None: cls,mk="habit-na-card","○"
        elif str(status).lower()=="done": cls,mk="habit-done-card","✓"
        else: cls,mk="habit-skip-card","✗"
        return f'<div class="habit-card {cls}"><span>{icon}</span><span>{mk} {label}</span></div>'
    st.markdown(f'<div class="habit-grid">{hc("📓","Daily Journal",ht.get("daily_journal"))}{hc("📊","Chart Analysis",ht.get("chart_analysis"))}{hc("💹","Trades",ht.get("trades"))}{hc("🪥","Clearness/Brushing",ht.get("clearness_brushing"))}</div>', unsafe_allow_html=True)
    if ht.get("chart_notes"): st.markdown(f'<div class="habit-journal-area" style="margin-top:0.7rem;border-left:3px solid #1e8449;"><div class="habit-journal-label">📊 Chart Notes</div>{ht["chart_notes"]}</div>', unsafe_allow_html=True)
    if ht.get("trade_notes"): st.markdown(f'<div class="habit-journal-area" style="margin-top:0.5rem;border-left:3px solid #2980b9;"><div class="habit-journal-label" style="color:#2980b9;">💹 Trade Journal</div>{ht["trade_notes"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Gratitude Daily
    gpts = data.get("gratitude_points") or []
    wod = data.get("word_of_day") or {}
    if isinstance(wod, str): wod = {"word": wod, "definition": ""}
    st.markdown(f'<div class="card card-gratitude"><div class="card-title title-gratitude">🙌 Gratitude · Daily</div>', unsafe_allow_html=True)
    for i,p in enumerate(gpts[:3],1):
        if p: st.markdown(f'<div class="grat-item"><span class="grat-num">{i}</span><span class="grat-text">{p}</span></div>', unsafe_allow_html=True)
    if wod.get("word"): st.markdown(f'<div class="word-box"><div class="fl" style="color:#d35400;">Word of the Day</div><div class="word-title">{wod["word"]}</div><div class="word-def">{wod.get("definition","")}</div></div>', unsafe_allow_html=True)
    if data.get("lesson_learned"): st.markdown(f'<div class="fl">Lesson Learned</div><div class="lesson-box">{data["lesson_learned"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Monthly
    gm = data.get("monthly") or {}
    if any([gm.get("top_3_grateful"),gm.get("proud_of"),gm.get("month_in_one_word"),gm.get("next_month_objectives")]):
        st.markdown(f'<div class="card card-gratitude"><div class="card-title title-gratitude">🗓 Gratitude · Monthly</div>', unsafe_allow_html=True)
        for i,p in enumerate((gm.get("top_3_grateful") or [])[:3],1):
            if p: st.markdown(f'<div class="grat-item"><span class="grat-num">{i}</span><span class="grat-text">{p}</span></div>', unsafe_allow_html=True)
        if gm.get("proud_of"): st.markdown(f'<div class="fl">Proud Of</div><div class="fv">{gm["proud_of"]}</div>', unsafe_allow_html=True)
        if gm.get("month_in_one_word"): st.markdown(f'<div class="fl">Month In One Word</div><div class="fv-accent">{gm["month_in_one_word"]}</div>', unsafe_allow_html=True)
        if gm.get("next_month_objectives"):
            st.markdown('<div class="fl">Next Month</div>', unsafe_allow_html=True)
            for o in (gm["next_month_objectives"] or [])[:3]:
                if o: st.markdown(f'<div class="goal-item"><span style="color:#d35400;">→</span>{o}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Health
    hth = data.get("health") or {}
    fr = data.get("food_recommendation") or {}
    st.markdown(f'<div class="card card-health"><div class="card-title title-health">❤️ Health Track</div>', unsafe_allow_html=True)
    if hth.get("food_eaten"): st.markdown(f'<div class="health-stat"><span>🍽️</span><span><b>Ate:</b> {hth["food_eaten"]}</span></div>', unsafe_allow_html=True)
    if hth.get("meditation"): st.markdown(f'<div class="health-stat"><span>🧘</span><span><b>Meditation:</b> {hth["meditation"]}</span></div>', unsafe_allow_html=True)
    if hth.get("budget"): st.markdown(f'<div class="health-stat"><span>💰</span><span><b>Budget:</b> {hth["budget"]}</span></div>', unsafe_allow_html=True)
    if fr.get("breakfast"):
        st.markdown('<div class="food-rec"><div class="food-title">🤖 AI Meal Plan · Today</div>', unsafe_allow_html=True)
        for icon,key in [("🌅","breakfast"),("☀️","lunch"),("🌙","dinner"),("🍎","snack")]:
            if fr.get(key): st.markdown(f'<div class="food-meal">{icon} <b>{key.title()}:</b> {fr[key]}</div>', unsafe_allow_html=True)
        if fr.get("budget_note"): st.markdown(f'<div class="food-meal" style="color:{TEXT2};font-size:0.75rem;">💡 {fr["budget_note"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Motivation
    if data.get("daily_motivation"):
        st.markdown(f'<div class="card card-motivation"><div class="card-title title-motivation">⚡ Daily Motivation</div><div class="motivation-box"><div class="motivation-text">{data["daily_motivation"]}</div></div></div>', unsafe_allow_html=True)

# ── Stats Tab ──
def render_stats(sb):
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        result = sb.table("journal_entries").select("*").order("created_at", desc=True).limit(90).execute()
        entries = []
        for e in (result.data or []):
            if not isinstance(e, dict): continue
            parsed = safe_parse(e.get("extracted_data", {}))
            if not is_empty_entry(parsed):
                e["_parsed"] = parsed
                entries.append(e)

        if not entries:
            st.markdown('<div class="cg-error">No entries yet to analyze.</div>', unsafe_allow_html=True)
            return

        stats = compute_stats(entries)

        st.markdown(f'<div class="card card-stats"><div class="card-title title-stats">📊 Trading Performance</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["win_rate"]}%</div><div class="stat-label">Win Rate</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["avg_rr"]}R</div><div class="stat-label">Avg R:R</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["current_streak"]}</div><div class="stat-label">Streak</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c4,c5,c6 = st.columns(3)
        with c4: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#27ae60;">{stats["wins"]}</div><div class="stat-label">Wins</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#e74c3c;">{stats["losses"]}</div><div class="stat-label">Losses</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#f39c12;">{stats["be"]}</div><div class="stat-label">B/E</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c7,c8 = st.columns(2)
        with c7: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["journal_days"]}</div><div class="stat-label">Journal Days</div></div>', unsafe_allow_html=True)
        with c8: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["max_streak"]}</div><div class="stat-label">Best Streak</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Weekly Summary
        st.markdown(f'<div class="card card-stats"><div class="card-title title-stats">📅 Weekly AI Summary</div>', unsafe_allow_html=True)
        now = get_eat_now()
        week_start = now - timedelta(days=now.weekday())
        week_entries = [e for e in entries if e.get("entry_date","") >= week_start.strftime("%Y-%m-%d")]
        if st.button("🤖 Generate This Week's Summary"):
            if not week_entries:
                st.warning("No entries this week yet.")
            else:
                with st.spinner("AI is reviewing your week…"):
                    week_texts = []
                    for e in week_entries:
                        d = e.get("entry_date","")
                        raw_text = e.get("raw_text","")
                        mood = e.get("_parsed",{}).get("mood","")
                        week_texts.append(f"[{d} - {mood}]: {raw_text}")
                    combined = "\n\n".join(week_texts)
                    week_range = f"{week_start.strftime('%d %b')} – {now.strftime('%d %b %Y')}"
                    summary = generate_weekly_summary(combined, week_range)
                    st.markdown(f'<div class="week-summary-box">{summary.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as ex:
        st.markdown(f'<div class="cg-error">Stats error: {ex}</div>', unsafe_allow_html=True)

# ── History Tab ──
def render_history(sb):
    try:
        result = sb.table("journal_entries").select("*").order("created_at", desc=True).limit(60).execute()
        raw_data = result.data if isinstance(result.data, list) else []
        valid = []
        for e in raw_data:
            if not isinstance(e, dict): continue
            parsed = safe_parse(e.get("extracted_data", {}))
            if not is_empty_entry(parsed):
                e["_parsed"] = parsed
                valid.append(e)
        if not valid:
            st.markdown('<div class="card" style="text-align:center;padding:2rem;"><p style="color:#999;font-family:Montserrat;font-size:0.9rem;margin:0;">No entries yet.</p></div>', unsafe_allow_html=True)
            return
        for e in valid:
            raw = e["_parsed"]
            if not isinstance(raw, dict): continue
            mood = raw.get("mood") or "Focused"
            date_str = e.get("entry_date","")
            entry_id = e.get("id")
            try:
                dt_obj = datetime.fromisoformat(date_str)
                display_date = dt_obj.strftime("%A, %d %B %Y")
            except: display_date = date_str
            mood_colors = {"excellent":"#27ae60","good":"#2ecc71","focused":"#4834d4","grateful":"#e67e22","tired":"#7f8c8d","stressed":"#e74c3c","neutral":"#95a5a6","low":"#c0392b"}
            mood_color = mood_colors.get(str(mood).lower(), "#4834d4")

            st.markdown(f"""
            <div class="history-card">
              <div class="history-header">
                <div>
                  <div style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:#d4af37;">📅 {display_date}</div>
                  <div style="font-family:'Oswald',sans-serif;font-size:0.62rem;color:rgba(255,255,255,0.5);letter-spacing:0.15em;margin-top:0.2rem;">CIPHER GHOST LOG</div>
                </div>
                <div style="background:{mood_color};color:white;border-radius:20px;padding:0.2rem 0.9rem;font-family:'Oswald',sans-serif;font-size:0.78rem;letter-spacing:0.08em;font-weight:600;">{mood}</div>
              </div>
            </div>""", unsafe_allow_html=True)

            show_key = f"show_{entry_id}"
            if show_key not in st.session_state: st.session_state[show_key] = False
            col_view, col_del = st.columns([1,1])
            with col_view:
                btn_label = "▲ Collapse" if st.session_state[show_key] else "▼ View Entry"
                if st.button(btn_label, key=f"view_{entry_id}"):
                    st.session_state[show_key] = not st.session_state[show_key]
                    st.rerun()
            with col_del:
                if st.button("🗑 Delete", key=f"del_{entry_id}"):
                    st.session_state[f"confirm_{entry_id}"] = True
            if st.session_state.get(f"confirm_{entry_id}"):
                st.warning("Delete permanently?")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("✓ Yes", key=f"yes_{entry_id}"):
                        sb.table("journal_entries").delete().eq("id", entry_id).execute()
                        st.session_state.pop(f"confirm_{entry_id}", None)
                        st.session_state.pop(show_key, None)
                        st.rerun()
                with c2:
                    if st.button("✗ Cancel", key=f"no_{entry_id}"):
                        st.session_state.pop(f"confirm_{entry_id}", None)
                        st.rerun()
            if st.session_state.get(show_key):
                try: entry_dt = datetime.fromisoformat(date_str).replace(tzinfo=EAT)
                except: entry_dt = get_eat_now()
                render_entry(raw, entry_dt)
                # PDF Download
                try:
                    pdf_bytes = generate_pdf(raw, entry_dt, e.get("raw_text",""))
                    b64 = base64.b64encode(pdf_bytes).decode()
                    fname = f"CipherGhost_{date_str}.pdf"
                    st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{fname}" style="display:inline-block;background:linear-gradient(135deg,#c0392b,#e74c3c);color:white;padding:0.5rem 1.2rem;border-radius:8px;font-family:Oswald,sans-serif;font-size:0.8rem;letter-spacing:0.1em;text-decoration:none;margin-top:0.5rem;">📤 DOWNLOAD PDF</a>', unsafe_allow_html=True)
                except Exception as pdf_err:
                    st.caption(f"PDF unavailable: {pdf_err}")
            st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)
    except Exception as ex:
        st.markdown(f'<div class="cg-error">History error: {ex}</div>', unsafe_allow_html=True)

# ── MAIN ──
def main():
    now = get_eat_now()
    sunday = is_sunday(now)
    DM = st.session_state.dark_mode

    # Hero
    st.markdown(f"""
    <div class="cg-hero">
      <h1>AUTOJOURNAL</h1>
      <div class="sub">Cipher Ghost · Personal OS</div>
      <div class="cg-date-pill">{now.strftime("%A, %d %B %Y · %H:%M EAT")}</div>
    </div>""", unsafe_allow_html=True)

    # Dark mode toggle
    col_dm = st.columns([4,1])[1]
    with col_dm:
        dm_label = "☀️ Light" if DM else "🌙 Dark"
        if st.button(dm_label, key="dm_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    # Reminder
    reminder_hour = 21
    if now.hour == reminder_hour and now.minute < 10:
        st.markdown(f'<div class="cg-success">🔔 Journal reminder — it\'s {now.strftime("%H:%M")}. Time to dump your day!</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    tab_new, tab_history, tab_stats = st.tabs(["✦ New Entry", "◈ History", "📊 Stats"])

    with tab_new:
        st.markdown("<br>", unsafe_allow_html=True)
        if sunday:
            st.markdown('<span class="sunday-badge">✦ SUNDAY — Devotion active</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;color:{"#d4af37" if DM else "#1a1a2e"};margin-bottom:0.3rem;">Dump Your Day</div>'
            f'<div style="font-family:\'Montserrat\',sans-serif;font-size:0.82rem;color:{"#a0a0c0" if DM else "#555"};margin-bottom:0.8rem;line-height:1.5;">Type or use 🎤 voice-to-text. AI builds everything — verse, prayer, meal plan, word of day.</div>',
            unsafe_allow_html=True,
        )
        user_input = st.text_area(label="j", label_visibility="collapsed",
            placeholder="e.g. Good Monday. Grateful for family, health and a clean setup on Gold. Did chart analysis — CHoCH at 2315, took long, hit TP +1.5R. Meditated 10 mins. Budget $35.",
            height=210)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡  EXTRACT & SAVE JOURNAL"):
            if not user_input.strip():
                st.markdown('<div class="cg-error">⚠ Write at least one sentence.</div>', unsafe_allow_html=True)
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

    with tab_stats:
        try:
            sb = init_supabase()
            render_stats(sb)
        except Exception as e:
            st.markdown(f'<div class="cg-error">⚠ {e}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
