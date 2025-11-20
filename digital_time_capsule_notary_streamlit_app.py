import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date

# -------------------------------------------------------------
# 🔹 DATABASE SETUP
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
# 🔹 HELPER FUNCTIONS
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
# 🔹 PAGE SETUP
# -------------------------------------------------------------
st.set_page_config(page_title="Digital Notary", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = "Guest"

if "kyc" not in st.session_state:
    st.session_state.kyc = False

if "page" not in st.session_state:
    st.session_state.page = "KYC"


# -------------------------------------------------------------
# 🔹 PREMIUM GLASS UI CSS
# -------------------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}

/* GLASS BUTTONS */
.stButton>button {
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    padding: 14px 26px !important;
    border-radius: 14px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.18) !important;
    transition: 0.25s ease !important;
}

.stButton>button:hover {
    background: rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0px 8px 22px rgba(0,0,0,0.3) !important;
}

/* NAV BAR */
.nav-row {
    display: flex;
    justify-content: center;
    gap: 18px;
    margin-top: 10px;
    margin-bottom: 22px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# 🔹 HEADER
# -------------------------------------------------------------
st.markdown("## 🌌 Digital Notary — Secure. Premium. Simple.")
st.write("")


# -------------------------------------------------------------
# 🔹 NAVIGATION BUTTONS
# -------------------------------------------------------------
st.markdown("<div class='nav-row'>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🪪 KYC"):
        st.session_state.page = "KYC"

with col2:
    if st.button("🏠 Home"):
        st.session_state.page = "Home"

with col3:
    if st.button("🔏 Seal"):
        st.session_state.page = "Seal"

with col4:
    if st.button("🔎 Verify"):
        st.session_state.page = "Verify"

with col5:
    if st.button("👤 Profile"):
        st.session_state.page = "Profile"

st.markdown("</div>", unsafe_allow_html=True)

st.write("---")


# -------------------------------------------------------------
# 🔹 CARD COMPONENT
# -------------------------------------------------------------
def card(title, content):
    with st.container(border=True):
        st.subheader(title)
        st.write(content)


# -------------------------------------------------------------
# 🔹 KYC PAGE
# -------------------------------------------------------------
if st.session_state.page == "KYC":
    st.header("🪪 Identity Verification")

    with st.container(border=True):
        name = st.text_input("Enter Full Name", value=st.session_state.user)

        if st.button("Verify Identity"):
            if name.strip():
                st.session_state.user = name.strip()
                st.session_state.kyc = True
                st.success("Identity Verified Successfully ✔")
            else:
                st.error("Please enter your name.")

    if st.session_state.kyc:
        st.success(f"Verified as **{st.session_state.user}**")


# -------------------------------------------------------------
# 🔹 HOME PAGE
# -------------------------------------------------------------
elif st.session_state.page == "Home":
    st.header("✨ Recent Sealed Documents")

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT user, hash, seal_date FROM documents ORDER BY seal_date DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()

    if not rows:
        st.info("No documents sealed yet.")
    else:
        for user, hv, seal_date in rows:
            card(
                f"🔏 Sealed by {user}",
                f"**Hash:** `{hv[:30]}...`\n\n**Sealed On:** {seal_date}"
            )


# -------------------------------------------------------------
# 🔹 SEAL PAGE
# -------------------------------------------------------------
elif st.session_state.page == "Seal":
    st.header("🔏 Seal a Document")

    if not st.session_state.kyc:
        st.warning("Please complete KYC first.")
    else:
        with st.container(border=True):
            content = st.text_area("Enter Document Text")
            release = st.date_input("Release Date", min_value=date.today())

            if st.button("Seal Document"):
                if not content.strip():
                    st.error("Content cannot be empty.")
                else:
                    h = sha256_hash(content)
                    save_document(h, content, st.session_state.user, release.isoformat())
                    st.success("Document Sealed Successfully ✔")
                    st.code(h)


# -------------------------------------------------------------
# 🔹 VERIFY PAGE
# -------------------------------------------------------------
elif st.session_state.page == "Verify":
    st.header("🔎 Verify Document")

    with st.container(border=True):
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
                    st.warning(f"Locked until **{release_dt.strftime('%B %d, %Y')}**")
                else:
                    if sha256_hash(text) == h:
                        st.success("Document Verified ✔")
                        st.write(f"**Signed By:** {user}")
                        st.write(f"**Sealed On:** {sd}")
                    else:
                        st.error("Document content does not match ❌")


# -------------------------------------------------------------
# 🔹 PROFILE PAGE
# -------------------------------------------------------------
elif st.session_state.page == "Profile":
    st.header(f"👤 Documents of {st.session_state.user}")

    docs = fetch_user_documents(st.session_state.user)

    if not docs:
        st.info("You have not sealed any documents yet.")
    else:
        for hv, sd, rd, content in docs:
            with st.container(border=True):
                st.write(f"**Hash:** `{hv}`")
                st.write(f"**Sealed:** {sd}")
                st.write(f"**Releases:** {rd}")

                if st.checkbox(f"Show Content ({hv[:12]})"):
                    st.text_area("Content", content, height=150)

