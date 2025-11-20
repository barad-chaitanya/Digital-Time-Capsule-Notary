import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date

# -------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------
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


# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def save_document(hash_value, content, user, release_date):
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO documents (hash, content, user, seal_date, release_date)
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


# -------------------------------------------------------------
# PAGE STATE
# -------------------------------------------------------------
st.set_page_config(
    page_title="Digital Notary",
    layout="centered"
)

if "user" not in st.session_state:
    st.session_state.user = "Guest"

if "kyc" not in st.session_state:
    st.session_state.kyc = False

if "page" not in st.session_state:
    st.session_state.page = "KYC"


# -------------------------------------------------------------
# STRIPE UI CSS
# -------------------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

h1, h2, h3 {
    font-weight: 600 !important;
}

.button-row {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin-bottom: 22px;
}

/* Stripe Navigation Buttons (Glass/Depth Feel) */
.stButton>button {
    background: #0A0E27 !important;
    color: white !important;
    padding: 12px 26px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    transition: 0.25s ease !important;
    font-size: 15px !important;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.2) !important;
}

.stButton>button:hover {
    background: #2A2F52 !important;
    transform: translateY(-3px);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.35) !important;
}

.container-box {
    background: white;
    padding: 26px;
    border-radius: 14px;
    box-shadow: 0px 4px 24px rgba(0,0,0,0.08);
    border: 1px solid #EEE;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# HEADER (Stripe-like)
# -------------------------------------------------------------
st.markdown("<h2 style='text-align:center; color:#0A0E27;'>Digital Notary</h2>", unsafe_allow_html=True)
st.write("")
st.write("")


# -------------------------------------------------------------
# FIVE MAIN BUTTONS IN STRIPE STYLE
# -------------------------------------------------------------
st.markdown("<div class='button-row'>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("KYC"):
        st.session_state.page = "KYC"

with col2:
    if st.button("Home"):
        st.session_state.page = "Home"

with col3:
    if st.button("Seal"):
        st.session_state.page = "Seal"

with col4:
    if st.button("Verify"):
        st.session_state.page = "Verify"

with col5:
    if st.button("Profile"):
        st.session_state.page = "Profile"

st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE LOGIC
# -------------------------------------------------------------

# ---------- KYC ----------
if st.session_state.page == "KYC":
    st.subheader("🔷 Identity Verification")
    with st.container():
        with st.container():
            name = st.text_input("Enter Full Name", value=st.session_state.user)

            if st.button("Verify Identity"):
                if name.strip():
                    st.session_state.user = name.strip()
                    st.session_state.kyc = True
                    st.success("Identity Verified Successfully ✔")
                else:
                    st.error("Please enter your name.")

    if st.session_state.kyc:
        st.info(f"Verified as **{st.session_state.user}**")


# ---------- HOME ----------
elif st.session_state.page == "Home":
    st.subheader("Recent Sealed Documents")
    rows = fetch_user_documents(st.session_state.user)

    if not rows:
        st.info("No recent documents.")
    else:
        for hv, sd, rd, content in rows[:5]:
            with st.container():
                st.write(f"**Hash:** `{hv[:30]}...`")
                st.write(f"**Sealed:** {sd}")


# ---------- SEAL ----------
elif st.session_state.page == "Seal":
    st.subheader("Seal a Document")

    if not st.session_state.kyc:
        st.warning("Complete KYC first.")
    else:
        content = st.text_area("Enter Document Text")
        release = st.date_input("Release date", min_value=date.today())

        if st.button("Seal Document"):
            if not content.strip():
                st.error("Content cannot be empty.")
            else:
                h = sha256_hash(content)
                save_document(h, content, st.session_state.user, release.isoformat())
                st.success("Document Sealed ✔")
                st.code(h)


# ---------- VERIFY ----------
elif st.session_state.page == "Verify":
    st.subheader("Verify Document")

    h = st.text_input("Enter Document Hash")
    text = st.text_area("Paste Document Text")

    if st.button("Verify"):
        record = fetch_document(h)

        if not record:
            st.error("Hash not found ❌")
        else:
            hv, stored, user, sd, rd = record
            release_dt = datetime.fromisoformat(rd)

            if datetime.now() < release_dt:
                st.warning(f"🔒 Locked until {release_dt.strftime('%B %d, %Y')}")
            else:
                if sha256_hash(text) == h:
                    st.success("Document Verified ✔")
                    st.write(f"**Signed By:** {user}")
                else:
                    st.error("Content does not match ❌")


# ---------- PROFILE ----------
elif st.session_state.page == "Profile":
    st.subheader(f"{st.session_state.user}'s Documents")

    docs = fetch_user_documents(st.session_state.user)

    if not docs:
        st.info("No sealed documents.")
    else:
        for hv, sd, rd, content in docs:
            with st.container():
                st.write(f"**Hash:** `{hv}`")
                st.write(f"Sealed:** {sd}")
                st.write(f"Release:** {rd}")
                if st.checkbox(f"Show Document ({hv[:10]}...)"):
                    st.text_area("Content", content)

