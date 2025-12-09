import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import os

# ======================================================================
# Database Setup
# ======================================================================
DB = "ledger.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            hash TEXT PRIMARY KEY,
            content TEXT,
            signer TEXT,
            seal_date TEXT,
            release_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_document(hash_id, content, signer, seal_date, release_date):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documents (hash, content, signer, seal_date, release_date)
        VALUES (?, ?, ?, ?, ?)
    """, (hash_id, content, signer, seal_date, release_date))
    conn.commit()
    conn.close()

def fetch_document(hash_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE hash=?", (hash_id,))
    data = cur.fetchone()
    conn.close()
    return data

# ======================================================================
# Hash Helper
# ======================================================================
def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# ======================================================================
# Internal PDF Generator (NO external libraries)
# ======================================================================
def generate_pdf(text, filename="document.pdf"):
    path = os.path.join(os.getcwd(), filename)

    # Escape parentheses (PDF text rule)
    safe_text = text.replace("(", "\\(").replace(")", "\\)")

    body = f"BT /F1 12 Tf 50 750 Td ({safe_text}) Tj ET"

    pdf = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >>
>>
endobj
4 0 obj
<< /Length {len(body)} >>
stream
{body}
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000061 00000 n 
0000000116 00000 n 
0000000273 00000 n 
0000000460 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
560
%%EOF
"""

    with open(path, "wb") as f:
        f.write(pdf.encode("latin-1"))

    return path

# ======================================================================
# Streamlit App Setup
# ======================================================================
st.set_page_config(page_title="Digital Time Capsule", layout="centered")
init_db()

PAGES = [
    "Home",
    "KYC Verification",
    "Seal Document",
    "Verify Document",
    "Public Lookup"
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("Navigation")
st.session_state.page = st.sidebar.radio("Go to", PAGES)

# ======================================================================
# HOME PAGE
# ======================================================================
if st.session_state.page == "Home":
    st.title("🏛 Digital Time Notary")
    st.write("""
    A simple platform for:
    - KYC Identity Verification  
    - Document Notary + Time Locks  
    - Public Release Ledger  
    """)

# ======================================================================
# KYC PAGE
# ======================================================================
elif st.session_state.page == "KYC Verification":
    st.header("🧑‍💼 KYC Identity Verification")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth")
    country = st.text_input("Country")
    id_number = st.text_input("Govt ID Number")

    if st.button("Verify Identity", key="kyc_verify"):
        if not name or not country or not id_number:
            st.error("All fields required.")
        else:
            st.success("Identity Verified Successfully")
            st.json({
                "name": name,
                "dob": str(dob),
                "country": country,
                "id": id_number
            })

# ======================================================================
# SEAL DOCUMENT PAGE
# ======================================================================
elif st.session_state.page == "Seal Document":
    st.header("📝 Seal a Document")

    signer = st.text_input("Signer Name")
    content = st.text_area("Document Content", height=200)
    release_date = st.date_input("Release Date")

    if st.button("Seal Document", key="seal_doc"):
        if not signer or not content:
            st.error("All fields required.")
        else:
            hash_id = sha256_hash(content)
            seal_dt = datetime.now().isoformat()

            save_document(hash_id, content, signer, seal_dt, str(release_date))

            st.success("Document sealed successfully!")
            st.code(hash_id)

# ======================================================================
# VERIFY DOCUMENT PAGE
# ======================================================================
elif st.session_state.page == "Verify Document":
    st.header("🔎 Verify a Document")

    hash_in = st.text_input("Document Hash")
    doc_text = st.text_area("Paste Original Document (optional)", height=200)

    if st.button("Verify Document", key="verify_document"):
        rec = fetch_document(hash_in)

        if not rec:
            st.error("Hash Not Found")
        else:
            _hash, stored, signer, seal_date, release_date = rec
            release_dt = datetime.fromisoformat(release_date)

            if datetime.now() < release_dt:
                st.warning(f"🔒 Locked until {release_dt.strftime('%B %d, %Y')}")
            else:
                st.success(f"Document Released — Signed by {signer}")

                st.text_area("Stored Document", stored, height=200)

                pdf_path = generate_pdf(stored, f"{hash_in}.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇ Download PDF",
                        f,
                        file_name=f"{hash_in}.pdf",
                        mime="application/pdf"
                    )

                if doc_text.strip():
                    if sha256_hash(doc_text) == hash_in:
                        st.info("✔ Document integrity verified")
                    else:
                        st.error("❌ Document mismatch")

# ======================================================================
# PUBLIC LOOKUP PAGE
# ======================================================================
elif st.session_state.page == "Public Lookup":
    st.header("🌍 Public Document Lookup")

    hash_in = st.text_input("Enter Document Hash")

    if st.button("Search", key="lookup_search"):
        rec = fetch_document(hash_in)

        if not rec:
            st.error("Hash Not Found")
        else:
            _hash, stored, signer, seal_date, release_date = rec
            release_dt = datetime.fromisoformat(release_date)

            if datetime.now() < release_dt:
                st.warning(f"🔒 Locked until {release_dt.strftime('%B %d, %Y')}")
            else:
                st.success(f"Released — Signed by {signer}")

                st.text_area("Document Content", stored, height=200)

                pdf_path = generate_pdf(stored, f"{hash_in}.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇ Download PDF",
                        f,
                        file_name=f"{hash_in}.pdf",
                        mime="application/pdf"
                    )

