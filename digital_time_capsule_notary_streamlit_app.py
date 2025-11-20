# app.py — "Digital Notary" (Stripe-inspired UI)
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date
import streamlit.components.v1 as components

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="Digital Notary",
    layout="wide",
)

# ---------------------------
# Database helpers (SQLite)
# ---------------------------
DB_PATH = "time_capsule.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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

def save_document(hash_val, content, signer, release_date_iso):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO sealed_docs (hash, content, signer_id, seal_date, release_date) VALUES (?, ?, ?, ?, ?)",
        (hash_val, content, signer, datetime.now().isoformat(), release_date_iso)
    )
    conn.commit()
    conn.close()

def get_document(hash_val):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM sealed_docs WHERE hash=?", (hash_val,))
    res = c.fetchone()
    conn.close()
    return res

def get_docs_for_user(user):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT hash, content, seal_date, release_date FROM sealed_docs WHERE signer_id=? ORDER BY seal_date DESC", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ---------------------------
# Utility: hash
# ---------------------------
def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ---------------------------
# CSS / UI (Stripe-like)
# ---------------------------
st.markdown(
    """
    <style>
    /* Root + background */
    :root{
        --bg:#0f1720;
        --card:#0b1220;
        --muted: #94a3b8;
        --accent: linear-gradient(90deg,#5eead4,#60a5fa);
        --glass: rgba(255,255,255,0.03);
    }
    /* Page background */
    [data-testid="stAppViewContainer"]{
        background: linear-gradient(180deg, #020617 0%, #07102a 100%);
        color: #e6eef8;
        min-height: 100vh;
    }
    /* Top nav */
    .top-nav{
        display:flex;align-items:center;justify-content:space-between;
        padding:18px 28px; gap:12px;
    }
    .brand{
        display:flex;align-items:center;gap:12px;
        font-weight:700;color:white;font-size:18px;
    }
    .brand .logo{
        width:36px;height:36px;border-radius:8px;
        background: linear-gradient(135deg,#7dd3fc,#a78bfa);
        display:inline-flex;align-items:center;justify-content:center;
        box-shadow: 0 4px 18px rgba(99,102,241,0.18);
        font-weight:800;color:#021124;
    }
    .nav-links { display:flex; gap:18px; align-items:center; color:var(--muted); font-weight:600; }
    .nav-cta { display:flex; gap:10px; align-items:center; }

    /* Big hero */
    .hero{
        display:grid;
        grid-template-columns: 1fr 420px;
        gap:36px;
        align-items:center;
        padding: 36px 28px;
    }
    .hero-card{
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius:16px; padding:26px;
        box-shadow: 0 12px 40px rgba(2,6,23,0.7);
        border: 1px solid rgba(255,255,255,0.04);
        backdrop-filter: blur(6px);
    }
    .hero h1{ font-size:42px; margin:0 0 12px 0; line-height:1.02; color: #e6f2ff;}
    .hero p { color: var(--muted); margin:0 0 22px 0; font-size:16px; }

    /* CTA button (elevated) */
    .cta {
        background: linear-gradient(90deg,#60a5fa,#7dd3fc);
        color:#021124; padding:12px 20px; border-radius:12px; font-weight:700;
        border:none; cursor:pointer; box-shadow: 0 10px 30px rgba(96,165,250,0.16);
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .cta:hover { transform: translateY(-4px); box-shadow: 0 18px 40px rgba(96,165,250,0.22); }

    /* secondary button */
    .btn-ghost{
        background: transparent; border:1px solid rgba(255,255,255,0.06); padding:10px 16px; border-radius:10px;
        color: var(--muted); font-weight:700;
    }

    /* small feature cards / grid */
    .grid{
        display:grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap:16px; margin-top:18px;
    }
    .feature{
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius:12px; padding:18px; border:1px solid rgba(255,255,255,0.03);
    }
    .feature h4 { margin:0; font-size:16px; color:#e6f2ff }
    .feature p { margin:6px 0 0 0; color:var(--muted); font-size:13px; }

    /* cards for ledger rows */
    .ledger-row{
        display:flex; flex-direction:column; gap:8px; padding:14px; border-radius:12px;
        background: rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.03);
    }
    .muted { color: var(--muted); font-size:13px; }

    /* small code block */
    pre.code {
        background: rgba(2,6,23,0.45);
        padding:12px; border-radius:8px; color:#cfe9ff; overflow:auto; font-size:13px;
    }

    /* Profile sidebar */
    .profile-box {
        background: linear-gradient(180deg, rgba(255,255,255,0.015), rgba(255,255,255,0.01));
        padding:18px; border-radius:12px; border:1px solid rgba(255,255,255,0.03);
    }

    /* responsive tweaks */
    @media (max-width: 980px) {
        .hero { grid-template-columns: 1fr; }
        .top-nav { padding: 12px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# small hero animation (subtle)
components.html("""
<style>
@keyframes floaty { 0% { transform: translateY(0px); } 50% { transform: translateY(-6px);} 100% { transform: translateY(0px);} }
.float-emoji { display:inline-block; transform-origin:center; animation: floaty 3.8s ease-in-out infinite; }
</style>
""", height=1)

# ---------------------------
# Top navigation (custom)
# ---------------------------
st.markdown("""
<div class="top-nav">
    <div style="display:flex;align-items:center;gap:18px;">
        <div class="brand">
            <div class="logo">DN</div>
            <div style="display:flex;flex-direction:column;line-height:0.95;">
                <div style="font-size:14px;color:#a5b4cc;font-weight:700">Digital Notary</div>
                <div style="font-size:11px;color:#94a3b8;margin-top:1px">Sealed · Verifiable · Time-locked</div>
            </div>
        </div>
        <div class="nav-links" style="margin-left:20px;">
            <div>Products</div>
            <div>Docs</div>
            <div>Pricing</div>
            <div>Support</div>
        </div>
    </div>

    <div class="nav-cta">
        <div class="muted">Signed in as: <strong style="color:white">{user}</strong></div>
    </div>
</div>
""".format(user=(st.session_state.user if "user" in st.session_state and st.session_state.user else "Guest")), unsafe_allow_html=True)

# ---------------------------
# HERO area (two columns)
# ---------------------------
col1, col2 = st.columns([2.2, 1])

with col1:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.markdown('<h1>Sealable time-capsules for your documents</h1>', unsafe_allow_html=True)
    st.markdown('<p>Seal any text as a cryptographic fingerprint (SHA-256). Share the hash and prove integrity later — with optional time-lock release dates.</p>', unsafe_allow_html=True)

    # CTA buttons row
    c1, c2, c3 = st.columns([0.7,0.7,1], gap="small")
    with c1:
        if st.button("Seal a document", key="hero_seal"):
            st.experimental_set_query_params(tab="seal")
    with c2:
        if st.button("Verify a document", key="hero_verify"):
            st.experimental_set_query_params(tab="verify")
    with c3:
        st.markdown('<button class="btn-ghost">Learn more</button>', unsafe_allow_html=True)

    # features grid
    st.markdown('<div class="grid" style="margin-top:18px">', unsafe_allow_html=True)
    st.markdown('<div class="feature"><h4>Tamper-evident</h4><p class="muted">Even one character change alters the fingerprint.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature"><h4>Time-lock release</h4><p class="muted">Only verify after the chosen date.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature"><h4>Persistent ledger</h4><p class="muted">Stored securely in a database with immutable hashes.</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # hero-card
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">'
                '<div><strong>Quick actions</strong><div class="muted" style="margin-top:6px;font-size:13px">Get started fast</div></div>'
                '</div>', unsafe_allow_html=True)

    if st.button("Quick Seal", key="quick_seal"):
        st.experimental_set_query_params(tab="seal")
    if st.button("My Profile", key="quick_profile"):
        st.experimental_set_query_params(tab="profile")

    st.markdown('<hr style="opacity:0.06;margin:14px 0">', unsafe_allow_html=True)
    st.markdown('<div class="muted" style="font-size:13px">Status</div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:10px;margin-top:8px"><div style="width:10px;height:10px;border-radius:50%;background:#34d399"></div><div>Database connected</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Main app content tabs (seal/verify/profile) using query param or default
# ---------------------------
# read URL param
params = st.experimental_get_query_params()
tab_q = params.get("tab", ["home"])[0]

tabs = ["home","seal","verify","profile"]

# use compact layout below hero
st.write("")
if tab_q == "home":
    # show a compact ledger preview
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.subheader("Recent seals")
    # fetch recent 6
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT hash, signer_id, seal_date, release_date FROM sealed_docs ORDER BY seal_date DESC LIMIT 6")
    rows = c.fetchall()
    conn.close()

    if not rows:
        st.info("No sealed documents yet — create the first one.")
    else:
        cols = st.columns(3)
        for i, r in enumerate(rows):
            with cols[i % 3]:
                h, signer, seal_date, release_date = r
                locked = datetime.now() < datetime.fromisoformat(release_date) if release_date else False
                status = "Locked" if locked else "Unlocked"
                st.markdown('<div class="ledger-row">', unsafe_allow_html=True)
                st.markdown(f"**{h[:12]}...**")
                st.markdown(f"<div class='muted'>by {signer} • {datetime.fromisoformat(seal_date).strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='muted'>Release: {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)
                if not locked:
                    if st.button(f"Verify {h[:8]}", key=f"v_{h[:8]}"):
                        st.experimental_set_query_params(tab="verify", hash=h)
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_q == "seal":
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.header("Seal a Document")
    if "user" not in st.session_state or not st.session_state.get("user"):
        st.warning("Please verify your identity first in the Profile tab (or use the Quick actions above).")

    # identity box inline
    col_a, col_b = st.columns([2,1])
    with col_a:
        doc_text = st.text_area("Paste the exact document text you want to seal", height=260)
    with col_b:
        st.markdown('<div class="profile-box">', unsafe_allow_html=True)
        st.markdown('<strong>Your identity</strong>')
        if "user" in st.session_state and st.session_state.get("user"):
            st.markdown(f"<div class='muted'>{st.session_state.user}</div>", unsafe_allow_html=True)
        else:
            name_inp = st.text_input("Enter a name to seal as", key="temp_name")
            if st.button("Set identity", key="set_identity"):
                if name_inp.strip():
                    st.session_state.user = name_inp.strip()
                    st.success("Identity set")
                else:
                    st.error("Enter a valid name")
        st.markdown('<hr style="opacity:0.06;margin:12px 0">', unsafe_allow_html=True)
        release_date = st.date_input("Release (unlock) date", min_value=date.today())
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("Generate Hash & Seal"):
            if not doc_text.strip():
                st.error("Document cannot be empty.")
            elif "user" not in st.session_state or not st.session_state.get("user"):
                st.error("Set your identity in the box on the right before sealing.")
            elif release_date <= date.today():
                st.error("Release date must be in the future.")
            else:
                h = sha256_hash(doc_text)
                save_document(h, doc_text, st.session_state.user, release_date.isoformat())
                st.success("Document sealed successfully.")
                st.markdown(f"<pre class='code'>{h}</pre>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_q == "verify":
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.header("Verify a Document")
    # prefill hash param if provided
    pre_hash = params.get("hash", [""])[0] if params else ""
    verify_hash = st.text_input("Paste Notarized Hash ID", value=pre_hash)
    verify_text = st.text_area("Paste Document Text to Verify", height=260)

    if st.button("Verify Document"):
        if not verify_hash or not verify_text:
            st.error("Provide both the Hash ID and the original text to verify.")
        else:
            record = get_document(verify_hash)
            if not record:
                st.error("Hash not found in ledger.")
            else:
                _id, h, content, signer, seal_date, release_date = record
                if datetime.now() < datetime.fromisoformat(release_date):
                    st.warning(f"Time-lock active. Release date: {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}")
                else:
                    current_hash = sha256_hash(verify_text)
                    if current_hash == verify_hash:
                        st.success(f"Document verified — sealed by {signer} on {datetime.fromisoformat(seal_date).strftime('%b %d, %Y %I:%M %p')}")
                    else:
                        st.error("Document does not match — fingerprint mismatch.")
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_q == "profile":
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.header("Profile — Your Documents")
    if "user" not in st.session_state or not st.session_state.get("user"):
        st.warning("Set your identity (name) by sealing a document or using the 'Set identity' action on the Seal tab.")
    else:
        user = st.session_state.user
        rows = get_docs_for_user(user)
        if not rows:
            st.info("You have no sealed documents yet.")
        else:
            st.markdown(f"<div style='margin-bottom:12px;color:#cbd5e1'>Found <strong>{len(rows)}</strong> sealed documents for <strong>{user}</strong></div>", unsafe_allow_html=True)
            for h, content, seal_date, release_date in rows:
                locked = datetime.now() < datetime.fromisoformat(release_date) if release_date else False
                status = "🔒 Locked" if locked else "🟢 Unlocked"
                expander_label = f"{status} — {h[:16]}..."
                with st.expander(expander_label):
                    st.markdown(f"**Hash:** `{h}`")
                    st.markdown(f"**Sealed on:** {datetime.fromisoformat(seal_date).strftime('%b %d, %Y %I:%M %p')}")
                    st.markdown(f"**Release date:** {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}")
                    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                    if locked:
                        st.info("Document locked until release date — content hidden.")
                    else:
                        if st.checkbox(f"Show full document content ({h[:8]}...)", key=f"show_{h[:8]}"):
                            st.text_area("Original Document", value=content, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="padding:28px 36px; color:#94a3b8; font-size:13px; text-align:center;">
    © {year} Digital Notary — cryptographic sealing & time-lock verification
</div>
""".format(year=datetime.now().year), unsafe_allow_html=True)
