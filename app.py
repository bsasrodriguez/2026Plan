"""
Sal Rodriguez — Coaching Dashboard
Open Source · Python + SQLite + Streamlit
Run locally:  pip install streamlit pandas plotly && streamlit run app.py
Deploy free:  streamlit.io/cloud (sign in with Gmail, connect GitHub)
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sal Rodriguez — Coaching Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "coaching.db"

# ── COLORS ────────────────────────────────────────────────────────────────────
TEAL    = "#0F6E56"
BLUE    = "#1B4F8A"
AMBER   = "#854F0B"
GREEN   = "#3B6D11"
PURPLE  = "#534AB7"
RED     = "#A32D2D"
NAVY    = "#1B3A6B"

# ── DATABASE SETUP ────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS tbl_WeeklyCheckin (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        week_of         DATE    NOT NULL UNIQUE,
        week_number     INTEGER,
        cpa_hours       REAL    DEFAULT 0,
        exam_locked     TEXT    DEFAULT 'No',
        tuesday_class   TEXT    DEFAULT 'No',
        budget_ok       TEXT    DEFAULT 'No',
        new_debt        TEXT    DEFAULT 'No',
        debt_payment    REAL    DEFAULT 0,
        cardio          INTEGER DEFAULT 0,
        drinks          INTEGER DEFAULT 0,
        weight_lbs      REAL,
        dfe_night       TEXT    DEFAULT 'No',
        vented          TEXT    DEFAULT 'No',
        energy          INTEGER DEFAULT 5,
        one_win         TEXT,
        one_diff        TEXT,
        score           REAL,
        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tbl_CPAExams (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_number     INTEGER NOT NULL,
        section         TEXT,
        target_date     DATE,
        actual_date     DATE,
        score           INTEGER,
        pass_fail       TEXT    DEFAULT 'Pending',
        status          TEXT    DEFAULT 'Not Started',
        study_hours     REAL    DEFAULT 0,
        attempt         INTEGER DEFAULT 1,
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS tbl_StudyLog (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        study_date      DATE NOT NULL,
        exam_id         INTEGER REFERENCES tbl_CPAExams(id),
        topic           TEXT,
        minutes         INTEGER DEFAULT 0,
        study_type      TEXT,
        q_attempted     INTEGER DEFAULT 0,
        q_correct       INTEGER DEFAULT 0,
        confidence      INTEGER DEFAULT 5,
        notes           TEXT,
        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tbl_HealthLog (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        week_of         DATE NOT NULL UNIQUE,
        weight_lbs      REAL,
        target_lbs      REAL DEFAULT 271,
        cardio          INTEGER DEFAULT 0,
        cardio_mins     INTEGER DEFAULT 0,
        drinks          INTEGER DEFAULT 0,
        sleep_hrs       REAL,
        energy          INTEGER DEFAULT 5,
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS tbl_FinanceLog (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        month_year      TEXT NOT NULL UNIQUE,
        month_label     TEXT,
        total_debt      REAL,
        debt_paid       REAL DEFAULT 0,
        emergency_fund  REAL DEFAULT 0,
        budget          REAL,
        actual_spend    REAL,
        new_debt        REAL DEFAULT 0,
        notes           TEXT,
        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tbl_Milestones (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        category        TEXT,
        title           TEXT NOT NULL,
        target_date     DATE,
        completed_date  DATE,
        status          TEXT DEFAULT 'Pending',
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS tbl_DailyLog (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date        DATE NOT NULL UNIQUE,
        cpa_studied     INTEGER DEFAULT -1,
        cpa_mins        INTEGER DEFAULT 0,
        cardio          INTEGER DEFAULT -1,
        drinks          INTEGER DEFAULT 0,
        weight_lbs      REAL,
        present         INTEGER DEFAULT -1,
        no_venting      INTEGER DEFAULT -1,
        budget_ok       INTEGER DEFAULT -1,
        sleep_hrs       REAL,
        morning_routine INTEGER DEFAULT -1,
        mit_done        INTEGER DEFAULT -1,
        mit_text        TEXT,
        win_of_day      TEXT,
        mood_note       TEXT,
        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed CPA exams if empty
    if cur.execute("SELECT COUNT(*) FROM tbl_CPAExams").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO tbl_CPAExams (exam_number,section,target_date,status) VALUES (?,?,?,?)",
            [
                (1, "FAR — Financial Accounting & Reporting", "2026-05-31", "Studying"),
                (2, "AUD — Auditing & Attestation",           "2026-06-30", "Not Started"),
                (3, "REG — Regulation",                       "2026-11-30", "Not Started"),
                (4, "BEC or TCP",                             "2027-02-28", "Not Started"),
            ]
        )

    # Seed milestones if empty
    if cur.execute("SELECT COUNT(*) FROM tbl_Milestones").fetchone()[0] == 0:
        milestones = [
            ("Finance",      "Budget built and first month executed",               "2026-04-30"),
            ("Health",       "Cardio habit: 3x/week for 4 consecutive weeks",       "2026-05-15"),
            ("CPA",          "CPA Exam 1 — PASSED",                                 "2026-05-31"),
            ("CPA",          "CPA Exam 2 — PASSED",                                 "2026-06-30"),
            ("Work",         "Work strategic decision made in writing",              "2026-06-30"),
            ("Health",       "Weight: 280 lbs",                                     "2026-06-30"),
            ("Finance",      "$2,000 emergency fund built",                         "2026-09-30"),
            ("Health",       "Alcohol consistently max 2 drinks/week for 3 months", "2026-09-30"),
            ("Health",       "Weight: 271 lbs — 20 lb goal ACHIEVED",              "2026-09-30"),
            ("CPA",          "CPA Exam 3 — PASSED",                                 "2026-11-30"),
            ("Law School",   "Talked to 2 JD/CPA professionals",                   "2026-12-31"),
            ("Finance",      "$4,000 net debt reduction",                           "2026-12-31"),
            ("CPA",          "CPA Exam 4 — PASSED — ALL 4 COMPLETE",               "2027-02-28"),
            ("Relationship", "6-month device-free evening streak",                  "2027-03-31"),
            ("Finance",      "$6,000 net debt reduction",                           "2027-03-31"),
            ("Law School",   "Law school research complete — financial case built", "2027-06-30"),
            ("Law School",   "Decision gate: Apply to law school?",                 "2027-09-30"),
        ]
        cur.executemany(
            "INSERT INTO tbl_Milestones (category,title,target_date) VALUES (?,?,?)",
            milestones
        )

    conn.commit()
    conn.close()

def calc_score(d):
    s = 0
    s += min(d.get("cpa_hours", 0) / 5, 1) * 25
    s += 10 if d.get("budget_ok") == "Yes" else 0
    s += 5  if d.get("new_debt")  == "No"  else 0
    s += min(d.get("cardio", 0) / 3, 1) * 15
    s += 10 if d.get("drinks", 99) <= 2 else 0
    s += 10 if d.get("dfe_night") == "Yes" else 0
    s += 10 if d.get("vented")    == "No"  else 0
    s += (d.get("energy", 5) / 10) * 15
    return round(s, 1)

# ── SIDEBAR NAV ───────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='background:{NAVY};padding:16px;border-radius:8px;margin-bottom:16px'>
            <div style='color:white;font-size:18px;font-weight:600'>🎯 Sal Rodriguez</div>
            <div style='color:#9FDFCB;font-size:12px;margin-top:4px'>18-Month Coaching Plan</div>
            <div style='color:#7799BB;font-size:11px'>Mar 2026 – Sep 2027</div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["📊 Dashboard", "✅ Weekly Check-In", "📅 Daily Log",
             "📚 CPA Tracker", "💰 Finance", "⚖️ Health",
             "🏆 Milestones", "📈 Reports & Charts"],
            label_visibility="collapsed"
        )

        st.divider()
        st.caption("**Database:** coaching.db (local SQLite)")
        st.caption("**Built with:** Python · Streamlit · Plotly")
        st.caption("Deploy free → streamlit.io/cloud")
    return page

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
def page_dashboard(conn):
    st.title("📊 Command Center")

    # KPIs
    exams = pd.read_sql("SELECT * FROM tbl_CPAExams ORDER BY exam_number", conn)
    passed = len(exams[exams["pass_fail"] == "PASS"])
    checkins = pd.read_sql("SELECT * FROM tbl_WeeklyCheckin ORDER BY week_of DESC", conn)
    health = pd.read_sql("SELECT * FROM tbl_HealthLog ORDER BY week_of DESC LIMIT 1", conn)
    finance = pd.read_sql("SELECT SUM(debt_paid) as total FROM tbl_FinanceLog", conn)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📚 CPA Exams Passed", f"{passed} / 4",
                  delta="Keep studying" if passed < 4 else "DONE! 🎉")
    with c2:
        total_paid = finance["total"].iloc[0] or 0
        st.metric("💰 Debt Reduced", f"${total_paid:,.0f}",
                  delta=f"${6000-total_paid:,.0f} to $6k goal")
    with c3:
        w = health["weight_lbs"].iloc[0] if len(health) else 291
        st.metric("⚖️ Weight", f"{w} lbs",
                  delta=f"{w-271:.1f} lbs to 271 goal",
                  delta_color="inverse")
    with c4:
        st.metric("🔥 Check-Ins Logged", len(checkins),
                  delta="Sunday ritual" if len(checkins) else "Start this Sunday!")

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("5 Priority Goals")
        goals = [
            ("P1 — CPA Exams",         TEAL,   max(passed/4*100, 3)),
            ("P2 — Financial",          BLUE,   min(total_paid/6000*100, 100)),
            ("P3 — Health",             GREEN,  min((311-float(w))/40*100, 100) if w else 5),
            ("P4 — Relationship",       PURPLE, 0),
            ("P5 — Work Decision",      AMBER,  0),
        ]
        for title, color, pct in goals:
            st.markdown(f"**{title}** — {pct:.0f}%")
            st.progress(pct / 100)

    with col2:
        st.subheader("Next Milestones")
        ms = pd.read_sql(
            "SELECT category, title, target_date FROM tbl_Milestones "
            "WHERE status='Pending' ORDER BY target_date LIMIT 5", conn
        )
        for _, row in ms.iterrows():
            st.markdown(f"🔲 `{row['target_date']}` {row['title'][:45]}")

    st.divider()
    st.subheader("CPA Exam Status")
    cols = st.columns(4)
    for i, (_, exam) in enumerate(exams.iterrows()):
        color = TEAL if exam["pass_fail"] == "PASS" else (BLUE if exam["status"] == "Studying" else "#888")
        cols[i].markdown(f"""
        <div style='background:{color}22;border:1px solid {color};border-radius:8px;padding:12px;text-align:center'>
            <div style='font-size:11px;color:{color};font-weight:600'>EXAM {exam['exam_number']}</div>
            <div style='font-size:13px;font-weight:500;margin:4px 0'>{exam['section'].split('—')[0].strip()}</div>
            <div style='font-size:11px;color:#888'>{exam['status']}</div>
            <div style='font-size:10px;color:#aaa'>Target: {exam['target_date']}</div>
        </div>
        """, unsafe_allow_html=True)

    if len(checkins):
        st.divider()
        st.subheader("Latest Weekly Check-In")
        latest = checkins.iloc[0]
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("CPA Study", f"{latest['cpa_hours']}h", "✅" if latest['cpa_hours']>=5 else "⚠️")
        c2.metric("Cardio",    f"{latest['cardio']}/3",   "✅" if latest['cardio']>=3 else "⚠️")
        c3.metric("Drinks",    latest['drinks'],           "✅" if latest['drinks']<=2 else "🔴")
        c4.metric("Weight",    f"{latest['weight_lbs']} lbs" if latest['weight_lbs'] else "—")
        c5.metric("Energy",    f"{latest['energy']}/10")
        c6.metric("Score",     f"{latest['score']}%")

# ── WEEKLY CHECK-IN ───────────────────────────────────────────────────────────
def page_weekly_checkin(conn):
    st.title("✅ Weekly Check-In")
    st.info("Complete every Sunday evening. 20 minutes. This is non-negotiable.")

    with st.form("weekly_form"):
        c1, c2, c3 = st.columns(3)
        week_of     = c1.date_input("Week of (Sunday)", value=date.today())
        week_num    = c2.number_input("Week number", min_value=1, max_value=78, value=1)
        energy      = c3.slider("Overall energy (1–10)", 1, 10, 5)

        st.markdown(f"#### 📚 CPA — Priority 1")
        c1, c2, c3 = st.columns(3)
        cpa_hours   = c1.number_input("Study hours this week", 0.0, 40.0, 0.0, 0.5)
        exam_locked = c2.selectbox("Exam date locked?", ["No", "Yes"])
        tue_class   = c3.selectbox("Tuesday class attended?", ["No", "Yes", "N/A"])

        st.markdown(f"#### 💰 Finance — Priority 2")
        c1, c2, c3 = st.columns(3)
        budget_ok  = c1.selectbox("Budget on track?", ["No", "Yes"])
        new_debt   = c2.selectbox("New debt taken on?", ["No", "Yes"])
        debt_pay   = c3.number_input("Debt payment made ($)", 0.0, 10000.0, 0.0, 50.0)

        st.markdown(f"#### ⚖️ Health — Priority 3")
        c1, c2, c3 = st.columns(3)
        cardio     = c1.number_input("Cardio sessions (target: 3)", 0, 7, 0)
        drinks     = c2.number_input("Drinks this week (max: 2)", 0, 50, 0)
        weight     = c3.number_input("Weight this Sunday (lbs)", 150.0, 400.0, 291.0, 0.1)

        st.markdown(f"#### ❤️ Relationship — Priority 4")
        c1, c2 = st.columns(2)
        dfe    = c1.selectbox("Device-free evening happened?", ["No", "Yes"])
        vented = c2.selectbox("Vented about boss to partner?", ["Yes", "No"])

        st.markdown("#### Reflection")
        win  = st.text_area("One win from this week")
        diff = st.text_area("One thing to do differently next week")

        submitted = st.form_submit_button("💾 Save Check-In", type="primary")

    if submitted:
        d = dict(cpa_hours=cpa_hours, budget_ok=budget_ok, new_debt=new_debt,
                 cardio=cardio, drinks=drinks, dfe_night=dfe, vented=vented, energy=energy)
        score = calc_score(d)
        try:
            conn.execute("""
                INSERT OR REPLACE INTO tbl_WeeklyCheckin
                (week_of, week_number, cpa_hours, exam_locked, tuesday_class,
                 budget_ok, new_debt, debt_payment, cardio, drinks, weight_lbs,
                 dfe_night, vented, energy, one_win, one_diff, score)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (str(week_of), week_num, cpa_hours, exam_locked, tue_class,
                  budget_ok, new_debt, debt_pay, cardio, drinks, weight,
                  dfe, vented, energy, win, diff, score))
            conn.commit()
            st.success(f"✅ Week of {week_of} saved! Your score: **{score}%**")
            if score >= 70:
                st.balloons()
        except Exception as e:
            st.error(f"Error saving: {e}")

