import streamlit as st
import sqlite3
import json
import time
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
DB_PATH = "quiz_data.db"

def get_admin_password():
    # Prefer Streamlit secrets (set this in Streamlit Cloud -> App settings -> Secrets)
    # ADMIN_PASSWORD = "your-password-here"
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return "gladsa2026"  # fallback default — change this before sharing publicly!

QUIZ_TITLE = "Java DSA Mid-Term Quiz"

QUESTIONS = [
    {
        "q": "In Java, what happens when you repeatedly concatenate characters to an existing standard String object within a loop?",
        "options": [
            "A new String object is allocated each time in memory.",
            "A character array is temporarily generated in-place.",
            "The original String object is modified in-place.",
            "The garbage collector pauses the execution thread.",
        ],
        "correct": 0,
        "hint": "Think about String immutability — can a String object's internal character data ever change after creation?",
    },
    {
        "q": "Which class would you prefer over String for building a large string inside a loop with thousands of concatenations, and why?",
        "options": [
            "String, because it caches results automatically.",
            "StringBuilder, because it uses a mutable, resizable character buffer.",
            "Character, because it stores single characters more efficiently.",
            "Integer, because concatenation is a numeric operation.",
        ],
        "correct": 1,
        "hint": "Which class avoids creating a brand-new object on every single append?",
    },
    {
        "q": "What is the main difference between StringBuilder and StringBuffer?",
        "options": [
            "StringBuilder is immutable, StringBuffer is mutable.",
            "StringBuffer is synchronized (thread-safe), StringBuilder is not.",
            "StringBuilder can only hold numbers.",
            "There is no difference; they are aliases in Java.",
        ],
        "correct": 1,
        "hint": "One of them was designed with multi-threaded environments in mind — that comes with a performance cost.",
    },
    {
        "q": "In the Two Pointer technique with 'start' and 'end' pointers on a sorted array, what is the general condition to keep the loop running?",
        "options": [
            "start > end",
            "start == end",
            "start < end (or <=, depending on use case)",
            "end < 0",
        ],
        "correct": 2,
        "hint": "The two pointers move toward each other from opposite ends — when do they stop being valid?",
    },
    {
        "q": "What is the core idea behind the Sliding Window technique for array/string problems?",
        "options": [
            "Sorting the array before every comparison.",
            "Maintaining a contiguous range of elements and adjusting its boundaries instead of recomputing from scratch.",
            "Using recursion to check every possible subarray.",
            "Reversing the array first, then scanning left to right.",
        ],
        "correct": 1,
        "hint": "Think of a 'window' of fixed or variable size that slides across the array, reusing previous work.",
    },
    {
        "q": "Which data structure is most commonly used for Frequency Counting problems (e.g., LeetCode 242: Valid Anagram)?",
        "options": [
            "Stack",
            "HashMap (or an int[] array for fixed character sets like a-z)",
            "LinkedList",
            "Two-dimensional array",
        ],
        "correct": 1,
        "hint": "You need fast O(1) lookups to count how many times each character/element appears.",
    },
    {
        "q": "Two strings are anagrams of each other if:",
        "options": [
            "They have the same length only.",
            "They contain the exact same characters with the exact same frequencies, in any order.",
            "They start with the same letter.",
            "They are sorted identically only when reversed.",
        ],
        "correct": 1,
        "hint": "Think about what 'listen' and 'silent' have in common when you count each letter.",
    },
    {
        "q": "Given a Prefix Sum array built from arr[], how do you compute the sum of elements from index i to j (i <= j) in O(1) time?",
        "options": [
            "prefix[j] - prefix[i]",
            "prefix[j] + prefix[i]",
            "prefix[j] - prefix[i-1] (treating prefix[-1] as 0)",
            "You must always recompute the sum by looping from i to j.",
        ],
        "correct": 2,
        "hint": "The prefix array stores cumulative sums — subtract everything before index i from everything up to index j.",
    },
    {
        "q": "What is a strict requirement for Binary Search to work correctly on an array?",
        "options": [
            "The array must contain only positive integers.",
            "The array must be sorted.",
            "The array must have an even number of elements.",
            "The array must not contain duplicates.",
        ],
        "correct": 1,
        "hint": "Binary search eliminates half the search space each step — that only works if order is guaranteed.",
    },
    {
        "q": "What is the worst-case time complexity of Binary Search on an array of n elements, and how does it compare to Linear Search?",
        "options": [
            "O(n) — same as Linear Search.",
            "O(n^2) — slower than Linear Search.",
            "O(log n) — significantly faster than Linear Search's O(n) for large n.",
            "O(1) — constant time regardless of array size.",
        ],
        "correct": 2,
        "hint": "Each comparison in binary search cuts the remaining elements roughly in half.",
    },
]

