import streamlit as st
import hashlib
from datetime import datetime, date
from PyPDF2 import PdfWriter
import io

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Digital Notary",
    layout="centered",
)

# ---------------------- ANIMATED GRADIENT BG ----------------------
st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    margin: 0;
    padding: 0;
}

/* ANIMATED STRIPE GRADIENT */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #ff0080, #7928ca, #2d2dfc);
    background-size: 300% 300%;
    animation: gradientMove 12s ease infinite;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* CENTER THE MAIN CARD */
.block-container {
    max-width: 650px;
    margin: auto;
    padding-top: 2rem;
}

/* GLASS CARD */
.glass-card {
    background: rgba(255,255,255,0.13);
    border-radius: 22px;
    padding: 30px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
}

/* STRIPE STYLE BUTTON */
.stButton>button {
    background-color: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.8);
    color: white !important;
    padding: 0.65rem 1.3rem;
    border-radius: 14px;
    font-weight: 600;
    transition: 0.25s;
    backdrop-filter: blur(10px);
}

.stButton>button:hover {
    background-color: rgba(255,255,255,0.25);
    transform: scale(1.06);
    box-shadow: 0 0 20px rgba(255,255,255,0.7);
}

/* CUSTOM FONT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

html, body, [data-testid="stAppViewContainer"] * {
    font-family: 'Inter', sans-serif !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------- SESSION STATE ----------------------
if "kyc_verified" not in st.session_state:
    st.session_state.kyc_verified = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "ledger" not in st.session_state:
    st.session_state.ledger = {}

# ---------------------- APP TITLE ----------------------
st.markdown("<h1 style='text-align:center;color:white;'>Digital Notary</h1>", unsafe_allow_html=True)

# ---------------------- MAIN CARD ----------------------
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    tabs = st.tabs(["KYC", "Seal Document", "Verify", "Profile"])

    # -----------------------------------------------------
    # TAB 1 — KYC
    # -----------------------------------------------------
    with tabs[0]:
        st.subheader("Identity Verification")

        user = st.text_input("Enter Your Name")

        if st.button("Verify Identity"):
            if user.strip():
                st.session_state.kyc_verified = True
                st.session_state.user_id = user
                st.success("Identity verified successfully!")
            else:
                st.error("Please enter a valid name.")

    # -----------------------------------------------------
    # TAB 2 — SEAL DOCUMENT
    # -----------------------------------------------------
    with tabs[1]:
        st.subheader("Seal a Document")

        if not st.session_state.kyc_verified:
            st.warning("Complete KYC first.")
        else:
            text = st.text_area("Document Content")

            release_date = st.date_input(
                "Release Date",
                min_value=date.today(),
                value=date(date.today().year + 1, date.today().month, date.today().day)
            )

            if st.button("Seal Document"):
                if not text.strip():
                    st.error("Document cannot be empty.")
                else:
                    doc_hash = hashlib.sha256(text.encode()).hexdigest()

                    st.session_state.ledger[doc_hash] = {
                        "text": text,
                        "signer": st.session_state.user_id,
                        "sealed_on": datetime.now().isoformat(),
                        "release_date": release_date.isoformat()
                    }

                    st.success("Document sealed!")

                    # Generate password-protected PDF
                    pdf_buffer = io.BytesIO()
                    writer = PdfWriter()

                    # Create empty PDF
                    writer.add_blank_page(width=300, height=300)

                    # Apply password = hash
                    writer.encrypt(doc_hash)

                    writer.write(pdf_buffer)
                    pdf_buffer.seek(0)

                    st.download_button(
                        "Download Certificate (PDF)",
                        data=pdf_buffer,
                        file_name="seal_certificate.pdf",
                        mime="application/pdf"
                    )

                    st.info(f"Document Hash (Password): {doc_hash}")

    # -----------------------------------------------------
    # TAB 3 — VERIFY
    # -----------------------------------------------------
    with tabs[2]:
        st.subheader("Verify Document Integrity")

        v_hash = st.text_input("Enter Hash")
        v_text = st.text_area("Paste Document")

        if st.button("Verify"):
            if v_hash in st.session_state.ledger:
                stored = st.session_state.ledger[v_hash]

                if hashlib.sha256(v_text.encode()).hexdigest() == v_hash:
                    if datetime.now() >= datetime.fromisoformat(stored["release_date"]):
                        st.success("Document is valid and released!")
                    else:
                        st.warning("Document is valid but still locked.")
                else:
                    st.error("Content does NOT match the hash.")
            else:
                st.error("Hash not found.")

    # -----------------------------------------------------
    # TAB 4 — PROFILE
    # -----------------------------------------------------
    with tabs[3]:
        st.subheader("Your Sealed Documents")

        if not st.session_state.ledger:
            st.info("You haven't sealed any documents yet.")
        else:
            for h, d in st.session_state.ledger.items():
                with st.expander(f"Document Hash: {h[:12]}..."):
                    st.write(f"**Signed by:** {d['signer']}")
                    st.write(f"**Sealed on:** {d['sealed_on']}")
                    st.write(f"**Release date:** {d['release_date']}")
                    st.code(d["text"])

    st.markdown("</div>", unsafe_allow_html=True)