# ── DAILY LOG ─────────────────────────────────────────────────────────────────
def page_daily(conn):
    st.title("📅 Daily Log")
    st.info("Log each evening. Takes 3 minutes. Builds the data that drives your reports.")

    HAB = {"✅ Done": 1, "❌ Missed": 0, "⏭️ Skip/N/A": -1}

    with st.form("daily_form"):
        c1, c2, c3 = st.columns(3)
        log_date = c1.date_input("Date", value=date.today())
        mit_text = c2.text_input("MIT — Most Important Task today")
        weight   = c3.number_input("Weight today (lbs, optional)", 0.0, 400.0, 0.0, 0.1)

        st.markdown("#### Daily Habits")
        c1, c2, c3 = st.columns(3)
        cpa_s  = c1.selectbox("📚 CPA Studied?",       list(HAB.keys()))
        cpamins= c2.number_input("CPA minutes", 0, 480, 0)
        cardio = c3.selectbox("🏃 Cardio?",             list(HAB.keys()))

        c1, c2, c3 = st.columns(3)
        drinks  = c1.number_input("🍺 Drinks today", 0, 20, 0)
        present = c2.selectbox("❤️ Present with partner?", list(HAB.keys()))
        no_vent = c3.selectbox("😤 No boss venting?",      list(HAB.keys()), index=2)

        c1, c2, c3 = st.columns(3)
        bud_ok  = c1.selectbox("💰 Budget OK?",           list(HAB.keys()), index=2)
        sleep   = c2.number_input("😴 Sleep hours", 0.0, 12.0, 7.0, 0.5)
        morning = c3.selectbox("🧘 Morning routine?",     list(HAB.keys()))

        mit_done= st.selectbox("📝 MIT Completed?", list(HAB.keys()))
        win_day = st.text_input("Win of the day")
        mood    = st.text_area("Mood / notes (optional)")

        submitted = st.form_submit_button("💾 Save Daily Log", type="primary")

    if submitted:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO tbl_DailyLog
                (log_date, cpa_studied, cpa_mins, cardio, drinks, weight_lbs,
                 present, no_venting, budget_ok, sleep_hrs, morning_routine,
                 mit_done, mit_text, win_of_day, mood_note)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (str(log_date), HAB[cpa_s], cpamins, HAB[cardio], drinks,
                  weight if weight > 0 else None, HAB[present], HAB[no_vent],
                  HAB[bud_ok], sleep, HAB[morning], HAB[mit_done],
                  mit_text, win_day, mood))
            conn.commit()
            st.success(f"✅ Daily log saved for {log_date}!")
        except Exception as e:
            st.error(f"Error: {e}")

