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
# DATABASE HELPERS
# -------------------------------------------
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
# HASH FUNCTION
# -------------------------------------------
def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


# -------------------------------------------
# STREAMLIT APP SETUP
# -------------------------------------------
st.set_page_config(page_title="Digital Notary", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = "Guest"

st.title("Digital Notary")


# -------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------
st.sidebar.header("Navigation")
page = st.sidebar.radio("Choose a section:", ["Home", "Seal Document", "Verify Document", "Profile"])

# USER NAME
st.sidebar.subheader("Your Name")
name = st.sidebar.text_input("Enter your name", st.session_state.user)

if st.sidebar.button("Set Name"):
    if name.strip():
        st.session_state.user = name.strip()
        st.sidebar.success("Name updated!")


# -------------------------------------------
# HOME PAGE
# -------------------------------------------
if page == "Home":
    st.header("Recent Sealed Documents")

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT user, hash, seal_date FROM documents ORDER BY seal_date DESC LIMIT 5")
    entries = c.fetchall()
    conn.close()

    if not entries:
        st.info("No documents have been sealed yet.")
    else:
        for user, hash_val, seal_date in entries:
            st.write(f"**User:** {user}")
            st.write(f"**Hash:** `{hash_val[:25]}...`")
            st.write(f"**Sealed on:** {seal_date}")
            st.write("---")


# -------------------------------------------
# SEAL DOCUMENT
# -------------------------------------------
elif page == "Seal Document":
    st.header("Seal a Document")

    content = st.text_area("Enter the document text here")
    release_date = st.date_input("Release Date", min_value=date.today())

    if st.button("Seal"):
        if not content.strip():
            st.error("Document cannot be empty.")
        else:
            hash_value = sha256_hash(content)
            save_document(hash_value, content, st.session_state.user, release_date.isoformat())

            st.success("Document successfully sealed!")
            st.write("Your document hash:")
            st.code(hash_value)


# -------------------------------------------
# VERIFY DOCUMENT
# -------------------------------------------
elif page == "Verify Document":
    st.header("Verify a Document")

    input_hash = st.text_input("Enter document hash")
    input_text = st.text_area("Paste the document text you want to verify")

    if st.button("Verify"):
        record = fetch_document(input_hash)

        if not record:
            st.error("Hash not found in registry.")
        else:
            hash_val, stored_content, user, seal_date, release_date = record

            # Time-lock check
            release_dt = datetime.fromisoformat(release_date)
            if datetime.now() < release_dt:
                st.warning(f"This document is locked until: {release_dt.strftime('%B %d, %Y')}")
            else:
                computed_hash = sha256_hash(input_text)
                if computed_hash == input_hash:
                    st.success("Document successfully verified!")
                    st.write(f"Signed by: **{user}**")
                    st.write(f"Sealed on: **{seal_date}**")
                else:
                    st.error("Document content does NOT match original.")


# -------------------------------------------
# PROFILE PAGE
# -------------------------------------------
elif page == "Profile":
    st.header(f"{st.session_state.user}'s Document History")

    docs = fetch_user_documents(st.session_state.user)

    if not docs:
        st.info("You have not sealed any documents yet.")
    else:
        for hash_val, seal_date, release_date, content in docs:
            st.write(f"**Hash:** `{hash_val}`")
            st.write(f"Sealed on: {seal_date}")
            st.write(f"Releases on: {release_date}")

            if st.checkbox(f"Show content for {hash_val[:8]}"):
                st.text_area("Document Content", content, height=150)

            st.write("---")