# ============================================================
# DATABASE
# ============================================================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            ts TEXT NOT NULL,
            answers TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def save_attempt(name, score, total, answers):
    conn = get_conn()
    conn.execute(
        "INSERT INTO attempts (name, score, total, ts, answers) VALUES (?, ?, ?, ?, ?)",
        (name, score, total, datetime.now().isoformat(), json.dumps(answers)),
    )
    conn.commit()
    conn.close()

def fetch_all_attempts():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, name, score, total, ts, answers FROM attempts ORDER BY ts DESC"
    ).fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "score": r[2],
            "total": r[3],
            "ts": r[4],
            "answers": json.loads(r[5]),
        }
        for r in rows
    ]

def best_scores(entries):
    best = {}
    for e in entries:
        key = e["name"].strip().lower()
        if key not in best or e["score"] > best[key]["score"]:
            best[key] = e
    return sorted(best.values(), key=lambda e: (-e["score"], e["ts"]))

# ============================================================
# STYLE
# ============================================================
st.set_page_config(page_title=QUIZ_TITLE, page_icon="🧠", layout="centered")

st.markdown("""
<style>
:root{
  --navy:#0a1f44; --navy-light:#132c5c; --navy-lighter:#1c3a72;
  --gold:#d4af37; --gold-light:#e8c766; --grey:#9aa5b8;
  --red:#e05a5a; --green:#4caf7d;
}
.stApp{ background: linear-gradient(160deg, var(--navy) 0%, #050d1f 100%); }
h1, h2, h3, .stMarkdown p, label, span, div { color: #f7f7f5 !important; }
.quiz-title{ color: var(--gold-light) !important; font-weight: 800; }
.stButton>button{
  background: var(--gold); color: var(--navy); font-weight: 700;
  border-radius: 8px; border: none; padding: 0.5rem 1.2rem;
}
.stButton>button:hover{ background: var(--gold-light); color: var(--navy); }
div[data-testid="stForm"] { background: var(--navy-light); padding: 20px; border-radius: 12px; border: 1px solid var(--navy-lighter);}
.lb-row{
  display:flex; justify-content:space-between; padding:8px 0;
  border-bottom:1px solid var(--navy-lighter); font-size:15px;
}
.lb-row.me{ color: var(--gold-light) !important; font-weight:700; }
.hint-box{
  background: var(--navy); border-left: 3px solid var(--gold);
  padding: 10px 14px; border-radius: 6px; font-size: 13px; color: var(--grey) !important;
}
.sheet-q{
  background: var(--navy); border-radius: 10px; padding: 14px 16px;
  margin-bottom: 10px; border-left: 3px solid var(--navy-lighter);
}
.sheet-q.correct{ border-left-color: var(--green); }
.sheet-q.incorrect{ border-left-color: var(--red); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "page": "start",
    "name": "",
    "current": 0,
    "answers": [None] * len(QUESTIONS),
    "correct_count": 0,
    "wrong_count": 0,
    "show_hint": False,
    "admin_authed": False,
    "admin_view": "list",
    "admin_selected_id": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_quiz():
    st.session_state.page = "start"
    st.session_state.name = ""
    st.session_state.current = 0
    st.session_state.answers = [None] * len(QUESTIONS)
    st.session_state.correct_count = 0
    st.session_state.wrong_count = 0
    st.session_state.show_hint = False

# ============================================================
# SIDEBAR — ADMIN PANEL
# ============================================================
with st.sidebar:
    st.markdown("### Instructor Admin Panel")
    if not st.session_state.admin_authed:
        pw = st.text_input("Admin password", type="password", key="admin_pw_input")
        if st.button("Login", key="admin_login_btn"):
            if pw == get_admin_password():
                st.session_state.admin_authed = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    else:
        st.success("Logged in as instructor")
        if st.button("Log out", key="admin_logout_btn"):
            st.session_state.admin_authed = False
            st.session_state.admin_view = "list"
            st.rerun()

        entries = fetch_all_attempts()
        st.caption(f"{len(entries)} attempt(s) recorded")

        search = st.text_input("Search by name", key="admin_search")
        filtered = [e for e in entries if search.lower() in e["name"].lower()] if search else entries

        st.markdown("---")
        st.markdown("**All attempts** (click to view sheet)")
        for e in filtered:
            label = f"{e['name']} — {e['score']}/{e['total']} — {e['ts'][:16].replace('T',' ')}"
            if st.button(label, key=f"attempt_{e['id']}"):
                st.session_state.admin_selected_id = e["id"]
                st.session_state.admin_view = "detail"
                st.rerun()

# ============================================================
# ADMIN DETAIL VIEW (main pane, overrides quiz when active)
# ============================================================
def render_admin_detail():
    entries = fetch_all_attempts()
    entry = next((e for e in entries if e["id"] == st.session_state.admin_selected_id), None)
    if not entry:
        st.warning("Attempt not found.")
        if st.button("Back"):
            st.session_state.admin_view = "list"
            st.rerun()
        return

    st.markdown(f'<h2 class="quiz-title">{entry["name"]}\'s Answer Sheet</h2>', unsafe_allow_html=True)
    st.caption(f"Submitted: {entry['ts'][:19].replace('T',' ')} — Score: {entry['score']}/{entry['total']}")

    if st.button("← Back to all attempts"):
        st.session_state.admin_view = "list"
        st.rerun()

    for i, q in enumerate(QUESTIONS):
        ans = entry["answers"][i] if i < len(entry["answers"]) else None
        correct_letter = chr(65 + q["correct"])
        if ans is None:
            st.markdown(f"""
            <div class="sheet-q">
              <div><strong>Q{i+1}.</strong> {q['q']}</div>
              <div style="color:var(--grey);margin-top:6px;">Not answered.</div>
            </div>
            """, unsafe_allow_html=True)
            continue
        sel_idx = ans["selectedIdx"]
        is_correct = ans["correct"]
        sel_letter = chr(65 + sel_idx)
        cls = "correct" if is_correct else "incorrect"
        extra = ""
        if not is_correct:
            extra = f'<div style="color:var(--green);margin-top:4px;">Correct: {correct_letter}. {q["options"][q["correct"]]}</div>'
        mark = "✓" if is_correct else "✕"
        color = "var(--green)" if is_correct else "var(--red)"
        st.markdown(f"""
        <div class="sheet-q {cls}">
          <div><strong>Q{i+1}.</strong> {q['q']}</div>
          <div style="color:{color};margin-top:6px;">Answered: {sel_letter}. {q['options'][sel_idx]} {mark}</div>
          {extra}
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# MAIN PANE ROUTING
# ============================================================
if st.session_state.admin_authed and st.session_state.admin_view == "detail":
    render_admin_detail()

else:
    st.markdown(f'<h1 class="quiz-title">{QUIZ_TITLE}</h1>', unsafe_allow_html=True)

    # ---------- START ----------
    if st.session_state.page == "start":
        st.write("Enter your name to begin. Your score will be added to the class leaderboard.")
        with st.form("start_form"):
            name = st.text_input("Your name")
            submitted = st.form_submit_button("Start Quiz")
            if submitted:
                if name.strip():
                    st.session_state.name = name.strip()
                    st.session_state.page = "quiz"
                    st.rerun()
                else:
                    st.warning("Please enter your name.")

    # ---------- QUIZ ----------
    elif st.session_state.page == "quiz":
        idx = st.session_state.current
        total = len(QUESTIONS)
        q = QUESTIONS[idx]

        st.progress((idx) / total)
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.caption(f"**{st.session_state.name}** — Question {idx+1}/{total}")
        c2.markdown(f"<span style='color:var(--red);'>✕ {st.session_state.wrong_count}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span style='color:var(--green);'>✓ {st.session_state.correct_count}</span>", unsafe_allow_html=True)

        st.markdown(f"### {q['q']}")

        already_answered = st.session_state.answers[idx] is not None
        option_labels = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q["options"])]

        if not already_answered:
            choice = st.radio("Choose one:", option_labels, index=None, key=f"radio_{idx}")
            if st.button("Submit Answer", key=f"submit_{idx}"):
                if choice is not None:
                    sel_idx = option_labels.index(choice)
                    is_correct = sel_idx == q["correct"]
                    st.session_state.answers[idx] = {"selectedIdx": sel_idx, "correct": is_correct}
                    if is_correct:
                        st.session_state.correct_count += 1
                    else:
                        st.session_state.wrong_count += 1
                    st.rerun()
                else:
                    st.warning("Select an option first.")
        else:
            ans = st.session_state.answers[idx]
            for i, opt in enumerate(q["options"]):
                if i == q["correct"]:
                    st.success(f"{chr(65+i)}. {opt}  ✓ Correct answer")
                elif i == ans["selectedIdx"]:
                    st.error(f"{chr(65+i)}. {opt}  ✕ Your answer")
                else:
                    st.write(f"{chr(65+i)}. {opt}")

        with st.expander("Hint"):
            st.markdown(f'<div class="hint-box">{q["hint"]}</div>', unsafe_allow_html=True)

        st.markdown("---")
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("Back", disabled=(idx == 0)):
                st.session_state.current -= 1
                st.rerun()
        with nav2:
            is_last = idx == total - 1
            next_label = "Finish" if is_last else "Next"
            next_disabled = st.session_state.answers[idx] is None
            if st.button(next_label, disabled=next_disabled):
                if is_last:
                    save_attempt(
                        st.session_state.name,
                        st.session_state.correct_count,
                        total,
                        st.session_state.answers,
                    )
                    st.session_state.page = "results"
                    st.rerun()
                else:
                    st.session_state.current += 1
                    st.rerun()

    # ---------- RESULTS ----------
    elif st.session_state.page == "results":
        total = len(QUESTIONS)
        pct = round((st.session_state.correct_count / total) * 100)
        st.markdown(f"#### {st.session_state.name}'s Result")
        st.markdown(f"<h1 class='quiz-title'>{st.session_state.correct_count}/{total}</h1>", unsafe_allow_html=True)
        st.caption(f"{pct}% correct")

        st.markdown("### Class Leaderboard")
        entries = fetch_all_attempts()
        ranked = best_scores(entries)
        if not ranked:
            st.info("No scores yet — you're the first!")
        else:
            for i, e in enumerate(ranked):
                is_me = e["name"] == st.session_state.name and e["score"] == st.session_state.correct_count
                cls = "me" if is_me else ""
                st.markdown(f"""
                <div class="lb-row {cls}">
                  <span>{i+1}. {e['name']}</span>
                  <span>{e['score']}/{e['total']}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("Retake Quiz"):
            reset_quiz()
            st.rerun()
