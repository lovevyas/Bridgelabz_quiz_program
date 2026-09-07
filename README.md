# Java DSA Mid-Term Quiz — Streamlit App

A self-hosted, interactive MCQ quiz with a shared class leaderboard and a
password-gated instructor admin panel (view all attempts + full answer sheets).

## What's different from the artifact version
This is a real Python/SQLite backend, so scores persist properly and the
admin password is kept out of the page source (via Streamlit "Secrets"),
unlike the browser-only version.

**Note on persistence:** Streamlit Community Cloud's filesystem is not
guaranteed to survive every redeploy or long idle period. For a single
class session or a short assessment window this is fine. If you need
guaranteed long-term storage across redeploys, swap `sqlite3` for a hosted
DB (e.g. Supabase, Neon Postgres) — ask me and I can wire that up.

## Files
- `app.py` — the whole app
- `requirements.txt` — dependencies
- `.streamlit/secrets.toml.example` — template for the admin password

## Deploy to Streamlit Community Cloud (free)

1. **Create a GitHub repo** and upload `app.py` and `requirements.txt`
   to it (the `.streamlit/secrets.toml.example` file is optional — don't
   upload a real `secrets.toml` to GitHub, ever).

   Easiest way if you don't already use GitHub:
   - Go to https://github.com/new, create a repo (e.g. `java-dsa-quiz`)
   - Click "uploading an existing file" and drag in `app.py` and
     `requirements.txt`
   - Commit

2. **Sign in to Streamlit Cloud**: go to https://share.streamlit.io and
   sign in with your GitHub account.

3. **Deploy**: click "New app" → pick your repo, branch `main`, and set
   "Main file path" to `app.py` → click "Deploy".

4. **Set your admin password** (do this before sharing the link with
   students):
   - In your app's dashboard on Streamlit Cloud, click the "⋮" menu →
     **Settings** → **Secrets**
   - Paste:
     ```
     ADMIN_PASSWORD = "choose-your-own-password"
     ```
   - Save. The app will restart automatically.
   - If you skip this step, it falls back to the default password
     `gladsa2026` — change it before giving students the link.

5. **Share the URL** Streamlit gives you (looks like
   `https://your-app-name.streamlit.app`) with your students.

6. **You (the instructor)** open the same URL, open the **sidebar**
   (small arrow, top-left) → enter your admin password under
   "Instructor Admin Panel" → see every attempt, click any student's
   name to view their full answer sheet.

## Running locally first (optional, to test before deploying)
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your own password
streamlit run app.py
```

## Editing the questions
All 10 questions live in the `QUESTIONS` list near the top of `app.py`.
Each entry is:
```python
{
    "q": "question text",
    "options": ["A text", "B text", "C text", "D text"],
    "correct": 0,   # index of the correct option
    "hint": "hint text",
}
```
Add, remove, or edit entries there — the app adapts automatically.
