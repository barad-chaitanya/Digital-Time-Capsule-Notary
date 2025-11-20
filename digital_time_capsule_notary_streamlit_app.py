import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date
from typing import Optional, List, Tuple

# ---------------------------
# App & DB setup
# ---------------------------
st.set_page_config(page_title="Digital Notary — Premium", layout="centered")

DB_FILE = "notary.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
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

init_db()

# ---------------------------
# Utility functions
# ---------------------------
def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def save_document(hash_val: str, content: str, user: str, release_iso: str) -> bool:
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO documents (hash, content, user, seal_date, release_date) VALUES (?, ?, ?, ?, ?)",
            (hash_val, content, user, datetime.now().isoformat(), release_iso)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"DB save error: {e}")
        return False

def fetch_document(hash_val: str) -> Optional[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM documents WHERE hash=?", (hash_val,))
    row = c.fetchone()
    conn.close()
    return row

def fetch_user_docs(user: str) -> List[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT hash, seal_date, release_date, content FROM documents WHERE user=? ORDER BY seal_date DESC", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

def list_recent(limit: int = 6) -> List[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT hash, user, seal_date, release_date FROM documents ORDER BY seal_date DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------------------
# Session state defaults
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = "Guest"
if "kyc_done" not in st.session_state:
    st.session_state.kyc_done = False
if "page" not in st.session_state:
    st.session_state.page = "KYC"

# ---------------------------
# Premium CSS (glass + stripe gradient + animations)
# ---------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Gradient hero */
    .gradient-hero {
        background: linear-gradient(135deg,#07102a 0%, #3b2dfd 45%, #b46bff 100%);
        padding: 34px 22px;
        border-radius: 14px;
        color: white;
        text-align: center;
        box-shadow: 0 18px 60px rgba(12,18,35,0.55);
        margin-bottom: 20px;
    }
    .gradient-hero h1 {
        margin: 0;
        font-size: 28px;
        letter-spacing: -0.4px;
    }
    .gradient-hero p {
        margin: 6px 0 0 0;
        color: rgba(255,255,255,0.9);
        opacity: 0.95;
    }

    /* Nav button row */
    .nav-row {
        display:flex;
        justify-content:center;
        gap:12px;
        margin: 14px 0 18px 0;
    }

    /* Primary button (glass-like with depth) */
    .stButton>button.primary {
        background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        padding: 10px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 28px rgba(59,47,129,0.22) !important;
        transition: transform 160ms ease, box-shadow 160ms ease !important;
        backdrop-filter: blur(6px) !important;
    }
    .stButton>button.primary:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 18px 48px rgba(59,47,129,0.30) !important;
    }

    /* Secondary ghost button */
    .stButton>button.ghost {
        background: transparent !important;
        color: rgba(255,255,255,0.95) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        padding: 10px 18px !important;
        border-radius: 10px !important;
    }

    /* Glass card */
    .card {
        background: rgba(255,255,255,0.96);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 28px rgba(8,10,20,0.06);
        border: 1px solid rgba(16,24,40,0.03);
        transition: transform 200ms ease, box-shadow 200ms ease;
    }
    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 18px 48px rgba(8,10,20,0.10);
    }

    /* subtle fade-in */
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .fade-up { animation: fadeUp 420ms ease both; }

    /* small muted */
    .muted { color: #6b7280; font-size:13px; }

    /* code box style */
    pre.code {
        background: #0b1220;
        color: #e6f2ff;
        padding: 10px;
        border-radius: 8px;
        overflow-x: auto;
    }

    /* ensure buttons are full-width-ish on small screens */
    @media (max-width: 640px) {
        .nav-row { flex-wrap: wrap; gap:8px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Header / Hero
# ---------------------------
st.markdown(
    """
    <div class="gradient-hero fade-up">
        <h1>Digital Notary</h1>
        <p>Seal. Time-lock. Verify. A premium, secure way to prove your documents.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Top-nav with five buttons (apply CSS classes when rendering)
# ---------------------------
st.markdown("<div class='nav-row'>", unsafe_allow_html=True)
cols = st.columns(5)

# We will render native Streamlit buttons but apply classes afterward by simple trick:
# Use container buttons then later ensure CSS targets .stButton>button.primary (we add class via attribute not directly possible),
# so we'll use different keys and rely on the CSS for all stButton>button (primary look).
with cols[0]:
    if st.button("KYC", key="nav_kyc"):
        st.session_state.page = "KYC"
with cols[1]:
    if st.button("Home", key="nav_home"):
        st.session_state.page = "Home"
with cols[2]:
    if st.button("Seal", key="nav_seal"):
        st.session_state.page = "Seal"
with cols[3]:
    if st.button("Verify", key="nav_verify"):
        st.session_state.page = "Verify"
with cols[4]:
    if st.button("Profile", key="nav_profile"):
        st.session_state.page = "Profile"

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Small helper to render a card (safe) with optional title and content
# ---------------------------
def render_card(title: str, render_fn):
    st.markdown("<div class='card fade-up'>", unsafe_allow_html=True)
    if title:
        st.subheader(title)
    render_fn()
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

# ---------------------------
# Pages
# ---------------------------

# KYC Page
if st.session_state.page == "KYC":
    def kyc_content():
        st.write("Before sealing documents, verify your identity.")
        name = st.text_input("Full name", value=st.session_state.user, key="kyc_name")
        if st.button("Verify Identity", key="kyc_verify"):
            if name.strip():
                st.session_state.user = name.strip()
                st.session_state.kyc_done = True
                st.success(f"Identity verified as **{st.session_state.user}**")
            else:
                st.error("Please enter a valid name.")
        if st.session_state.get("kyc_done"):
            st.info(f"Verified: **{st.session_state.user}**")
    render_card("🪪 Identity Verification (KYC)", kyc_content)

# Home Page
elif st.session_state.page == "Home":
    def home_content():
        st.write("Recent sealed documents (latest first).")
        rows = list_recent(6)
        if not rows:
            st.info("No sealed documents yet. Seal your first document.")
        else:
            for h, user, seal_date, release_date in rows:
                st.markdown("<div class='card' style='padding:12px; margin-bottom:10px;'>", unsafe_allow_html=True)
                st.write(f"**Hash:** `{h[:28]}...`")
                st.write(f"Sealed by **{user}** on {datetime.fromisoformat(seal_date).strftime('%b %d, %Y')}")
                st.write(f"<span class='muted'>Release: {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    render_card("🏠 Recent Seals", home_content)

# Seal Page
elif st.session_state.page == "Seal":
    def seal_content():
        if not st.session_state.get("kyc_done", False):
            st.warning("Please complete KYC before sealing documents.")
            return
        content = st.text_area("Paste the exact document text to seal", height=220, key="seal_text")
        release = st.date_input("Release (unlock) date", min_value=date.today(), key="seal_release")
        if st.button("Generate Hash & Seal", key="seal_btn"):
            if not content.strip():
                st.error("Document content cannot be empty.")
                return
            if release <= date.today():
                st.error("Release date must be in the future.")
                return
            h = sha256_hash(content)
            ok = save_document(h, content, st.session_state.user, release.isoformat())
            if ok:
                st.success("Document sealed successfully.")
                st.markdown(f"<pre class='code'>{h}</pre>", unsafe_allow_html=True)
    render_card("🔏 Seal Document", seal_content)

# Verify Page
elif st.session_state.page == "Verify":
    def verify_content():
        st.write("Provide the hash and the document text to verify integrity.")
        hash_in = st.text_input("Notarized Hash ID", key="verify_hash")
        doc_text = st.text_area("Paste Document Text", height=200, key="verify_text")
        if st.button("Verify Document", key="verify_btn"):
            if not hash_in or not doc_text:
                st.error("Please provide both the Hash ID and document text.")
                return
            rec = fetch_document(hash_in)
            if not rec:
                st.error("Hash not found in ledger.")
                return
            _id, h, stored_content, signer, seal_date, release_date = rec
            # time-lock check
            try:
                rel_dt = datetime.fromisoformat(release_date)
            except Exception:
                st.error("Stored release date format error.")
                return
            if datetime.now() < rel_dt:
                st.warning(f"🔒 Time-lock active. Release date: {rel_dt.strftime('%B %d, %Y')}")
                return
            # integrity check
            cur_h = sha256_hash(doc_text)
            if cur_h == hash_in:
                st.success(f"🟢 VERIFIED — sealed by **{signer}** on {datetime.fromisoformat(seal_date).strftime('%b %d, %Y %I:%M %p')}")
            else:
                st.error("🔴 FAILED — Document content does not match the sealed fingerprint.")
    render_card("🔎 Verify Document", verify_content)

# Profile Page
elif st.session_state.page == "Profile":
    def profile_content():
        if not st.session_state.get("kyc_done", False):
            st.warning("Set up your identity in KYC to see your documents.")
            return
        user = st.session_state.user
        docs = fetch_user_docs(user)
        if not docs:
            st.info("You have not sealed any documents yet.")
            return
        st.write(f"Showing {len(docs)} sealed document(s) for **{user}**.")
        for h, seal_date, release_date, content in docs:
            st.markdown("<div class='card' style='padding:12px; margin-bottom:12px;'>", unsafe_allow_html=True)
            st.write(f"**Hash:** `{h}`")
            st.write(f"Sealed on: {datetime.fromisoformat(seal_date).strftime('%b %d, %Y %I:%M %p')}")
            try:
                locked = datetime.now() < datetime.fromisoformat(release_date)
            except Exception:
                locked = False
            st.write(f"Release date: {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}")
            if locked:
                st.info("⏳ This document is still locked — content will be visible after the release date.")
            else:
                if st.checkbox(f"Show content ({h[:10]}...)", key=f"show_{h[:10]}"):
                    st.text_area("Original Document", content, height=180)
            st.markdown("</div>", unsafe_allow_html=True)
    render_card("👤 Profile — Your Sealed Documents", profile_content)

# ---------------------------
# Footer
# ---------------------------
st.write("")
st.markdown("<div class='muted' style='text-align:center;'>© {year} Digital Notary</div>".format(year=datetime.now().year), unsafe_allow_html=True)

