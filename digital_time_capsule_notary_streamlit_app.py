import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date

# -------------------------------------------
# DATABASE SETUP
# -------------------------------------------
DB_FILE = "notary.db"

def connect_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def setup_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            hash TEXT PRIMARY KEY,
            content TEXT,
            user TEXT,
            seal_date TEXT,
            release_date TEXT
        )
    """)
    conn.commit()
    conn.close()

setup_db()


# -------------------------------------------
# HELPERS
# -------------------------------------------
def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def save_document(hash_value, content, user, release_date):
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO documents (hash, content, user, seal_date, release_date)
        VALUES (?, ?, ?, ?, ?)
    """, (hash_value, content, user, datetime.now().isoformat(), release_date))
    conn.commit()
    conn.close()

def fetch_document(hash_value):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM documents WHERE hash=?", (hash_value,))
    result = c.fetchone()
    conn.close()
    return result

def fetch_user_documents(user):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT hash, seal_date, release_date, content FROM documents WHERE user=?", (user,))
    rows = c.fetchall()
    conn.close()
    return rows


# -------------------------------------------
# UI SETUP
# -------------------------------------------
st.set_page_config(page_title="Digital Notary", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = "Guest"
if "page" not in st.session_state:
    st.session_state.page = "Home"


# -------------------------------------------
# NAVIGATION (TOP BUTTONS)
# -------------------------------------------
st.markdown("## 🌌 Digital Notary — Secure. Simple. Premium.")
st.write("")

col1, col2, col3, col4 = st.columns(4)

if col1.button("🏠 Home"):
    st.session_state.page = "Home"
if col2.button("🔏 Seal"):
    st.session_state.page = "Seal"
if col3.button("🔎 Verify"):
    st.session_state.page = "Verify"
if col4.button("👤 Profile"):
    st.session_state.page = "Profile"

st.write("---")


# -------------------------------------------
# CARD COMPONENT
# -------------------------------------------
def card(title, content):
    with st.container(border=True):
        st.subheader(title)
        st.write(content)
        st.write("")


# -------------------------------------------
# HOME PAGE
# -------------------------------------------
if st.session_state.page == "Home":
    st.header("✨ Recently Sealed Documents")

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT user, hash, seal_date FROM documents ORDER BY seal_date DESC LIMIT 5")
    entries = c.fetchall()
    conn.close()

    if not entries:
        st.info("No documents sealed yet.")
    else:
        for user, hv, seal_date in entries:
            card(
                f"🔏 Document by {user}",
                f"**Hash:** `{hv[:30]}...`\n\n**Sealed on:** {seal_date}"
            )


# -------------------------------------------
# SEAL PAGE
# -------------------------------------------
elif st.session_state.page == "Seal":
    st.header("🔏 Seal a Document")

    with st.container(border=True):
        content = st.text_area("Document Text")
        release_date = st.date_input("Release Date", min_value=date.today())

        if st.button("Seal Document"):
            if not content.strip():
                st.error("Document cannot be empty.")
            else:
                hash_value = sha256_hash(content)
                save_document(hash_value, content, st.session_state.user, release_date.isoformat())

                st.success("Document successfully sealed!")
                st.code(hash_value)


# -------------------------------------------
# VERIFY PAGE
# -------------------------------------------
elif st.session_state.page == "Verify":
    st.header("🔎 Verify a Document")

    with st.container(border=True):
        input_hash = st.text_input("Enter Hash")
        input_text = st.text_area("Paste Document Text")

        if st.button("Verify"):
            record = fetch_document(input_hash)

            if not record:
                st.error("Hash not found.")
            else:
                hv, stored_content, user, seal_date, rel = record
                release_dt = datetime.fromisoformat(rel)

                if datetime.now() < release_dt:
                    st.warning(f"Document locked until **{release_dt.strftime('%B %d, %Y')}**")
                else:
                    if sha256_hash(input_text) == input_hash:
                        st.success("Document Verified ✔")
                        st.write(f"**Signed by:** {user}")
                        st.write(f"**Sealed on:** {seal_date}")
                    else:
                        st.error("Document content does NOT match original ❌")


# -------------------------------------------
# PROFILE PAGE
# -------------------------------------------
elif st.session_state.page == "Profile":
    st.header(f"👤 {st.session_state.user}'s Documents")

    docs = fetch_user_documents(st.session_state.user)

    if not docs:
        st.info("You have not sealed any documents yet.")
    else:
        for hv, sd, rd, content in docs:
            with st.container(border=True):
                st.write(f"**Hash:** `{hv}`")
                st.write(f"**Sealed:** {sd}")
                st.write(f"**Releases:** {rd}")

                if st.checkbox(f"Show Content ({hv[:10]})"):
                    st.text_area("Document Content", content, height=150)
