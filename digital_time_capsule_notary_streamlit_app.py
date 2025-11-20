# app.py — Digital Notary (Stripe-gradient + Outline Buttons + Encrypted PDF certificates)
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date
from typing import Optional, List, Tuple
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import io

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
# Utilities
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
    c.execute("SELECT hash, content, user, seal_date, release_date FROM documents WHERE hash=?", (hash_val,))
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
# Session defaults
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = "Guest"
if "kyc_done" not in st.session_state:
    st.session_state.kyc_done = False
if "page" not in st.session_state:
    st.session_state.page = "KYC"

# ---------------------------
# CSS / Header (Stripe gradient + outline buttons)
# ---------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Full app gradient background */
    body {
        background: linear-gradient(135deg, #0A0F2D 0%, #3B2DFD 50%, #D96FFF 100%) !important;
    }

    .hero {
        padding: 28px 18px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 18px;
    }

    .card {
        background: rgba(255,255,255,0.96);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 8px 28px rgba(8,10,20,0.06);
        border: 1px solid rgba(16,24,40,0.03);
        transition: transform 200ms ease, box-shadow 200ms ease;
        color: #041227;
    }
    .card:hover { transform: translateY(-6px); box-shadow: 0 18px 48px rgba(8,10,20,0.10); }

    .nav-row { display:flex; justify-content:center; gap:10px; margin: 12px 0 18px 0; }

    /* Outline (transparent) buttons with white border for nav */
    .stButton>button {
        background: transparent !important;
        color: white !important;
        padding: 10px 18px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.85) !important;
        font-weight: 600 !important;
        transition: transform 0.15s ease, background 0.15s ease !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12) !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        background: rgba(255,255,255,0.06) !important;
    }

    /* Small muted text */
    .muted { color: rgba(4,18,39,0.6); font-size:13px; }

    pre.code {
        background: #0b1220;
        color: #e6f2ff;
        padding: 10px;
        border-radius: 8px;
        overflow-x: auto;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# header hero (uses white text on gradient background)
st.markdown(
    """
    <div class="hero">
        <h1 style="margin:0">Digital Notary</h1>
        <p style="margin:6px 0 0 0;">Seal • Time-lock • Verify — premium notarized certificates</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Top nav (five outline buttons)
# ---------------------------
st.markdown("<div class='nav-row'>", unsafe_allow_html=True)
cols = st.columns(5)
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
# PDF certificate creation (FPDF) + encrypt with pypdf
# ---------------------------
def create_certificate_pdf_bytes(hash_val: str, content: str, user: str, seal_date: str, release_date: str) -> bytes:
    """
    Create a PDF certificate (in memory) using fpdf, then encrypt it with pypdf using hash_val as password.
    Returns encrypted PDF bytes.
    """
    # 1) Generate plain PDF with fpdf
    # Use A4-like size in points - fpdf default unit=pt works with those values if using format="A4"
    pdf = FPDF(orientation="P", unit="pt", format="A4")
    pdf.set_auto_page_break(auto=True, margin=40)
    pdf.add_page()

    # Header band
    w, h = 595.28, 841.89  # A4 points
    pdf.set_fill_color(59,45,253)  # deep purple tone
    pdf.rect(0, 0, w, 120, 'F')
    pdf.set_xy(40, 40)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.cell(0, 10, "Digital Notary — Sealed Certificate", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.ln(6)
    pdf.set_text_color(255,255,255)
    pdf.cell(0, 10, "Premium notarized certificate", ln=True)

    # Body
    pdf.set_text_color(10,10,10)
    pdf.ln(22)
    pdf.set_x(40)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 16, f"Sealed By: {user}")
    pdf.multi_cell(0, 16, f"Seal Date: {seal_date}")
    pdf.multi_cell(0, 16, f"Release Date: {release_date}")
    pdf.ln(8)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 14, "Document SHA-256 Fingerprint:")
    pdf.ln(6)
    pdf.set_font("Courier", size=9)
    for i in range(0, len(hash_val), 64):
        pdf.cell(0, 12, hash_val[i:i+64], ln=True)

    pdf.ln(12)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 14, "Document Preview")
    pdf.ln(6)
    pdf.set_font("Helvetica", size=10)
    preview = content.strip()
    if len(preview) > 1000:
        preview = preview[:1000] + "..."
    pdf.multi_cell(0, 12, preview)

    pdf.set_y(h - 120)
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 10, "Digital Notary • This certificate is electronically generated.", ln=True)

    # Get PDF bytes from fpdf
    pdf_bytes_str = pdf.output(dest='S')  # returns str in fpdf2
    if isinstance(pdf_bytes_str, str):
        pdf_bytes = pdf_bytes_str.encode('latin-1')
    else:
        pdf_bytes = pdf_bytes_str

    # 2) Encrypt with pypdf
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    # encrypt using hash as both user and owner password (user must enter to open)
    writer.encrypt(user_password=hash_val, owner_password=hash_val, use_128bit=True)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.read()

# ---------------------------
# Render card helper
# ---------------------------
def render_card(title: str, fn):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if title:
        st.subheader(title)
    fn()
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

# ---------------------------
# Pages
# ---------------------------

# KYC
if st.session_state.page == "KYC":
    def kyc_fn():
        st.write("Verify your identity (simple demo KYC).")
        name = st.text_input("Full name", value=st.session_state.user, key="kyc_name")
        if st.button("Verify Identity", key="kyc_verify"):
            if name.strip():
                st.session_state.user = name.strip()
                st.session_state.kyc_done = True
                st.success(f"Identity verified: {st.session_state.user}")
            else:
                st.error("Enter a valid name.")
        if st.session_state.get("kyc_done"):
            st.info(f"Verified user: **{st.session_state.user}**")
    render_card("🪪 Identity Verification (KYC)", kyc_fn)

# Home
elif st.session_state.page == "Home":
    def home_fn():
        st.write("Recent sealed documents (latest first).")
        rows = list_recent(6)
        if not rows:
            st.info("No sealed documents yet.")
        else:
            for h, user, seal_date, release_date in rows:
                st.markdown("<div class='card' style='padding:12px; margin-bottom:10px;'>", unsafe_allow_html=True)
                st.write(f"**Hash:** `{h[:32]}...`")
                st.write(f"Sealed by **{user}** on {datetime.fromisoformat(seal_date).strftime('%b %d, %Y')}")
                st.write(f"<span class='muted'>Release: {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    render_card("🏠 Recent Seals", home_fn)

# Seal
elif st.session_state.page == "Seal":
    def seal_fn():
        if not st.session_state.get("kyc_done", False):
            st.warning("Please complete KYC before sealing documents.")
            return
        content = st.text_area("Paste the exact document text to seal", height=220, key="seal_text")
        release = st.date_input("Release (unlock) date", min_value=date.today(), key="seal_release")
        if st.button("Generate Hash & Seal", key="do_seal"):
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
                st.markdown(f"<pre class='muted'>{h}</pre>", unsafe_allow_html=True)
    render_card("🔏 Seal Document", seal_fn)

# Verify
elif st.session_state.page == "Verify":
    def verify_fn():
        st.write("Provide the notarized hash and the original text to verify integrity.")
        hash_in = st.text_input("Notarized Hash ID", key="verify_hash")
        doc_text = st.text_area("Paste Document Text", height=200, key="verify_text")
        if st.button("Verify Document", key="verify_btn"):
            if not hash_in or not doc_text:
                st.error("Provide both Hash ID and document text.")
                return
            rec = fetch_document(hash_in)
            if not rec:
                st.error("Hash not found in ledger.")
                return
            _hash, stored_content, signer, seal_date, release_date = rec
            # time-lock check
            try:
                rel_dt = datetime.fromisoformat(release_date)
            except Exception:
                st.error("Stored release date format error.")
                return
            if datetime.now() < rel_dt:
                st.warning(f"🔒 Time-lock active until {rel_dt.strftime('%B %d, %Y')}")
                return
            # integrity check
            cur_h = sha256_hash(doc_text)
            if cur_h == hash_in:
                st.success(f"🟢 VERIFIED — sealed by **{signer}** on {datetime.fromisoformat(seal_date).strftime('%b %d, %Y %I:%M %p')}")
            else:
                st.error("🔴 FAILED — Document content does not match the sealed fingerprint.")
    render_card("🔎 Verify Document", verify_fn)

# Profile
elif st.session_state.page == "Profile":
    def profile_fn():
        if not st.session_state.get("kyc_done", False):
            st.warning("Complete KYC to view your documents.")
            return
        user = st.session_state.user
        docs = fetch_user_docs(user)
        if not docs:
            st.info("You have not sealed any documents yet.")
            return
        st.write(f"Showing {len(docs)} sealed document(s) for **{user}**.")
        for h, seal_date, release_date, content in docs:
            st.markdown("<div style='padding:12px;border-radius:8px;margin-bottom:12px;background:rgba(255,255,255,0.96)'>", unsafe_allow_html=True)
            st.write(f"**Hash:** `{h}`")
            st.write(f"Sealed on: {datetime.fromisoformat(seal_date).strftime('%b %d, %Y %I:%M %p')}")
            st.write(f"Release date: {datetime.fromisoformat(release_date).strftime('%b %d, %Y')}")
            try:
                locked = datetime.now() < datetime.fromisoformat(release_date)
            except Exception:
                locked = False
            if locked:
                st.info("⏳ This document is still locked — content will be visible after the release date.")
            else:
                if st.checkbox(f"Show content ({h[:10]}...)", key=f"show_{h[:10]}"):
                    st.text_area("Original Document", content, height=180)
                    # PDF download generation
                    if st.button(f"Download Certificate ({h[:10]})", key=f"cert_{h[:10]}"):
                        pdf_bytes = create_certificate_pdf_bytes(h, content, user, seal_date, release_date)
                        st.download_button(
                            label="Download Encrypted PDF Certificate (password = hash)",
                            data=pdf_bytes,
                            file_name=f"certificate_{h[:10]}.pdf",
                            mime="application/pdf"
                        )
            st.markdown("</div>", unsafe_allow_html=True)
    render_card("👤 Profile — Your Sealed Documents", profile_fn)

# Footer
st.write("")
st.markdown("<div class='muted' style='text-align:center;'>© {year} Digital Notary</div>".format(year=datetime.now().year), unsafe_allow_html=True)