# ── CPA TRACKER ───────────────────────────────────────────────────────────────
def page_cpa(conn):
    st.title("📚 CPA Tracker")

    exams = pd.read_sql("SELECT * FROM tbl_CPAExams ORDER BY exam_number", conn)

    st.subheader("Exam Status")
    for _, exam in exams.iterrows():
        with st.expander(f"Exam {exam['exam_number']} — {exam['section']}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", exam["status"])
            c2.metric("Target", exam["target_date"])
            c3.metric("Score",  exam["score"] or "—")
            c4.metric("Result", exam["pass_fail"])

            with st.form(f"exam_update_{exam['id']}"):
                nc1, nc2, nc3 = st.columns(3)
                new_status = nc1.selectbox("Update status",
                    ["Not Started", "Studying", "Registered", "Passed", "Failed - Retaking"],
                    index=["Not Started","Studying","Registered","Passed","Failed - Retaking"]
                         .index(exam["status"]) if exam["status"] in
                         ["Not Started","Studying","Registered","Passed","Failed - Retaking"] else 0)
                new_score  = nc2.number_input("Score (if taken)", 0, 99, int(exam["score"]) if exam["score"] else 0)
                new_pf     = nc3.selectbox("Pass/Fail", ["Pending", "PASS", "FAIL"],
                    index=["Pending","PASS","FAIL"].index(exam["pass_fail"]) if exam["pass_fail"] in ["Pending","PASS","FAIL"] else 0)
                if st.form_submit_button("Update Exam"):
                    conn.execute(
                        "UPDATE tbl_CPAExams SET status=?, score=?, pass_fail=? WHERE id=?",
                        (new_status, new_score if new_score > 0 else None, new_pf, exam["id"])
                    )
                    conn.commit()
                    st.success("Updated!")
                    st.rerun()

    st.divider()
    st.subheader("Log a Study Session")
    with st.form("study_form"):
        c1, c2, c3 = st.columns(3)
        study_date = c1.date_input("Date", value=date.today())
        exam_choice= c2.selectbox("Exam", [f"Exam {r['exam_number']} — {r['section'].split('—')[0]}" for _,r in exams.iterrows()])
        exam_id    = exams.iloc[["Exam 1","Exam 2","Exam 3","Exam 4"].index(exam_choice.split(" —")[0])]["id"]
        study_type = c3.selectbox("Type", ["Reading","Practice Questions","MCQ","Simulations","Live Class","Review","Mock Exam"])

        c1, c2, c3 = st.columns(3)
        topic   = c1.text_input("Topic covered")
        minutes = c2.number_input("Minutes studied", 0, 480, 60)
        conf    = c3.slider("Confidence (1–10)", 1, 10, 5)

        c1, c2 = st.columns(2)
        q_att = c1.number_input("Questions attempted", 0, 200, 0)
        q_cor = c2.number_input("Questions correct", 0, 200, 0)
        notes = st.text_area("Notes")

        if st.form_submit_button("💾 Save Study Session", type="primary"):
            conn.execute("""
                INSERT INTO tbl_StudyLog (study_date, exam_id, topic, minutes,
                    study_type, q_attempted, q_correct, confidence, notes)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (str(study_date), int(exam_id), topic, minutes, study_type, q_att, q_cor, conf, notes))
            conn.commit()
            st.success(f"✅ {minutes} min study session saved!")

    st.divider()
    st.subheader("Study Session History")
    sessions = pd.read_sql("""
        SELECT s.study_date, e.exam_number, s.topic, s.study_type,
               s.minutes, s.confidence, s.q_attempted, s.q_correct
        FROM tbl_StudyLog s
        JOIN tbl_CPAExams e ON s.exam_id = e.id
        ORDER BY s.study_date DESC LIMIT 50
    """, conn)
    if len(sessions):
        sessions["accuracy"] = sessions.apply(
            lambda r: f"{r['q_correct']}/{r['q_attempted']} ({r['q_correct']/r['q_attempted']*100:.0f}%)"
            if r["q_attempted"] > 0 else "—", axis=1)
        st.dataframe(sessions[["study_date","exam_number","topic","study_type","minutes","confidence","accuracy"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No study sessions yet. Log your first one above.")

# ── FINANCE ───────────────────────────────────────────────────────────────────
def page_finance(conn):
    st.title("💰 Finance Tracker")
    st.warning("Update once per month — first Sunday. Priority 2: non-negotiable.")

    with st.form("finance_form"):
        c1, c2, c3 = st.columns(3)
        month   = c1.text_input("Month (YYYY-MM)", value=date.today().strftime("%Y-%m"))
        label   = c2.text_input("Label", value=date.today().strftime("%B %Y"))
        debt    = c3.number_input("Total debt balance ($)", 0.0, 500000.0, 0.0, 100.0)

        c1, c2, c3 = st.columns(3)
        paid    = c1.number_input("Debt paid this month ($)", 0.0, 10000.0, 500.0, 50.0)
        efund   = c2.number_input("Emergency fund balance ($)", 0.0, 50000.0, 0.0, 50.0)
        new_d   = c3.number_input("New debt added ($)", 0.0, 50000.0, 0.0, 50.0)

        c1, c2 = st.columns(2)
        budget  = c1.number_input("Monthly budget ($)", 0.0, 20000.0, 0.0, 100.0)
        spend   = c2.number_input("Actual spend ($)", 0.0, 20000.0, 0.0, 100.0)
        notes   = st.text_area("Notes")

        if st.form_submit_button("💾 Save Finance Record", type="primary"):
            conn.execute("""
                INSERT OR REPLACE INTO tbl_FinanceLog
                (month_year, month_label, total_debt, debt_paid, emergency_fund,
                 new_debt, budget, actual_spend, notes)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (month, label, debt, paid, efund, new_d, budget, spend, notes))
            conn.commit()
            st.success(f"✅ Finance record saved for {label}!")

    st.divider()
    records = pd.read_sql("SELECT * FROM tbl_FinanceLog ORDER BY month_year DESC", conn)
    if len(records):
        total_paid = records["debt_paid"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Debt Reduced", f"${total_paid:,.0f}", delta=f"${6000-total_paid:,.0f} to $6k goal")
        c2.metric("Emergency Fund", f"${records.iloc[0]['emergency_fund']:,.0f}" if len(records) else "$0")
        c3.metric("Months Tracked", len(records))

        records["net_change"] = records["debt_paid"] - records["new_debt"]
        records["variance"] = records["budget"] - records["actual_spend"]
        st.dataframe(records[["month_label","total_debt","debt_paid","net_change","emergency_fund","variance"]].rename(
            columns={"month_label":"Month","total_debt":"Debt Balance","debt_paid":"Paid",
                     "net_change":"Net Change","emergency_fund":"Emerg. Fund","variance":"Budget Variance"}),
            use_container_width=True, hide_index=True)

# ── HEALTH ────────────────────────────────────────────────────────────────────
def page_health(conn):
    st.title("⚖️ Health Tracker")

    with st.form("health_form"):
        c1, c2, c3 = st.columns(3)
        week_of = c1.date_input("Week of", value=date.today())
        weight  = c2.number_input("Weight this Sunday (lbs)", 150.0, 400.0, 291.0, 0.1)
        change  = c3.number_input("Weight change vs last week", -10.0, 10.0, 0.0, 0.1)

        c1, c2, c3 = st.columns(3)
        cardio  = c1.number_input("Cardio sessions (target 3)", 0, 7, 0)
        cmins   = c2.number_input("Total cardio minutes", 0, 600, 0)
        drinks  = c3.number_input("Drinks this week (max 2)", 0, 50, 0)

        c1, c2 = st.columns(2)
        sleep   = c1.number_input("Avg sleep hrs/night", 0.0, 12.0, 7.0, 0.5)
        energy  = c2.slider("Energy level (1–10)", 1, 10, 5)
        notes   = st.text_area("Notes")

        if st.form_submit_button("💾 Save Health Log", type="primary"):
            conn.execute("""
                INSERT OR REPLACE INTO tbl_HealthLog
                (week_of, weight_lbs, cardio, cardio_mins, drinks, sleep_hrs, energy, notes)
                VALUES (?,?,?,?,?,?,?,?)
            """, (str(week_of), weight, cardio, cmins, drinks, sleep, energy, notes))
            conn.commit()
            st.success(f"✅ Health log saved! {291-weight:.1f} lbs lost from starting weight.")

    st.divider()
    logs = pd.read_sql("SELECT * FROM tbl_HealthLog ORDER BY week_of DESC", conn)
    if len(logs):
        latest = logs.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Weight", f"{latest['weight_lbs']} lbs",
                  delta=f"{latest['weight_lbs']-271:.1f} to 271 goal", delta_color="inverse")
        c2.metric("Cardio This Week", f"{latest['cardio']}/3",
                  delta="✅" if latest['cardio']>=3 else "⚠️")
        c3.metric("Drinks This Week", latest['drinks'],
                  delta="✅ On target" if latest['drinks']<=2 else "🔴 Over limit")
        c4.metric("Energy", f"{latest['energy']}/10")

        fig = px.line(logs.sort_values("week_of"), x="week_of", y="weight_lbs",
                      title="Weight Progress", color_discrete_sequence=[GREEN],
                      markers=True)
        fig.add_hline(y=271, line_dash="dash", line_color=AMBER,
                      annotation_text="Goal: 271 lbs", annotation_position="right")
        fig.update_layout(xaxis_title="Week", yaxis_title="Weight (lbs)",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ── MILESTONES ────────────────────────────────────────────────────────────────
def page_milestones(conn):
    st.title("🏆 18-Month Milestones")
    ms = pd.read_sql("SELECT * FROM tbl_Milestones ORDER BY target_date", conn)

    done = len(ms[ms["status"] == "Complete"])
    st.metric("Milestones Complete", f"{done} / {len(ms)}")
    st.progress(done / len(ms))
    st.divider()

    cat_colors = {"CPA": TEAL, "Finance": BLUE, "Health": GREEN,
                  "Relationship": PURPLE, "Work": AMBER, "Law School": NAVY}

    for _, row in ms.iterrows():
        col1, col2, col3, col4 = st.columns([3, 1.5, 1.2, 1])
        icon = "✅" if row["status"] == "Complete" else ("🚀" if row["status"] == "In Progress" else "⏳")
        col1.markdown(f"{icon} **{row['title']}**")
        col2.caption(row["target_date"])
        col3.caption(row["category"])
        new_status = col4.selectbox("", ["Pending", "In Progress", "Complete"],
            index=["Pending","In Progress","Complete"].index(row["status"])
                  if row["status"] in ["Pending","In Progress","Complete"] else 0,
            key=f"ms_{row['id']}", label_visibility="collapsed")
        if new_status != row["status"]:
            conn.execute("UPDATE tbl_Milestones SET status=? WHERE id=?",
                         (new_status, row["id"]))
            conn.commit()
            st.rerun()

# ── REPORTS ───────────────────────────────────────────────────────────────────
def page_reports(conn):
    st.title("📈 Reports & Charts")

    checkins = pd.read_sql("SELECT * FROM tbl_WeeklyCheckin ORDER BY week_of", conn)

    if len(checkins) == 0:
        st.info("No check-ins yet. Complete your first Sunday check-in to see reports.")
        return

    tab1, tab2, tab3 = st.tabs(["Weekly Scores", "Health Trend", "CPA Study Hours"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=checkins["week_of"], y=checkins["score"],
                             marker_color=TEAL, name="Weekly Score"))
        fig.add_hline(y=70, line_dash="dash", line_color=AMBER,
                      annotation_text="70% target")
        fig.update_layout(title="Weekly Score Trend (target: 70%+)",
                          xaxis_title="Week", yaxis_title="Score (%)",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(checkins[["week_of","cpa_hours","cardio","drinks",
                                "weight_lbs","energy","score"]].rename(
            columns={"week_of":"Week","cpa_hours":"CPA Hrs","cardio":"Cardio",
                     "drinks":"Drinks","weight_lbs":"Weight","energy":"Energy","score":"Score %"}),
            use_container_width=True, hide_index=True)

    with tab2:
        health = pd.read_sql("SELECT * FROM tbl_HealthLog ORDER BY week_of", conn)
        if len(health):
            fig = px.line(health, x="week_of", y="weight_lbs",
                          title="Weight vs Target (271 lbs)",
                          color_discrete_sequence=[GREEN], markers=True)
            fig.add_hline(y=271, line_dash="dash", line_color=AMBER,
                          annotation_text="Goal: 271")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = px.bar(checkins, x="week_of", y="cpa_hours",
                     title="CPA Study Hours per Week (target: 5+)",
                     color_discrete_sequence=[TEAL])
        fig.add_hline(y=5, line_dash="dash", line_color=AMBER,
                      annotation_text="5 hr target")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    init_db()
    conn = get_db()
    page = sidebar()

    if page == "📊 Dashboard":         page_dashboard(conn)
    elif page == "✅ Weekly Check-In": page_weekly_checkin(conn)
    elif page == "📅 Daily Log":       page_daily(conn)
    elif page == "📚 CPA Tracker":     page_cpa(conn)
    elif page == "💰 Finance":         page_finance(conn)
    elif page == "⚖️ Health":          page_health(conn)
    elif page == "🏆 Milestones":      page_milestones(conn)
    elif page == "📈 Reports & Charts": page_reports(conn)

    conn.close()

if __name__ == "__main__":
    main()
