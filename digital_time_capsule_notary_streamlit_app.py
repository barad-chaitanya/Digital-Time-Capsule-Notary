import streamlit as st
import hashlib
from datetime import datetime, date
import base64

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="Time Capsule Notary",
    layout="wide",
)

# ================================
# BACKGROUND IMAGE
# ================================
  # replace with any bg image you want

def set_bg():
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: url('{bg_url}');
            background-size: cover;
            background-attachment: fixed;
        }}
        
        /* Remove top padding */
        .main .block-container {{
            padding-top: 2rem;
        }}
        
        /* Glass cards */
        .glass {{
            background: rgba(255, 255, 255, 0.13);
            padding: 25px;
            border-radius: 18px;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: 0px 4px 30px rgba(0,0,0,0.25);
        }}

        /* Title neon glow */
        .title-glow {{
            font-size: 44px;
            font-weight: 800;
            color: #ffffff;
            text-shadow: 0px 0px 20px rgba(0,255,255,0.9);
            text-align: center;
        }}

        /* Subtext */
        .subtitle {{
            text-align: center;
            font-size: 18px;
            margin-top: -10px;
            color: #e0f7ff;
        }}

        /* Neon buttons */
        .stButton>button {{
            background: linear-gradient(135deg, #00f2ff, #007bff);
            color: black;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            border: none;
            font-size: 17px;
            font-weight: 600;
            box-shadow: 0px 0px 12px rgba(0,255,255,0.7);
            transition: 0.3s ease;
        }}
        .stButton>button:hover {{
            transform: scale(1.05);
            box-shadow: 0px 0px 20px rgba(0,255,255,1);
        }}

        /* Inputs glass styling */
        textarea, input {{
            background: rgba(255,255,255,0.3)!important;
            backdrop-filter: blur(5px)!important;
            border-radius: 10px!important;
            color: white !important;
        }}

        .block-container {{
            color: white;
        }}

        .tabs-label {{
            font-size: 20px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# ================================
# SESSION INIT
# ================================
if 'ledger' not in st.session_state:
    st.session_state.ledger = {}
if 'kyc_verified' not in st.session_state:
    st.session_state.kyc_verified = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = "UNKNOWN"

# ================================
# HASHING LOGIC
# ================================
def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# ================================
# MAIN TITLE
# ================================
st.markdown("<h1 class='title-glow'>🔮 Digital Time Capsule Notary</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A futuristic blockchain-style sealing & verification system</p>", unsafe_allow_html=True)
st.markdown("")

# ================================
# TABS WITH MODERN LOOK
# ================================
tab1, tab2, tab3 = st.tabs([
    "👤 Identity Setup",
    "📜 Seal Document",
    "🔍 Verify Integrity"
])

# ============================================================
# TAB 1 — KYC (DUMMY)
# ============================================================
with tab1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    st.subheader("🔐 Identity Verification (Dummy KYC)")

    st.write(
        """
        This simulation mimics a blockchain identity oracle.  
        Enter your name to become *Verified*.
        """
    )

    status_emoji = "✅" if st.session_state.kyc_verified else "❌"
    status_text = "VERIFIED" if st.session_state.kyc_verified else "UNVERIFIED"
    st.info(f"**Status:** {status_emoji} {status_text}")

    user_name = st.text_input(
        "Enter your Name / ID",
        value=st.session_state.user_id if st.session_state.user_id != "UNKNOWN" else "",
        disabled=st.session_state.kyc_verified
    )

    if st.button("Verify Identity", disabled=st.session_state.kyc_verified):
        if user_name.strip():
            st.session_state.user_id = user_name.strip()
            st.session_state.kyc_verified = True
            st.success("Identity Verified!")
        else:
            st.error("Enter a valid name.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# TAB 2 — SEAL DOCUMENT
# ============================================================
with tab2:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    st.subheader("📜 Seal Document")

    if not st.session_state.kyc_verified:
        st.warning("Please complete Identity Verification first.")
    else:
        doc = st.text_area("Paste EXACT Document Content", height=200)

        release_date = st.date_input(
            "Release Date (Time Lock)",
            min_value=date.today(),
            value=date(date.today().year + 5, date.today().month, date.today().day)
        )

        if st.button("Seal to Ledger"):
            if not doc.strip():
                st.error("Document cannot be empty.")
            elif release_date <= date.today():
                st.error("Release date must be in the future.")
            else:
                h = sha256_hash(doc)
                st.session_state.ledger[h] = {
                    "seal_date": datetime.now().isoformat(),
                    "signer_id": st.session_state.user_id,
                    "release_date": release_date.isoformat(),
                }

                st.success("Document Sealed Successfully!")

                st.code(h)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# TAB 3 — VERIFY
# ============================================================
with tab3:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    st.subheader("🔍 Verify Sealed Document")

    hash_id = st.text_input("Enter Hash ID")
    verify_doc = st.text_area("Paste Document to Verify", height=200)

    if st.button("Verify Integrity"):
        record = st.session_state.ledger.get(hash_id)

        if not record:
            st.error("❌ Hash not found — forged or incorrect.")
        else:
            release_dt = datetime.strptime(record["release_date"], "%Y-%m-%d")

            if datetime.now() < release_dt:
                st.warning(f"🔒 Time-locked until {release_dt.date()}")
            else:
                if sha256_hash(verify_doc) == hash_id:
                    st.success("🟢 Document Verified — Untampered")
                else:
                    st.error("🔴 Document Changed — Hash Mismatch")

    st.markdown("</div>", unsafe_allow_html=True)
