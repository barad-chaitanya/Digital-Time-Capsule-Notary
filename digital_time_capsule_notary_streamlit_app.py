import streamlit as st
import hashlib
from datetime import datetime, date

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="Time Capsule Notary | Modern UI",
    layout="centered"
)

# ---------------------------------------
# PREMIUM SOLID BACKGROUND + GLASS + 3D BUTTONS
# ---------------------------------------
st.markdown("""
<style>

    /* FULL PAGE SOLID PREMIUM BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(145deg, #0E0F11, #1A1B1E);
        color: white;
    }

    /* REMOVE TOP SPACING */
    .main .block-container {
        padding-top: 2rem;
    }

    /* ----- MODERN TITLE GLOW ----- */
    .title-glow {
        font-size: 46px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg,#B4E0FF,#6FBAFF,#4CC2F7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 25px rgba(100,170,255,0.45);
        letter-spacing: 1px;
    }

    .subtitle {
        text-align: center;
        color: #C9D6E8;
        margin-top: -14px;
        font-size: 17px;
        opacity: 0.85;
    }

    /* ----- GLASS CARD WITH SHINE + DEPTH ----- */
    .glass-card {
        background: rgba(255,255,255,0.06);
        padding: 28px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 
            0px 12px 25px rgba(0,0,0,0.6),
            inset 0px 1px 4px rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }

    /* Glass Shine Reflection */
    .glass-card::before {
        content: "";
        position: absolute;
        top: -80%;
        left: -40%;
        width: 200%;
        height: 200%;
        background: linear-gradient(120deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 60%);
        transform: rotate(25deg);
        pointer-events: none;
    }

    /* ----- PREMIUM 3D BUTTONS ----- */
    .stButton>button {
        background: linear-gradient(135deg, #57C1EB, #246FA8);
        color: white;
        border: none;
        padding: 12px 26px;
        font-size: 17px;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 
            0px 4px 14px rgba(0,150,255,0.45),
            inset 0px 1px 3px rgba(255,255,255,0.2);
        transition: 0.2s ease-in-out;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow:
            0px 7px 20px rgba(0,150,255,0.75),
            inset 0px 1px 4px rgba(255,255,255,0.25);
    }

    .stButton>button:active {
        transform: translateY(1px);
        box-shadow:
            0px 2px 10px rgba(0,150,255,0.45),
            inset 0px 1px 3px rgba(255,255,255,0.15);
    }

    /* TEXT INPUT + TEXT AREA PREMIUM GLASS FIELDS */
    textarea, input, select {
        background: rgba(255,255,255,0.08) !important;
        color: #E3ECF7 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        backdrop-filter: blur(6px) !important;
    }

    label, .stTextInput label {
        font-weight: 600 !important;
        color: #D3E1F2 !important;
        margin-bottom: 8px !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# TITLE
# ---------------------------------------
st.markdown("<h1 class='title-glow'>Digital Time Capsule Notary</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>High-fidelity cryptographic sealing & verification</p>", unsafe_allow_html=True)
st.write("")

# ---------------------------------------
# SESSION INIT
# ---------------------------------------
if 'ledger' not in st.session_state:
    st.session_state.ledger = {}
if 'kyc_verified' not in st.session_state:
    st.session_state.kyc_verified = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = "UNKNOWN"

# HASH
def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

# ---------------------------------------
# TABS
# ---------------------------------------
tab1, tab2, tab3 = st.tabs([
    "👤 Identity Setup",
    "📜 Seal Document",
    "🔍 Verify Integrity"
])

# ===========================
# TAB 1 — KYC
# ===========================
with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🔐 Identity Verification")

    st.info("Verification Status: " + ("✅ Verified" if st.session_state.kyc_verified else "❌ Unverified"))

    name = st.text_input("Enter Name / ID", value="" if st.session_state.user_id=="UNKNOWN" else st.session_state.user_id, disabled=st.session_state.kyc_verified)

    if st.button("Verify Identity", disabled=st.session_state.kyc_verified):
        if name.strip():
            st.session_state.user_id = name.strip()
            st.session_state.kyc_verified = True
            st.success("Identity Successfully Verified!")
        else:
            st.error("Enter a valid ID.")

    st.markdown("</div>", unsafe_allow_html=True)

# ===========================
# TAB 2 — SEAL DOCUMENT
# ===========================
with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.subheader("📜 Seal Your Document")

    if not st.session_state.kyc_verified:
        st.warning("Complete Identity Verification first.")

    else:
        doc_text = st.text_area("Paste document content", height=200)

        release_date = st.date_input("Release Date (Time Lock)", min_value=date.today())

        if st.button("Seal Document"):
            if not doc_text.strip():
                st.error("Document cannot be empty.")
            else:
                h = sha256_hash(doc_text)
                st.session_state.ledger[h] = {
                    "seal_date": datetime.now().isoformat(),
                    "signer_id": st.session_state.user_id,
                    "release_date": release_date.isoformat()
                }
                st.success("Document Sealed Successfully!")
                st.code(h)

    st.markdown("</div>", unsafe_allow_html=True)

# ===========================
# TAB 3 — VERIFICATION
# ===========================
with tab3:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.subheader("🔍 Verify Document")

    hash_id = st.text_input("Enter Hash ID")
    check_doc = st.text_area("Document to verify", height=200)

    if st.button("Verify Integrity"):
        record = st.session_state.ledger.get(hash_id)
        if not record:
            st.error("Invalid or unregistered hash.")
        else:
            # time lock
            if datetime.now() < datetime.fromisoformat(record["release_date"]):
                st.warning("🔒 Time lock active. Cannot verify yet.")
            else:
                if sha256_hash(check_doc) == hash_id:
                    st.success("🟢 Verified — Document is original.")
                else:
                    st.error("🔴 Document mismatch — Contents altered.")

    st.markdown("</div>", unsafe_allow_html=True)
