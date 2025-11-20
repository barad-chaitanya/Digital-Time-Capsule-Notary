import streamlit as st
import hashlib
from datetime import datetime, date
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfdoc import StandardEncryption
import io

# ------------------ DATABASE SETUP ------------------
def init_db():
    conn = sqlite3.connect('notary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                    hash TEXT PRIMARY KEY,
                    user TEXT,
                    content TEXT,
                    seal_date TEXT,
                    release_date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ------------------ HASH FUNCTION ------------------
def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# ------------------ PDF GENERATOR ------------------
def generate_seal_certificate(hash_val, content, user, seal_date, release_date):
    buffer = io.BytesIO()
    encrypt = StandardEncryption(userPassword=hash_val, ownerPassword=hash_val, canPrint=0)
    c = canvas.Canvas(buffer, pagesize=A4, encrypt=encrypt)

    width, height = A4

    # Gradient background
    for i in range(0, 100):
        shade = 0.02 * i
        c.setFillColor(Color(0.1 + shade, 0.0 + shade/3, 0.4 + shade/2))
        c.rect(0, i * (height/100), width, height/100, stroke=0, fill=1)

    # Certificate header
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, height - 80, "Digital Notary — Seal Certificate")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 130, f"Sealed By: {user}")
    c.drawString(50, height - 150, f"Seal Date: {seal_date}")
    c.drawString(50, height - 170, f"Release Date: {release_date}")

    # Hash fingerprint
    c.drawString(50, height - 200, "Document SHA-256 Fingerprint:")
    text_obj = c.beginText(50, height - 220)
    text_obj.setFont("Helvetica", 10)
    text_obj.textLines(hash_val)
    c.drawText(text_obj)

    # Content preview
    preview = content[:500] + ("..." if len(content) > 500 else "")
    text_obj2 = c.beginText(50, height - 300)
    text_obj2.setFont("Helvetica", 10)
    text_obj2.textLines("Document Preview:")
    text_obj2.textLines(preview)
    c.drawText(text_obj2)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ------------------ UI STYLING ------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0b1224 0%, #121b38 40%, #1e114a 100%) !important;
    font-family: 'Inter', sans-serif !important;
}

.gradient-header {
    background: linear-gradient(135deg, #0A0E27 0%, #4F3DFE 50%, #A86CFF 100%);
    padding: 40px;
    border-radius: 18px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin-bottom: 30px;
}

.card {
    background: rgba(255, 255, 255, 0.15);
    padding: 22px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0px 5px 25px rgba(0,0,0,0.25);
    transition: 0.25s ease;
    margin-bottom: 20px;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0px 15px 40px rgba(0,0,0,0.45);
}

.stButton>button {
    background: rgba(255,255,255,0.2) !important;
    color: white !important;
    padding: 12px 26px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    backdrop-filter: blur(6px);
    transition: 0.25s ease !important;
    font-size: 16px !important;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.3) !important;
}

.stButton>button:hover {
    transform: translateY(-4px);
    box-shadow: 0px 12px 30px rgba(0,0,0,0.5) !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("""
<div class='gradient-header'>
    <h1>Digital Notary</h1>
    <p>Premium Document Sealing, Verification & Certification</p>
</div>
""", unsafe_allow_html=True)

# ------------------ BUTTON NAVIGATION ------------------
page = st.radio(
    "Navigation",
    ["KYC", "Seal Document", "Verify Document", "Your Documents"],
    horizontal=True
)

# ------------------ PAGE 1: KYC ------------------
if page == "KYC":
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("🔹 KYC Verification")
    name = st.text_input("Enter Your Full Name")
    kyc_btn = st.button("Verify Identity")

    if kyc_btn and name.strip():
        st.session_state['user'] = name
        st.success("Identity Verified Successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ PAGE 2: SEAL DOCUMENT ------------------
if page == "Seal Document":
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("🔒 Seal a New Document")

    if 'user' not in st.session_state:
        st.warning("Complete KYC first!")
    else:
        text = st.text_area("Document Content", height=200)
        release_date = st.date_input("Release Date", min_value=date.today())

        if st.button("Seal Document"):
            h = sha256_hash(text)
            seal_date = datetime.now().isoformat()

            conn = sqlite3.connect('notary.db')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?, ?)",
                      (h, st.session_state['user'], text, seal_date, release_date.isoformat()))
            conn.commit()
            conn.close()

            st.success(f"Document sealed successfully! Hash: {h}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ PAGE 3: VERIFY DOCUMENT ------------------
if page == "Verify Document":
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("🔍 Verify Document Integrity")
    hash_input = st.text_input("Enter Hash ID")
    doc_input = st.text_area("Paste Document Content", height=180)

    if st.button("Verify"):
        current = sha256_hash(doc_input)
        if current == hash_input:
            st.success("Document is authentic!")
        else:
            st.error("Document does not match the original.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ PAGE 4: PROFILE ------------------
if page == "Your Documents":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📁 Your Sealed Documents")

    conn = sqlite3.connect('notary.db')
    c = conn.cursor()
    c.execute("SELECT * FROM documents")
    rows = c.fetchall()
    conn.close()

    for h, user, content, seal_date, release_date in rows:
        st.markdown(f"### 🔖 Document Hash: {h[:12]}...")
        st.write(f"Sealed By: {user}")
        st.write(f"Seal Date: {seal_date}")
        st.write(f"Release Date: {release_date}")

        if st.checkbox(f"Show Document ({h[:10]}...)"):
            st.text_area("Document Content", content, height=180)

            if st.button(f"Download Certificate ({h[:10]})"):
                pdf = generate_seal_certificate(h, content, user, seal_date, release_date)
                st.download_button("Download PDF Certificate", pdf, file_name=f"certificate_{h[:10]}.pdf", mime="application/pdf")

    st.markdown("</div>", unsafe_allow_html=True)
    
