import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import uuid
import re
import hashlib
from datetime import date, timedelta

# ── Config ─────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Habit Tracker",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "habit_data.json")

# ── CSS ─────────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #F7F6F3 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton,
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display: none !important; }

/* ── Top nav tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border: 1px solid #E4E4E7;
    border-radius: 14px;
    padding: 4px;
    gap: 2px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 9px 20px;
    font-size: 13.5px;
    font-weight: 500;
    color: #71717A;
    background: transparent;
    flex: 1;
    justify-content: center;
    transition: all 0.15s ease;
}
.stTabs [aria-selected="true"] {
    background: #18181B !important;
    color: #FFFFFF !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 28px !important; }

/* ── Habit cards ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #E8E8E6 !important;
    border-radius: 14px !important;
    padding: 6px 12px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.15s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8E8E6;
    border-radius: 14px;
    padding: 18px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] { font-size: 12px !important; font-weight: 500; color: #71717A !important; text-transform: uppercase; letter-spacing: 0.4px; }
[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; color: #18181B !important; letter-spacing: -0.5px; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 8px 18px !important;
    border: 1px solid #E4E4E7 !important;
    transition: all 0.15s ease !important;
    background: #FFFFFF !important;
    color: #18181B !important;
}
.stButton > button:hover {
    background: #F4F4F5 !important;
    border-color: #D4D4D8 !important;
}
.stButton > button[kind="primary"] {
    background: #18181B !important;
    color: #FFFFFF !important;
    border-color: #18181B !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3F3F46 !important;
    border-color: #3F3F46 !important;
}

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] > button {
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
}
[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: #18181B !important;
    color: white !important;
    border-color: #18181B !important;
}

/* ── Inputs ── */
input[type="text"], input[type="number"], textarea {
    border-radius: 9px !important;
    border: 1px solid #E4E4E7 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    background: #FAFAF9 !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: #18181B !important;
    box-shadow: 0 0 0 2px rgba(24,24,27,0.08) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border: 1px solid #E8E8E6 !important;
    border-radius: 14px !important;
    background: #FFFFFF !important;
    margin-bottom: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    font-size: 14px !important;
    color: #18181B !important;
    padding: 14px 18px !important;
}
[data-testid="stExpander"] summary:hover {
    background: #FAFAF9;
}

