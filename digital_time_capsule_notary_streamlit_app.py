import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Digital Time Capsule",
    layout="centered"
)

# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect("time_capsule.db")
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

def save_document(hash_val, content, signer, release_date):
    conn = sqlite3.connect("time_capsule.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO sealed_docs (hash, content, signer_id, seal_date, release_date) VALUES (?, ?, ?, ?, ?)",
        (hash_val, content, signer, datetime.now().isoformat(), release_date)
    )
    conn.commit()
    conn.close()

def get_document(hash_val):
    conn = sqlite3.connect("time_capsule.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sealed_docs WHERE hash=?", (hash_val,))
    res = c.fetchone()
    conn.close()
    return res

# Initialize DB
init_db()

# --------------------------------------------------
# HASH FUNCTION
# --------------------------------------------------
def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# --------------------------------------------------
# ULTRA PREMIUM ANIMATED CSS
# --------------------------------------------------
st.markdown("""
<style>

    /* ----------------------------------------
       PREMIUM BACKGROUND LAYER
    ----------------------------------------- */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top, #121318, #050506 70%);
        color: white;
        overflow: hidden;
    }

    /* Floating particles */
    @keyframes float {
        0% { transform: translateY(0px) translateX(0px); opacity: 0.5; }
        50% { transform: translateY(-40px) translateX(20px); opacity: 1; }
        100% { transform: translateY(0px) translateX(0px); opacity: 0.5; }
    }

    .particle {
        position: absolute;
        width: 8px;
        height: 8px;
        background: rgba(120,190,255,0.7);
        border-radius: 50%;
        box-shadow: 0px 0px 10px rgba(120,190,255,0.9);
        animation: float 6s infinite ease-in-out;
    }

    /* ----------------------------------------
       HOLOGRAPHIC TITLE
    ----------------------------------------- */
    .title {
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg,#4ACBFF,#A8D0FF,#4ACBFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 35px rgba(80,160,255,0.35);
        animation: glowTitle 4s infinite alternate;
    }

    @keyframes glowTitle {
        from { text-shadow: 0px 0px 20px rgba(80,160,255,0.15); }
        to { text-shadow: 0px 0px 40px rgba(80,160,255,0.55); }
    }

    /* ----------------------------------------
       ANIMATED GLASS CARD
    ----------------------------------------- */
    .glass-card {
        background: rgba(255,255,255,0.06);
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.12);
        padding: 28px;
        backdrop-filter: blur(12px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.45);
        position: relative;
        overflow: hidden;
    }

    /* Shine animation */
    .glass-card::before {
        content: "";
        position: absolute;
        top: -100%;
        left: -60%;
        width: 260%;
        height: 260%;
        background: linear-gradient(120deg, rgba(255,255,255,0.10), rgba(255,255,255,0));
        transform: rotate(20deg);
        animation: shine 7s infinite linear;
    }

    @keyframes shine {
        from { transform: translateX(-100%) rotate(20deg); }
        to   { transform: translateX(100%) rotate(20deg);  }
    }

    /* ----------------------------------------
       HOLOGRAPHIC BUTTONS
    ----------------------------------------- */
    .stButton>button {
        background: linear-gradient(135deg, #4ACBFF, #2476E5);
        padding: 12px 30px;
        border-radius: 14px;
        font-size: 18px;
        color: white;
        font-weight: 600;
        border: none;
        box-shadow:
            0px 7px 22px rgba(60,160,255,0.4),
            inset 0px 1px 4px rgba(255,255,255,0.2);
        transition: 0.2s;
    }

    .stButton>button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow:
            0px 12px 26px rgba(60,160,255,0.7),
            inset 0px 1px 5px rgba(255,255,255,0.25);
    }

    .stButton>button:active {
        transform: translateY(1px);
    }

    /* Inputs */
    textarea, input {
        background: rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #E8F1FF !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        backdrop-filter: blur(6px) !important;
    }

</style>

<script>
let body = window.parent.document.body;
for(let i=0; i<25; i++){
    let p = document.createElement("div");
    p.className = "particle";
    p.style.left = Math.random()*100 + "vw";
    p.style.top = Math.random()*100 + "vh";
    p.style.animationDuration = (6 + Math.random()*4) + "s";
    p.style.opacity = 0.3 + Math.random()*0.4;
    body.appendChild(p);
}
</script>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.markdown("<h1 class='title'>Digital Notary</h1>", unsafe_allow_html=True)

st.write("")

# SESSION
if "kyc" not in st.session_state:
    st.session_state.kyc = False
if "user" not in st.session_state:
    st.session_state.user = None

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Identity",
    "📜 Seal Document",
    "🔍 Verify",
    "🧾 Profile"
])

# --------------------------------------------------
# TAB 1 — IDENTITY
# --------------------------------------------------
with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("👤 Identity Verification")

    name = st.text_input("Enter your name / ID")

    if st.button("Verify Identity"):
        if name.strip():
            st.session_state.kyc = True
            st.session_state.user = name.strip()
            st.success("Identity verified!")
        else:
            st.error("Name cannot be empty.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# TAB 2 — SEAL
# --------------------------------------------------
with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if not st.session_state.kyc:
        st.warning("Verify identity first.")
    else:
        st.subheader("📜 Seal Document")

        content = st.text_area("Paste your document")
        release_date = st.date_input("Release date", min_value=date.today())

        if st.button("Seal Now"):
            if content.strip():
                h = sha256_hash(content)
                save_document(h, content, st.session_state.user, release_date.isoformat())
                st.success("Document sealed!")
                st.code(h)
            else:
                st.error("Document cannot be empty.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# TAB 3 — VERIFY
# --------------------------------------------------
with tab3:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.subheader("🔍 Verify Document Integrity")

    hash_val = st.text_input("Enter hash")
    new_content = st.text_area("Paste document to verify")

    if st.button("Verify"):
        record = get_document(hash_val)

        if not record:
            st.error("Hash not found in blockchain ledger!")
        else:
            _, _, original_content, signer, seal_date, release_date = record

            # Check time lock
            if datetime.now() < datetime.fromisoformat(release_date):
                st.warning(f"🔒 Locked until {release_date}")
            else:
                if sha256_hash(new_content) == hash_val:
                    st.success(f"🟢 Verified! Sealed by **{signer}** on {seal_date}")
                else:
                    st.error("🔴 Document has been altered!")

    st.markdown("</div>", unsafe_allow_html=True)
# --------------------------------------------------
# TAB 4 — PROFILE (USER DASHBOARD)
# --------------------------------------------------
with tab4:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🧾 Your Sealed Documents")

    if not st.session_state.kyc:
        st.warning("Verify identity first to see your documents.")
    else:
        conn = sqlite3.connect("time_capsule.db")
        c = conn.cursor()
        c.execute("SELECT hash, content, signer_id, seal_date, release_date FROM sealed_docs WHERE signer_id=?", 
                  (st.session_state.user,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            st.info("You have not sealed any documents yet.")
        else:
            st.success(f"Found **{len(rows)}** documents sealed by **{st.session_state.user}**")

            for hash_val, content, signer, seal_date, release_date in rows:
                # Check lock status
                locked = datetime.now() < datetime.fromisoformat(release_date)
                status = "🔒 Locked" if locked else "🟢 Unlocked"

                with st.expander(f"{status} — Hash: {hash_val[:20]}..."):
                    st.markdown(f"**Hash:** `{hash_val}`")
                    st.markdown(f"**Signed by:** {signer}")
                    st.markdown(f"**Sealed on:** {seal_date}")
                    st.markdown(f"**Release date:** {release_date}")

                    if not locked:
                        show = st.checkbox(f"Show document content for {hash_val[:10]}...", key=hash_val)
                        if show:
                            st.text_area("Original Document Content", content, height=150, disabled=True)
                    else:
                        st.info("⏳ This document is still locked. Content will be visible after the release date.")

    st.markdown("</div>", unsafe_allow_html=True)
