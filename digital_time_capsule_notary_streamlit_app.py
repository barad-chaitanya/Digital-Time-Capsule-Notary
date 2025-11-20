"""
Digital Notary — Stripe Enterprise style (Option C)
- Streamlit app with SQLite persistence for sealed documents
- Tabs: Identity, Seal, Verify, Profile
- Premium UI (glass, depth, subtle animations)
- Safe HTML usage (wrapped with st.markdown(..., unsafe_allow_html=True))
"""

import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date
from typing import Optional, List, Tuple

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(page_title="Digital Notary", layout="wide", initial_sidebar_state="auto")

# ---------------------------
# Database helpers
# ---------------------------
DB_PATH = "time_capsule.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sealed_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE,
            content TEXT,
            signer_id TEXT,
            seal_date TEXT,
            release_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_document(hash_val: str, content: str, signer: str, release_iso: str) -> bool:
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO sealed_docs (hash, content, signer_id, seal_date, release_date) VALUES (?, ?, ?, ?, ?)",
            (hash_val, content, signer, datetime.now().isoformat(), release_iso)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error while saving: {e}")
        return False

def get_document(hash_val: str) -> Optional[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM sealed_docs WHERE hash=?", (hash_val,))
    res = c.fetchone()
    conn.close()
    return res

def get_docs_for_user(user: str) -> List[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT hash, content, seal_date, release_date FROM sealed_docs WHERE signer_id=? ORDER BY seal_date DESC", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

def list_recent(limit: int = 6) -> List[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT hash, signer_id, seal_date, release_date FROM sealed_docs ORDER BY seal_date DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# Initialize DB at startup
init_db()

# ---------------------------
# Utilities
# ---------------------------
def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def iso_to_dt(iso: str) -> datetime:
    return datetime.fromisoformat(iso)

# ---------------------------
# PREMIUM CSS (Stripe Enterprise-like)
# ---------------------------
# Note: all raw HTML is injected via st.markdown(..., unsafe_allow_html=True) at top-level
st.markdown(
    """
    <style>
    :root{
        --bg-1: #f6f8fb;    /* light base */
        --bg-2: #0b1020;    /* deep dark accent */
        --card: rgba(255,255,255,0.06);
        --muted: #7b8aa3;
        --accent-1: #5eead4;
        --accent-2: #60a5fa;
        --glass-border: rgba(255,255,255,0.06);
    }

    /* Page background - subtle two-tone split */
    [data-testid="stAppViewContainer"]{
        background: linear-gradient(180deg, #0b1020 0%, #0f1724 40%, #eaf2fb 100%);
        min-height:100vh;
        color: #eaf2fb;
        font-family: "Inter", "Segoe UI", Roboto, sans-serif;
    }

    /* Top navigation bar (safe to render) */
    .dn-topbar {
        display:flex; align-items:center; justify-content:space-between;
        padding:16px 28px; gap:16px;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    .dn-brand { display:flex; gap:12px; align-items:center; }
    .dn-logo {
        width:42px; height:42px; border-radius:8px;
        background: linear-gradient(135deg,#344eeb,#2ed0c8);
        display:inline-flex; align-items:center; justify-content:center;
        font-weight:800; color:#041227; box-shadow: 0 6px 25px rgba(50,80,200,0.12);
    }
    .dn-title { font-weight:700; color:#eaf2fb; font-size:15px; }
    .dn-sub { font-size:12px; color: var(--muted); margin-top:-3px; }

    /* top actions */
    .dn-actions { display:flex; gap:12px; align-items:center; }

    /* hero container */
    .dn-hero {
        display:grid; grid-template-columns: 1fr 380px; gap:28px; padding:22px 28px;
    }

    .dn-hero-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius:14px; padding:26px; border:1px solid var(--glass-border);
        box-shadow: 0 20px 50px rgba(2,6,23,0.6); backdrop-filter: blur(6px);
    }

    .dn-hero h1 { margin:0; color:#eaf2fb; font-size:34px; line-height:1.05; }
    .dn-hero p  { margin-top:10px; color:var(--muted); font-size:15px; }

    /* CTA */
    .dn-cta {
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
        padding:10px 18px; color:#041227; font-weight:700; border-radius:12px;
        border:none; cursor:pointer; box-shadow: 0 10px 30px rgba(80,170,255,0.12);
        transition: transform .12s ease, box-shadow .15s ease;
    }
    .dn-cta:hover { transform: translateY(-4px); box-shadow: 0 18px 36px rgba(80,170,255,0.2); }

    /* neutral ghost button */
    .dn-ghost {
        background:transparent; border:1px solid rgba(255,255,255,0.06);
        padding:8px 14px; border-radius:10px; color:var(--muted); font-weight:700;
    }

    /* small features */
    .dn-grid { display:grid; grid-template-columns: repeat(auto-fill,minmax(210px,1fr)); gap:12px; margin-top:18px; }
    .dn-feature { padding:14px; border-radius:12px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005)); border:1px solid rgba(255,255,255,0.03); color:#eaf2fb;}

    /* hero-right card */
    .profile-box {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius:12px; padding:18px; border:1px solid rgba(255,255,255,0.03);
    }

    /* content cards */
    .glass-card {
        background: linear-gradient(180deg, rgba(10,14,20,0.65), rgba(255,255,255,0.02));
        border-radius:12px; padding:18px; border:1px solid rgba(255,255,255,0.04);
        box-shadow: 0 10px 30px rgba(2,6,23,0.5);
    }

    /* ledger rows */
    .ledger-row { padding:12px; border-radius:10px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.02); margin-bottom:10px; }
    .muted { color:var(--muted); font-size:13px; }

    pre.code {
        background: rgba(2,6,23,0.5);
        padding:12px; border-radius:8px; color:#cfe9ff; overflow:auto; font-size:13px;
    }

    /* responsive */
    @media (max-width: 980px) {
        .dn-hero { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Top navigation (render via st.markdown safely)
# ---------------------------
user_display = st.session_state.get("user", "Guest")

st.markdown(
    f"""
    <div class="dn-topbar">
        <div class="dn-brand">
            <div class="dn-logo">DN</div>
            <div>
                <div class="dn-title">Digital Notary</div>
                <div class="dn-sub">Sealed · Verifiable · Time-locked</div>
            </div>
        </div>

        <div class="dn-actions">
            <div style="color:var(--muted); font-weight:700; font-size:13px;">Signed in as <strong style="color:#eaf2fb; margin-left:6px;">{user_display}</strong></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Hero section
# ---------------------------
col_main, col_sidebar = st.columns([2.2, 1])

with col_main:
    st.markdown('<div class="dn-hero">', unsafe_allow_html=True)
    st.markdown('<div class="dn-hero-card">', unsafe_allow_html=True)
    st.markdown('<h1>Sealable, verifiable time-capsules for documents</h1>', unsafe_allow_html=True)
    st.markdown('<p>Seal any exact text with a SHA-256 fingerprint. Share the hash and prove the integrity later — optionally time-locked until a future release date.</p>', unsafe_allow_html=True)

    # CTA row
    c1, c2, c3 = st.columns([0.7, 0.7, 1])
    with c1:
        if st.button("Seal a document", key="cta_seal"):
            st.experimental_set_query_params(tab="seal")
    with c2:
        if st.button("Verify a document", key="cta_verify"):
            st.experimental_set_query_params(tab="verify")
    with c3:
        st.markdown('<button class="dn-ghost">Docs</button>', unsafe_allow_html=True)

    # Features grid
    st.markdown('<div class="dn-grid">', unsafe_allow_html=True)
    st.markdown('<div class="dn-feature"><strong>Tamper-evident</strong><div class="muted">Any change alters the fingerprint.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="dn-feature"><strong>Time-locks</strong><div class="muted">Only verify after the release date.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="dn-feature"><strong>Persistent ledger</strong><div class="muted">Stored securely with cryptographic hashes.</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # hero-card
    st.markdown('</div>', unsafe_allow_html=True)

with col_sidebar:
    st.markdown('<div class="profile-box">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size:16px;">Quick actions</strong>', unsafe_allow_html=True)
    st.markdown('<div class="muted" style="margin-top:6px;">Start sealing, verify, or view your profile.</div>', unsafe_allow_html=True)
    if st.button("Quick Seal", key="quick_seal"):
        st.experimental_set_query_params(tab="seal")
    if st.button("My Profile", key="quick_profile"):
        st.experimental_set_query_params(tab="profile")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Determine active tab (from query param or default)
# ---------------------------
params = st.experimental_get_query_params()
active_tab = params.get("tab", ["home"])[0]

# Provide a compact manual tab selector UI (safe Streamlit controls)
tab_buttons = st.columns([1,1,1,1])
with tab_buttons[0]:
    if st.button("Home", key="t_home"):
        st.experimental_set_query_params(tab="home")
with tab_buttons[1]:
    if st.button("Seal", key="t_seal"):
        st.experimental_set_query_params(tab="seal")
with tab_buttons[2]:
    if st.button("Verify", key="t_verify"):
        st.experimental_set_query_params(tab="verify")
with tab_buttons[3]:
    if st.button("Profile", key="t_profile"):
        st.experimental_set_query_params(tab="profile")

st.write("")  # spacing

# ---------------------------
# HOME (recent seals)
# ---------------------------
if active_tab == "home":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Recent sealed documents")
    recent = list_recent(6)
    if not recent:
        st.info("No sealed documents yet — be the first to seal one.")
    else:
        cols = st.columns(3)
        for idx, row in enumerate(recent):
            h, signer, seal_date, release_date = row
            locked = False
            try:
                locked = datetime.now() < iso_to_dt(release_date)
            except Exception:
                locked = False
            with cols[idx % 3]:
                st.markdown('<div class="ledger-row">', unsafe_allow_html=True)
                st.markdown(f"**{h[:12]}...**")
                st.markdown(f"<div class='muted'>by {signer} • {iso_to_dt(seal_date).strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='muted'>Release: {iso_to_dt(release_date).strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)
                if not locked:
                    if st.button(f"Verify {h[:8]}", key=f"verify_{h[:8]}"):
                        st.experimental_set_query_params(tab="verify", hash=h)
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# SEAL tab
# ---------------------------
elif active_tab == "seal":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("Seal Document")
    st.write("Paste the exact document text you want to seal. Choose a release (unlock) date in the future.")

    # identity / user field (persisted in session_state)
    if "user" not in st.session_state or not st.session_state.user:
        st.warning("You have not set your identity. Set a name below (this will be used as the signer_id).")

    left, right = st.columns([3, 1])
    with left:
        doc_text = st.text_area("Document content (exact text)", height=260, key="seal_text")
    with right:
        st.markdown('<div class="profile-box">', unsafe_allow_html=True)
        st.markdown('<strong>Signer</strong>', unsafe_allow_html=True)
        if st.session_state.get("user"):
            st.markdown(f"<div class='muted'>{st.session_state.get('user')}</div>", unsafe_allow_html=True)
        else:
            temp_name = st.text_input("Signer name", key="signer_name")
            if st.button("Set signer", key="set_signer"):
                if temp_name.strip():
                    st.session_state.user = temp_name.strip()
                    st.success("Signer set.")
                else:
                    st.error("Enter a valid name.")
        st.markdown('<hr style="opacity:0.06;margin:12px 0">', unsafe_allow_html=True)
        release_date = st.date_input("Release date (unlock)", min_value=date.today(), key="release_date")
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("Generate Hash & Seal", key="do_seal"):
            if not doc_text or not doc_text.strip():
                st.error("Document content cannot be empty.")
            elif not st.session_state.get("user"):
                st.error("Set signer name before sealing.")
            elif release_date <= date.today():
                st.error("Release date must be in the future.")
            else:
                h = sha256_hash(doc_text)
                ok = save_document(h, doc_text, st.session_state.user, release_date.isoformat())
                if ok:
                    st.success("Document sealed successfully.")
                    st.markdown(f"<pre class='code'>{h}</pre>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# VERIFY tab
# ---------------------------
elif active_tab == "verify":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("Verify Document")
    query_hash = params.get("hash", [""])[0] if params else ""
    verify_hash = st.text_input("Paste Notarized Hash ID", value=query_hash, key="verify_hash")
    verify_text = st.text_area("Paste Document text to verify", height=260, key="verify_text")

    if st.button("Verify Document", key="do_verify"):
        if not verify_hash or not verify_text:
            st.error("Please provide both the Hash ID and the document text.")
        else:
            record = get_document(verify_hash)
            if not record:
                st.error("Hash not found in ledger.")
            else:
                _id, h, content, signer, seal_date, release_date = record
                try:
                    locked = datetime.now() < iso_to_dt(release_date)
                except Exception:
                    locked = False
                if locked:
                    st.warning(f"🔒 Time-lock active. Release date: {iso_to_dt(release_date).strftime('%b %d, %Y')}")
                else:
                    current_hash = sha256_hash(verify_text)
                    if current_hash == verify_hash:
                        st.success(f"🟢 Verified — sealed by {signer} on {iso_to_dt(seal_date).strftime('%b %d, %Y %I:%M %p')}")
                    else:
                        st.error("🔴 Verification failed — document content does not match the sealed fingerprint.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# PROFILE tab
# ---------------------------
elif active_tab == "profile":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("Profile — Your sealed documents")

    if not st.session_state.get("user"):
        st.warning("Set your signer name first (in Seal tab) to see your documents.")
    else:
        user = st.session_state.user
        docs = get_docs_for_user(user)
        if not docs:
            st.info("You have not sealed any documents yet.")
        else:
            st.markdown(f"<div class='muted'>Found <strong>{len(docs)}</strong> sealed document(s) for <strong>{user}</strong></div>", unsafe_allow_html=True)
            for h, content, seal_date, release_date in docs:
                try:
                    locked = datetime.now() < iso_to_dt(release_date)
                except Exception:
                    locked = False
                label = "🔒 Locked" if locked else "🟢 Unlocked"
                with st.expander(f"{label} — {h[:18]}..."):
                    st.markdown(f"**Hash:** `{h}`")
                    st.markdown(f"**Sealed on:** {iso_to_dt(seal_date).strftime('%b %d, %Y %I:%M %p')}")
                    st.markdown(f"**Release date:** {iso_to_dt(release_date).strftime('%b %d, %Y')}")
                    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                    if locked:
                        st.info("Document is still locked. Content will be visible after release date.")
                    else:
                        if st.checkbox(f"Show full document content ({h[:8]}...)", key=f"show_{h[:8]}"):
                            st.text_area("Original Document", value=content, height=200, key=f"content_{h[:8]}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    f"""
    <div style="padding:28px 36px; color:var(--muted); font-size:13px; text-align:center;">
        © {datetime.now().year} Digital Notary — cryptographic sealing & time-lock verification
    </div>
    """,
    unsafe_allow_html=True,
)