/* ── Checkboxes — large & circular ── */
/* Override Streamlit's primary color (red) → green for checkbox tick */
:root { --primary-color: #16A34A !important; }

[data-testid="stCheckbox"] { padding: 2px 0 !important; }
[data-testid="stCheckbox"] > label {
    align-items: center !important;
    gap: 16px !important;
    padding: 10px 4px !important;
    cursor: pointer !important;
    width: 100% !important;
}
/* The circle */
[data-testid="stCheckbox"] > label > div:first-child {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    border-radius: 50% !important;
    border: 2px solid #D4D4D8 !important;
    flex-shrink: 0 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
/* SVG tick inside */
[data-testid="stCheckbox"] > label > div:first-child svg {
    width: 16px !important;
    height: 16px !important;
}
/* Label text */
[data-testid="stCheckbox"] label p {
    font-size: 17px !important;
    font-weight: 600 !important;
    color: #18181B !important;
    letter-spacing: -0.2px !important;
    line-height: 1.3 !important;
    margin: 0 !important;
}

/* ── Habit progress bar (native) ── */
[data-testid="stProgressBar"] {
    margin-top: 4px !important;
    margin-left: 48px !important;
    margin-bottom: 6px !important;
}
[data-testid="stProgressBar"] > div {
    height: 6px !important;
    border-radius: 99px !important;
    background: #F0F0EE !important;
}
[data-testid="stProgressBar"] > div > div {
    height: 6px !important;
    border-radius: 99px !important;
    background: #18181B !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #18181B !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] span[data-checked="true"] {
    background: #18181B !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid #E8E8E6 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 14px !important;
}

/* ── Divider ── */
hr { border-color: #ECECEA !important; margin: 20px 0 !important; }

/* ── Captions ── */
[data-testid="stCaptionContainer"] { color: #71717A !important; font-size: 12.5px !important; }

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background: #18181B !important;
    border-radius: 99px !important;
}
[data-testid="stProgressBar"] > div {
    border-radius: 99px !important;
    background: #F0F0EE !important;
}

/* ── Page padding ── */
.block-container {
    padding-top: 24px !important;
    padding-bottom: 48px !important;
    max-width: 780px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data helpers ───────────────────────────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"habits": [], "logs": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def get_active_habits(data):
    return [h for h in data["habits"] if h.get("active", True)]

def get_logs_df(data):
    if not data["logs"]:
        return pd.DataFrame(columns=["date", "habit_id", "completed"])
    df = pd.DataFrame(data["logs"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def is_done_today(logs_df, habit_id, today):
    if logs_df.empty:
        return False
    match = logs_df[(logs_df["date"] == today) & (logs_df["habit_id"] == habit_id)]
    return False if match.empty else bool(match.iloc[0]["completed"])

def count_week_completions(logs_df, habit_id, week_start, week_end):
    if logs_df.empty:
        return 0
    mask = (
        (logs_df["habit_id"] == habit_id) &
        (logs_df["completed"] == True) &
        (logs_df["date"] >= week_start) &
        (logs_df["date"] <= week_end)
    )
    return logs_df[mask].shape[0]

def calculate_streak(logs_df, habit_id, today):
    if logs_df.empty:
        return 0
    done_dates = set(
        logs_df[
            (logs_df["habit_id"] == habit_id) &
            (logs_df["completed"] == True)
        ]["date"].tolist()
    )
    if not done_dates:
        return 0
    streak, check = 0, today
    if check not in done_dates:
        check = today - timedelta(days=1)
    while check in done_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak

def toggle_log(data, habit_id, today, new_value):
    data["logs"] = [
        l for l in data["logs"]
        if not (l["date"] == str(today) and l["habit_id"] == habit_id)
    ]
    data["logs"].append({"date": str(today), "habit_id": habit_id, "completed": new_value})
    save_data(data)

# ── Rewards helpers ────────────────────────────────────────────────────────────

def calculate_earnings(data, logs_df):
    total = 0.0
    breakdown = []
    today = date.today()
    for habit in data["habits"]:
        hid = habit["id"]
        daily_reward = float(habit.get("daily_reward", 0) or 0)
        weekly_bonus = float(habit.get("weekly_bonus", 0) or 0)
        target = habit.get("target_days", 1)
        if logs_df.empty:
            breakdown.append({"Habit": habit["name"], "Daily": 0.0, "Bonuses": 0.0, "Total": 0.0})
            continue
        completed_days = logs_df[
            (logs_df["habit_id"] == hid) & (logs_df["completed"] == True)
        ]["date"].tolist()
        daily_earned = len(completed_days) * daily_reward
        bonus_earned = 0.0
        if weekly_bonus > 0 and completed_days:
            first_day = min(completed_days)
            monday = first_day - timedelta(days=first_day.weekday())
            while monday <= today:
                week_end = monday + timedelta(days=6)
                week_count = sum(1 for d in completed_days if monday <= d <= week_end)
                if week_count >= target:
                    bonus_earned += weekly_bonus
                monday += timedelta(weeks=1)
        habit_total = daily_earned + bonus_earned
        total += habit_total
        breakdown.append({
            "Habit": habit["name"],
            "Daily": round(daily_earned, 2),
            "Bonuses": round(bonus_earned, 2),
            "Total": round(habit_total, 2)
        })
    return round(total, 2), breakdown

# ── Initiation panel ───────────────────────────────────────────────────────────

def render_text_with_links(text):
    """Convert bare URLs to markdown links and preserve line breaks."""
    url_pattern = r'(https?://[^\s]+)'
    linked = re.sub(url_pattern, r'[\1](\1)', text)
    return linked.replace('\n', '  \n')

def show_initiation_panel(habit):
    text = habit.get("initiation_text", "").strip()
    if not text:
        return
    with st.expander(f"📖  {habit['name']}", expanded=True):
        st.markdown(render_text_with_links(text))

# ── UI helpers ─────────────────────────────────────────────────────────────────

def done_card_html(name, week_count, target, streak):
    """Green card rendered as HTML for completed habits (outside bordered container)."""
    week_pct = min(week_count / target * 100, 100) if target > 0 else 0
    streak_html = f"<span style='font-size:12px;color:#16A34A;font-weight:500;margin-left:6px;'>🔥 {streak} day streak</span>" if streak >= 2 else ""
    return f"""
<div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:16px;padding:18px 22px 16px;margin-bottom:4px;box-shadow:0 1px 4px rgba(22,163,74,0.07);">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">
        <div style="width:32px;height:32px;background:#16A34A;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 2px 6px rgba(22,163,74,0.3);">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <path d="M2.5 7.5L6 11L12.5 4" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div>
            <span style="font-size:18px;font-weight:600;color:#14532D;letter-spacing:-0.3px;">{name}</span>{streak_html}
        </div>
    </div>
    <div style="margin-left:46px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:12px;color:#4ADE80;font-weight:500;">{week_count} of {target} days this week</span>
            {'<span style="font-size:12px;color:#16A34A;font-weight:600;">Week complete ✓</span>' if week_pct >= 100 else ''}
        </div>
        <div style="background:#DCFCE7;border-radius:99px;height:6px;overflow:hidden;">
            <div style="background:#16A34A;height:100%;width:{week_pct:.0f}%;border-radius:99px;"></div>
        </div>
    </div>
</div>
"""

# ── Page: Today ────────────────────────────────────────────────────────────────

def page_today(data):
    today = date.today()

    # Header
    st.markdown(f"""
<div style="margin-bottom:28px;">
    <p style="font-size:11px;font-weight:600;color:#A1A1AA;margin:0;letter-spacing:1px;text-transform:uppercase;">{today.strftime('%A')}</p>
    <h1 style="font-size:30px;font-weight:700;color:#18181B;margin:4px 0 0;letter-spacing:-0.8px;">{today.strftime('%B %d, %Y')}</h1>
</div>
""", unsafe_allow_html=True)

    habits = get_active_habits(data)
    if not habits:
        st.info("No habits yet. Head to Habits to add your first one.")
        return

    logs_df = get_logs_df(data)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    done_count = sum(1 for h in habits if is_done_today(logs_df, h["id"], today))
    total_count = len(habits)
    pct = int(done_count / total_count * 100)
    fill_color = "#16A34A" if pct == 100 else "#18181B"

    # Summary card with progress bar
    st.markdown(f"""
<div style="background:white;border:1px solid #E8E8E6;border-radius:18px;padding:22px 26px 20px;margin-bottom:28px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:16px;">
        <div>
            <p style="font-size:11px;font-weight:600;color:#A1A1AA;margin:0;letter-spacing:1px;text-transform:uppercase;">Today's progress</p>
            <p style="font-size:24px;font-weight:700;color:#18181B;margin:5px 0 0;letter-spacing:-0.6px;">
                {done_count} <span style="color:#A1A1AA;font-weight:400;">of</span> {total_count} habits
            </p>
        </div>
        <div style="font-size:32px;font-weight:700;color:{fill_color};letter-spacing:-1.5px;line-height:1;">{pct}%</div>
    </div>
    <div style="background:#F0F0EE;border-radius:99px;height:8px;overflow:hidden;">
        <div style="background:{fill_color};height:100%;width:{pct}%;border-radius:99px;transition:width 0.4s ease;min-width:{'8px' if pct > 0 else '0'};"></div>
    </div>
    {'<p style="font-size:13px;color:#16A34A;font-weight:500;margin:10px 0 0;">All done for today. Good work.</p>' if pct == 100 else ''}
</div>
""", unsafe_allow_html=True)

    # Habit cards
    for habit in habits:
        hid = habit["id"]
        target = habit["target_days"]
        done = is_done_today(logs_df, hid, today)
        week_count = count_week_completions(logs_df, hid, week_start, week_end)
        streak = calculate_streak(logs_df, hid, today)

        label = habit["name"] + (f"  🔥 {streak}" if streak >= 2 else "")
        pct = int(min(week_count / target, 1.0) * 100) if target > 0 else 0

        with st.container(border=True):
            new_val = st.checkbox(label, value=done, key=f"today_{hid}")
            st.markdown(f"""
<div style="margin-top:2px;margin-bottom:4px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-size:12px;color:#A1A1AA;font-weight:500;letter-spacing:0.3px;">{week_count} of {target} days this week</span>
        <span style="font-size:12px;color:#16A34A;font-weight:600;">{pct}%</span>
    </div>
    <div style="background:#F0F0EE;border-radius:99px;height:5px;width:100%;overflow:hidden;">
        <div style="background:#16A34A;border-radius:99px;height:5px;width:{pct}%;transition:width 0.4s ease;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

        if new_val != done:
            toggle_log(data, hid, today, new_val)
            st.rerun()

        if new_val and habit.get("has_initiation") and habit.get("initiation_text", "").strip():
            show_initiation_panel(habit)

# ── Page: Manage Habits ────────────────────────────────────────────────────────

def page_manage(data):
    st.markdown("<h1 style='margin-bottom:24px;'>Habits</h1>", unsafe_allow_html=True)

    with st.expander("＋  Add New Habit", expanded=len(data["habits"]) == 0):
        with st.form("add_habit_form", clear_on_submit=True):
            name = st.text_input("Habit name", placeholder="e.g. Read the news")
            target = st.slider("Days per week", min_value=1, max_value=7, value=5)

            st.divider()
            st.markdown("**Rewards** *(optional)*")
            col_a, col_b = st.columns(2)
            with col_a:
                daily_reward = st.number_input("£ per day completed", min_value=0.0, value=0.0, step=0.5)
            with col_b:
                weekly_bonus = st.number_input("£ bonus for full week", min_value=0.0, value=0.0, step=0.5)

            st.divider()
            st.markdown("**Initiation** *(optional)*")
            st.caption("Shows links and a Claude prompt when you check this habit.")
            has_initiation = st.toggle("Show initiation panel on check")
            initiation_text = st.text_area(
                "What do you want to see?",
                placeholder="e.g. News from the past 48 hours: Taiwan, US politics, financial markets",
                height=90
            )

            submitted = st.form_submit_button("Add Habit", type="primary")
            if submitted:
                if not name.strip():
                    st.error("Please enter a habit name.")
                else:
                    data["habits"].append({
                        "id": str(uuid.uuid4())[:8],
                        "name": name.strip(),
                        "target_days": target,
                        "active": True,
                        "created_at": str(date.today()),
                        "daily_reward": daily_reward,
                        "weekly_bonus": weekly_bonus,
                        "has_initiation": has_initiation,
                        "initiation_text": initiation_text.strip() if has_initiation else ""
                    })
                    save_data(data)
                    st.success(f"Added **{name}**!")
                    st.rerun()

    active_habits = [h for h in data["habits"] if h.get("active", True)]
    archived_habits = [h for h in data["habits"] if not h.get("active", True)]

    if active_habits:
        st.markdown("<h2 style='margin:24px 0 12px;'>Your Habits</h2>", unsafe_allow_html=True)
        for habit in active_habits:
            init_tag = "  (has initiation)" if habit.get("has_initiation") else ""
            with st.expander(f"{habit['name']}  {habit['target_days']}x/week{init_tag}"):
                with st.form(f"edit_{habit['id']}"):
                    new_name = st.text_input("Name", value=habit["name"])
                    new_target = st.slider("Days per week", 1, 7, habit["target_days"])

                    st.divider()
                    st.markdown("**Rewards**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        new_daily = st.number_input("£ per day", min_value=0.0,
                            value=float(habit.get("daily_reward", 0) or 0), step=0.5)
                    with col_b:
                        new_bonus = st.number_input("£ weekly bonus", min_value=0.0,
                            value=float(habit.get("weekly_bonus", 0) or 0), step=0.5)

                    st.divider()
                    st.markdown("**Initiation**")
                    new_has_init = st.toggle("Show initiation panel on check",
                                             value=habit.get("has_initiation", False))
                    new_init_text = st.text_area("What do you want to see?",
                                                  value=habit.get("initiation_text", ""),
                                                  height=90)

                    col1, col2 = st.columns(2)
                    with col1:
                        save_btn = st.form_submit_button("Save", type="primary")
                    with col2:
                        archive_btn = st.form_submit_button("Archive")

                    if save_btn:
                        for h in data["habits"]:
                            if h["id"] == habit["id"]:
                                h.update({
                                    "name": new_name.strip(),
                                    "target_days": new_target,
                                    "daily_reward": new_daily,
                                    "weekly_bonus": new_bonus,
                                    "has_initiation": new_has_init,
                                    "initiation_text": new_init_text.strip() if new_has_init else ""
                                })
                        save_data(data)
                        st.success("Saved!")
                        st.rerun()

                    if archive_btn:
                        for h in data["habits"]:
                            if h["id"] == habit["id"]:
                                h["active"] = False
                        save_data(data)
                        st.rerun()
    else:
        st.info("No habits yet. Add your first one above.")

    if archived_habits:
        with st.expander(f"Archived  ({len(archived_habits)})"):
            for habit in archived_habits:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"**{habit['name']}**")
                with col2:
                    if st.button("Restore", key=f"restore_{habit['id']}"):
                        for h in data["habits"]:
                            if h["id"] == habit["id"]:
                                h["active"] = True
                        save_data(data)
                        st.rerun()

# ── Page: Progress ─────────────────────────────────────────────────────────────

def page_progress(data):
    st.markdown("<h1 style='margin-bottom:24px;'>Progress</h1>", unsafe_allow_html=True)

    habits = get_active_habits(data)
    if not habits:
        st.info("Nothing to track yet. Add some habits first and your progress will show up here.")
        return

    logs_df = get_logs_df(data)
    today = date.today()

    # ── Streaks (always visible, above tabs) ──
    st.markdown("<h2 style='margin:0 0 12px;'>Streaks</h2>", unsafe_allow_html=True)
    streak_cols = st.columns(len(habits))
    for i, habit in enumerate(habits):
        streak = calculate_streak(logs_df, habit["id"], today)
        with streak_cols[i]:
            st.metric(habit["name"], f"🔥 {streak}" if streak >= 1 else "Not started")

    st.divider()

    tab_daily, tab_weekly, tab_monthly, tab_edit = st.tabs(["  7 Days  ", "  Weekly  ", "  Monthly  ", "  Edit Past  "])

    CHART_COLORS = ["#18181B", "#52525B", "#A1A1AA", "#D4D4D8", "#F4F4F5"]

    with tab_daily:
        last7 = [today - timedelta(days=i) for i in range(6, -1, -1)]
        rows = []
        for d in last7:
            row = {"Date": d.strftime("%a %d")}
            for habit in habits:
                done = (not logs_df.empty and
                        logs_df[(logs_df["date"] == d) & (logs_df["habit_id"] == habit["id"]) &
                                (logs_df["completed"] == True)].shape[0] > 0)
                row[habit["name"]] = "✓" if done else "·"
            rows.append(row)

        st.dataframe(pd.DataFrame(rows).set_index("Date"), use_container_width=True, height=280)

        st.markdown("<h2 style='margin:24px 0 12px;'>Completion rate</h2>", unsafe_allow_html=True)
        chart_data = []
        for habit in habits:
            count = 0 if logs_df.empty else logs_df[
                (logs_df["habit_id"] == habit["id"]) & (logs_df["completed"] == True) &
                (logs_df["date"].isin(last7))].shape[0]
            chart_data.append({"Habit": habit["name"], "Days": count, "Pct": round(count / 7 * 100)})
        fig = px.bar(pd.DataFrame(chart_data), x="Habit", y="Days",
                     color_discrete_sequence=["#18181B"], text="Days")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          font_family="Inter", showlegend=False,
                          margin=dict(l=0, r=0, t=20, b=0),
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F4F4F5"))
        fig.update_traces(textposition="outside", marker_line_width=0, width=0.5)
        st.plotly_chart(fig, use_container_width=True)

    with tab_weekly:
        week_data = []
        week_labels_ordered = []  # keep track of label order
        for w in range(7, -1, -1):
            wk_start = today - timedelta(days=today.weekday()) - timedelta(weeks=w)
            wk_end = wk_start + timedelta(days=6)
            label = wk_start.strftime("%b %d")
            if label not in week_labels_ordered:
                week_labels_ordered.append(label)
            for habit in habits:
                count = count_week_completions(logs_df, habit["id"], wk_start, wk_end)
                pct = round(min(count / habit["target_days"] * 100, 100), 1) if habit["target_days"] > 0 else 0
                week_data.append({
                    "Week": label,
                    "Habit": habit["name"],
                    "Days": count,
                    "Target": habit["target_days"],
                    "Pct": pct
                })
        week_df = pd.DataFrame(week_data)
        # Enforce chronological order on the x-axis
        week_df["Week"] = pd.Categorical(week_df["Week"], categories=week_labels_ordered, ordered=True)
        week_df = week_df.sort_values("Week")

        fig2 = px.line(week_df, x="Week", y="Pct", color="Habit", markers=True,
                       color_discrete_sequence=CHART_COLORS, range_y=[0, 115],
                       category_orders={"Week": week_labels_ordered})
        fig2.add_hline(y=100, line_dash="dot", line_color="#D4D4D8", annotation_text="target")
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", y=-0.2),
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="#F4F4F5", title="% of weekly target")
        )
        st.plotly_chart(fig2, use_container_width=True)

        this_week_label = week_labels_ordered[-1]
        latest = week_df[week_df["Week"] == this_week_label][["Habit", "Days", "Target", "Pct"]].set_index("Habit")
        latest.columns = ["Days Done", "Target", "% of Target"]
        st.markdown("<h2 style='margin:24px 0 12px;'>This week</h2>", unsafe_allow_html=True)
        st.dataframe(latest, use_container_width=True)

    with tab_monthly:
        month_start = today.replace(day=1)
        days_elapsed = (today - month_start).days + 1
        month_dates = [month_start + timedelta(days=i) for i in range(days_elapsed)]
        st.markdown(f"<p style='color:#71717A;font-size:13px;'>{today.strftime('%B %Y')} · {days_elapsed} days in</p>", unsafe_allow_html=True)

        for habit in habits:
            count = 0 if logs_df.empty else logs_df[
                (logs_df["habit_id"] == habit["id"]) & (logs_df["completed"] == True) &
                (logs_df["date"].isin(month_dates))].shape[0]
            expected = round(habit["target_days"] * days_elapsed / 7)
            pct = round(count / max(expected, 1) * 100)
            streak = calculate_streak(logs_df, habit["id"], today)

            st.markdown(f"<h3 style='margin:20px 0 12px;'>{habit['name']}</h3>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Done", count)
            c2.metric("Expected", expected)
            c3.metric("On track", f"{pct}%",
                      delta="ahead" if pct >= 100 else "behind",
                      delta_color="normal" if pct >= 100 else "inverse")
            c4.metric("Streak", f"🔥 {streak}" if streak else "Not started")
            st.divider()

    with tab_edit:
        st.markdown("<p style='color:#71717A;font-size:13px;margin-bottom:16px;'>Pick any past date to view or correct your habit logs.</p>", unsafe_allow_html=True)

        selected_date = st.date_input(
            "Select date",
            value=today - timedelta(days=1),
            max_value=today,
            format="DD/MM/YYYY"
        )

        if selected_date:
            st.markdown(f"<h3 style='margin:20px 0 12px;'>{selected_date.strftime('%A, %B %d %Y')}</h3>", unsafe_allow_html=True)

            changed = False
            for habit in habits:
                hid = habit["id"]
                current = is_done_today(logs_df, hid, selected_date)
                new_val = st.checkbox(
                    habit["name"],
                    value=current,
                    key=f"edit_{hid}_{selected_date}"
                )
                if new_val != current:
                    toggle_log(data, hid, selected_date, new_val)
                    changed = True

            if changed:
                st.success("Updated!")
                st.rerun()

# ── Page: Rewards ──────────────────────────────────────────────────────────────

def page_rewards(data):
    st.markdown("<h1 style='margin-bottom:8px;'>Rewards</h1>", unsafe_allow_html=True)
    st.markdown("""<p style='color:#71717A;font-size:14px;margin-bottom:28px;'>
        Every habit you complete earns you symbolic money based on the rates you set.
        Add items to your wishlist, assign what % of your balance goes toward each one,
        and watch your savings grow as a mental reminder of the extras consistency can buy you.
    </p>""", unsafe_allow_html=True)

    logs_df = get_logs_df(data)
    total, breakdown = calculate_earnings(data, logs_df)
    today = date.today()
    reward_habits = [h for h in data["habits"] if float(h.get("daily_reward", 0) or 0) > 0 or float(h.get("weekly_bonus", 0) or 0) > 0]

    if not reward_habits:
        st.info("No reward rates set yet. Edit a habit in **Habits** to add £/day or a weekly bonus.")
        return

    # Ensure wishlist exists
    if "wishlist" not in data:
        data["wishlist"] = []

    # ── Balance card ──
    allocated_total = sum(
        total * float(item.get("allocation_pct", 0)) / 100
        for item in data["wishlist"]
    )
    unallocated = max(0.0, total - allocated_total)

    st.markdown(f"""
<div style="background:#18181B;border-radius:16px;padding:28px 32px;margin-bottom:20px;">
    <p style="font-size:11px;font-weight:600;color:#71717A;margin:0;letter-spacing:1px;text-transform:uppercase;">Total balance</p>
    <p style="font-size:44px;font-weight:700;color:#FFFFFF;margin:6px 0 0;letter-spacing:-1.5px;">£{total:,.2f}</p>
    <p style="font-size:13px;color:#52525B;margin:8px 0 0;">
        £{allocated_total:,.2f} allocated to wishlist &nbsp;·&nbsp; £{unallocated:,.2f} unallocated
    </p>
</div>
""", unsafe_allow_html=True)

    # ── Wishlist ──
    st.markdown("<h2 style='margin:28px 0 4px;'>Wishlist</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A1A1AA;font-size:12.5px;margin-bottom:16px;'>Add what you want to save up for. Assign a % of your balance to each item and see how close you are.</p>", unsafe_allow_html=True)

    # Add item form
    with st.expander("＋  Add to Wishlist", expanded=len(data["wishlist"]) == 0):
        with st.form("add_wishlist_item", clear_on_submit=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                item_name = st.text_input("Item", placeholder="e.g. Gold earrings")
            with col2:
                item_price = st.number_input("Price (£)", min_value=0.0, value=50.0, step=10.0)
            with col3:
                item_pct = st.number_input("% of balance", min_value=0, max_value=100, value=20, step=5)
            add_btn = st.form_submit_button("Add Item", type="primary")
            if add_btn and item_name.strip():
                data["wishlist"].append({
                    "id": str(uuid.uuid4())[:8],
                    "name": item_name.strip(),
                    "price": item_price,
                    "allocation_pct": item_pct
                })
                save_data(data)
                st.rerun()

    # Wishlist items
    if data["wishlist"]:
        total_allocated_pct = sum(float(i.get("allocation_pct", 0)) for i in data["wishlist"])
        if total_allocated_pct > 100:
            st.warning(f"Your allocations add up to {total_allocated_pct:.0f}%, which is over 100%. Consider reducing some.")

        for item in data["wishlist"]:
            iid = item["id"]
            price = float(item.get("price", 0))
            pct = float(item.get("allocation_pct", 0))
            saved = total * pct / 100
            progress = min(saved / price, 1.0) if price > 0 else 0
            progress_pct = int(progress * 100)
            can_buy = saved >= price

            with st.container(border=True):
                col1, col2 = st.columns([5, 2])
                with col1:
                    badge = " <span style='background:#F0FDF4;color:#16A34A;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;'>Can buy! ✓</span>" if can_buy else ""
                    st.markdown(f"**{item['name']}**{badge}", unsafe_allow_html=True)
                    st.markdown(f"""
<div style="margin-top:8px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
        <span style="font-size:12px;color:#A1A1AA;">£{saved:,.2f} saved of £{price:,.2f}</span>
        <span style="font-size:12px;color:#16A34A;font-weight:600;">{progress_pct}%</span>
    </div>
    <div style="background:#F0F0EE;border-radius:99px;height:5px;width:100%;overflow:hidden;">
        <div style="background:#16A34A;border-radius:99px;height:5px;width:{progress_pct}%;"></div>
    </div>
    <p style="font-size:11px;color:#A1A1AA;margin:5px 0 0;">{pct:.0f}% of your balance allocated</p>
</div>
""", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    new_pct = st.number_input("% allocation", min_value=0, max_value=100, step=5,
                                               value=int(pct), key=f"pct_{iid}", label_visibility="collapsed")
                    if new_pct != int(pct):
                        for wi in data["wishlist"]:
                            if wi["id"] == iid:
                                wi["allocation_pct"] = new_pct
                        save_data(data)
                        st.rerun()
                    if st.button("Remove", key=f"del_{iid}"):
                        data["wishlist"] = [wi for wi in data["wishlist"] if wi["id"] != iid]
                        save_data(data)
                        st.rerun()
    else:
        st.markdown("<p style='color:#A1A1AA;font-size:13px;padding:12px 0;'>No items yet. Add something you are saving up for.</p>", unsafe_allow_html=True)

    # ── Earnings breakdown (collapsed) ──
    with st.expander("Earnings breakdown by habit"):
        df = pd.DataFrame(breakdown)
        df = df[df["Total"] > 0]
        if not df.empty:
            df_display = df.copy()
            for col in ["Daily", "Bonuses", "Total"]:
                df_display[col] = df_display[col].apply(lambda x: f"£{x:,.2f}")
            st.dataframe(df_display.set_index("Habit"), use_container_width=True)
        else:
            st.caption("Start checking habits to accumulate earnings.")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    inject_css()

    data = load_data()

    # App wordmark + balance chip
    logs_df = get_logs_df(data)
    total_balance, _ = calculate_earnings(data, logs_df)
    balance_chip = f" &nbsp; <span style='background:#F0FDF4;border:1px solid #BBF7D0;color:#15803D;border-radius:20px;padding:2px 12px;font-size:12px;font-weight:600;'>£{total_balance:,.2f}</span>" if total_balance > 0 else ""

    st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
    <span style="font-size:16px;font-weight:700;color:#18181B;letter-spacing:-0.3px;">✦ Habit Tracker</span>
    <span>{balance_chip}</span>
</div>
""", unsafe_allow_html=True)

    has_habits = bool(get_active_habits(data))

    if has_habits:
        tab_today, tab_habits, tab_progress, tab_rewards = st.tabs([
            "  Today  ", "  Habits  ", "  Progress  ", "  Rewards  "
        ])
        with tab_today:
            page_today(data)
        with tab_habits:
            page_manage(data)
        with tab_progress:
            page_progress(data)
        with tab_rewards:
            page_rewards(data)
    else:
        tab_habits, tab_today, tab_progress, tab_rewards = st.tabs([
            "  Habits  ", "  Today  ", "  Progress  ", "  Rewards  "
        ])
        with tab_habits:
            page_manage(data)
        with tab_today:
            page_today(data)
        with tab_progress:
            page_progress(data)
        with tab_rewards:
            page_rewards(data)

if __name__ == "__main__":
    main()
