# Sal Rodriguez — Coaching Dashboard
## Open Source · Python + SQLite + Streamlit

---

## Run on Your Computer (Windows, Mac, or Linux)

### Step 1 — Install Python (if not installed)
Download from python.org → Install → check "Add to PATH"

### Step 2 — Open Terminal / Command Prompt
- **Windows**: Press Win + R, type `cmd`, press Enter
- **Mac**: Press Cmd + Space, type `Terminal`, press Enter

### Step 3 — Install dependencies (one time only)
```
pip install streamlit pandas plotly
```

### Step 4 — Run the app
Navigate to this folder, then:
```
streamlit run app.py
```
Your browser opens automatically at http://localhost:8501

The database file `coaching.db` is created automatically in the same folder.

---

## Deploy FREE to the Cloud (access from phone, anywhere)

### Option A — Streamlit Cloud (easiest, Gmail login)
1. Create a free account at github.com (sign in with Gmail)
2. Create a new repository, upload app.py and requirements.txt
3. Go to share.streamlit.io → sign in with Gmail
4. Click "New app" → select your repository → Deploy
5. Get a public URL like: https://sal-coaching.streamlit.app

### Option B — Railway.app
1. Go to railway.app → sign in with Gmail
2. "New Project" → "Deploy from GitHub repo"
3. Add start command: `streamlit run app.py --server.port $PORT`
4. Done — free $5/month credit included

### Option C — Render.com
1. Go to render.com → sign in with Gmail
2. New → Web Service → connect GitHub repo
3. Build: `pip install -r requirements.txt`
4. Start: `streamlit run app.py --server.port 10000`
5. Free tier available

---

## What's Included

- 📊 **Dashboard** — KPIs, priority progress, exam status
- ✅ **Weekly Check-In** — Sunday accountability form (saves to DB)
- 📅 **Daily Log** — 10-habit tracker with scoring
- 📚 **CPA Tracker** — Exam status + study session log
- 💰 **Finance** — Monthly debt and budget tracking
- ⚖️ **Health** — Weight trend + cardio + alcohol tracking
- 🏆 **Milestones** — All 17 milestones with status toggle
- 📈 **Reports** — Charts: weekly score, weight trend, CPA hours

---

## Database
- Engine: SQLite (built into Python — zero install)
- File: `coaching.db` (lives in this folder)
- Backup: just copy `coaching.db` to Google Drive or Dropbox
- Import to MS Access: use the `Sal_Rodriguez_AccessSQL.sql` file

## Stack
- Python 3.9+
- Streamlit (web dashboard framework)
- SQLite (database)
- Pandas (data handling)
- Plotly (charts)
- All 100% free and open source
