import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date

# ---------------------------------
# DB Setup
# ---------------------------------
DB_PATH = "notary.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sealed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE,
            content TEXT,
            user TEXT,
            seal_date TEXT,
            release_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_doc(hash_val, content, user, release_date):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO sealed 
                 (hash, content, user, seal_date, release_date)
                 VALUES (?, ?, ?, ?, ?)""",
              (hash_val, content, user, datetime.now().isoformat(), release_date))
    conn.commit()
    conn.close()

def get_doc(hash_val):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM sealed WHERE hash=?", (hash_val,))
    data = c.fetchone()
    conn.close()
    return data

def get_user_docs(user):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT hash, content, seal_date, release_date FROM sealed WHERE user=?", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

# init DB
init_db()


# ---------------------------------
# APP UI
# ---------------------------------
st.title("Digital Notary")

# store username
if "user" not in st.session_state:
    st.session_state.user = "Guest"

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Seal", "Verify", "Profile"])

# USER NAME SECTION
st.sidebar.subheader("Your Name")
name_input = st.sidebar.text_input("Set your name", st.session_state.user)
if st.sidebar.button("Update name"):
    st.session_state.user = name_input
    st.sidebar.success("Name updated.")


# ---------------------------------
# HOME
# ---------------------------------
if page == "Home":
    st.header("Recent Sealed Documents")

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT hash, user, seal_date FROM sealed ORDER BY seal_date DESC LIMIT 5")
    recent = c.fetchall()
    conn.close()

    if not recent:
        st.info("No documents sealed yet.")
    else:
        for h, u, sd in recent:
            st.write(f"**Hash:** {h[:20]}...")
            st.write(f"Sealed by: {u}")
            st.write(f"Date: {sd}")
            st.write("---")


# ---------------------------------
# SEAL
# ---------------------------------
elif page == "Seal":
    st.header("Seal a Document")

    content = st.text_area("Enter your text")
    release_date = st.date_input("Release Date", min_value=date.today())

    if st.button("Seal Document"):
        if not content.strip():
            st.error("Content cannot be empty.")
        else:
            hash_val = hashlib.sha256(content.encode()).hexdigest()
            save_doc(hash_val, content, st.session_state.user, release_date.isoformat())
            st.success("Document sealed!")
            st.write("Document Hash:")
            st.code(hash_val)


# ---------------------------------
# VERIFY
# ---------------------------------
elif page == "Verify":
    st.header("Verify Document")

    hash_input = st.text_input("Enter Document Hash")
    text_input = st.text_area("Enter Document Text")

    if st.button("Verify"):
        record = get_doc(hash_input)
        if not record:
            st.error("Hash not found.")
        else:
            _id, h, content, user, seal_date, release_date = record

            release_dt = datetime.fromisoformat(release_date)
            now = datetime.now()

            if now < release_dt:
                st.warning(f"Document is locked until {release_dt.strftime('%b %d, %Y')}")
            else:
                computed = hashlib.sha256(text_input.encode()).hexdigest()
                if computed == hash_input:
                    st.success("Document Verified ✓")
                    st.write(f"Signed by {user} on {seal_date}")
                else:
                    st.error("Content does NOT match the sealed version.")


# ---------------------------------
# PROFILE
# ---------------------------------
elif page == "Profile":
    st.header(f"{st.session_state.user}'s Sealed Documents")

    docs = get_user_docs(st.session_state.user)

    if not docs:
        st.info("You haven't sealed anything yet.")
    else:
        for h, content, seal_date, release_date in docs:
            st.write(f"Hash: {h}")
            st.write(f"Sealed on: {seal_date}")
            st.write(f"Release: {release_date}")

            if st.checkbox(f"Show content {h[:8]}", key=h[:8]):
                st.text_area("Document", content, height=150)

            st.write("---")

    """,
    unsafe_allow_html=True,
)
