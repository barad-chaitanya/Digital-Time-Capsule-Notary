import streamlit as st
import hashlib
from datetime import datetime, date

# --- 1. INITIAL SETUP AND LEDGER (SIMULATED BLOCKCHAIN) ---
# Initialize the ledger and KYC status in Streamlit's session state
if 'ledger' not in st.session_state:
    st.session_state.ledger = {}
if 'kyc_verified' not in st.session_state:
    st.session_state.kyc_verified = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = "UNKNOWN"

# Set a clean page title (for a better URL look on deployment) and layout
st.set_page_config(
    layout="centered", 
    page_title="Time Capsule Notary | Digital Proof",
    initial_sidebar_state="collapsed"
)

# --- 2. HASHING LOGIC (CORE CRYPTOGRAPHY) ---
def sha256_hash(data: str) -> str:
    """Generates a SHA-256 cryptographic hash of the input string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# --- 3. UI LAYOUT ---
st.title("🔒 Digital Time Capsule Notary")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["👤 KYC Setup (Dummy)", "📜 Seal Document", "🔍 Verify Integrity"])

# --- TAB 1: DUMMY KYC SETUP ---
with tab1:
    st.header("Step 1: Identity Verification (Dummy KYC)")
    st.markdown(
        """
        In a real blockchain notary, this step would involve a trusted third party (an Identity Oracle) 
        verifying your government ID and issuing an **Identity Token** to your wallet. 
        
        For this simulation, just enter your name/ID to gain **Verified** status.
        """
    )
    
    status_emoji = '✅' if st.session_state.kyc_verified else '❌'
    status_text = 'VERIFIED' if st.session_state.kyc_verified else 'UNVERIFIED'
    st.info(f"Current Verification Status: **{status_emoji} {status_text}**")

    # Dummy KYC Input
    user_name = st.text_input(
        "Enter your Name or Unique ID", 
        value=st.session_state.user_id if st.session_state.user_id != "UNKNOWN" else "Alice Johnson", 
        key="kyc_name_input",
        disabled=st.session_state.kyc_verified # Disable input after verification
    )
    
    # Added key for robustness and disabled button after verification
    if st.button("Simulate KYC Verification", key="kyc_verify_btn", disabled=st.session_state.kyc_verified):
        if user_name.strip():
            st.session_state.kyc_verified = True
            st.session_state.user_id = user_name.strip()
            st.success(f"✅ Success! Identity '{user_name.strip()}' is now digitally verified and linked to your session. Proceed to Seal Document.")
            # st.experimental_rerun() is kept for immediate state update/UI switch
            st.experimental_rerun() 
        else:
            st.error("Please enter a name or ID to simulate verification.")

# --- TAB 2: SEAL DOCUMENT ---
with tab2:
    st.header("Step 2: Seal Document (The Present)")
    if not st.session_state.kyc_verified:
        st.warning("Please complete the Dummy KYC Setup first to link your identity to the seal.")
    else:
        st.info(f"Sealing as verified user: **{st.session_state.user_id}**")

        document_text = st.text_area(
            "Paste the EXACT document content you want to seal (e.g., A Prediction, A Private Will)",
            height=200,
            key="seal_text_area",
            placeholder="I, [User ID], hereby predict that flying cars will be common by 2045."
        )

        release_date = st.date_input(
            "Time-Lock Release Date",
            min_value=date.today(),
            value=date(date.today().year + 10, date.today().month, date.today().day)
        )
        st.caption("Verification will only pass *on or after* this future date.")

        if st.button("Generate Hash & Seal to Ledger", disabled=not st.session_state.kyc_verified):
            if not document_text.strip():
                st.error("Document content cannot be empty.")
            elif release_date <= date.today():
                st.error("The release date must be in the future to act as a time-lock.")
            else:
                # Calculate the unique cryptographic fingerprint
                document_hash = sha256_hash(document_text)
                
                # Store the permanent record in the simulated ledger
                st.session_state.ledger[document_hash] = {
                    "release_date": release_date.isoformat(),
                    "seal_date": datetime.now().isoformat(),
                    "signer_id": st.session_state.user_id,
                }
                
                st.success("✅ Document Successfully Sealed!")
                st.markdown(f"""
                    ### 📜 Sealed Certificate
                    - **Permanent Hash ID (The Fingerprint):** <code style='word-break: break-all;'>{document_hash}</code>
                    - **Sealed By:** {st.session_state.user_id}
                    - **Release Date:** {release_date.strftime("%B %d, %Y")}
                    
                    **🔑 Copy this Hash ID and save your original document text for future verification!**
                """, unsafe_allow_html=True)
                
# --- TAB 3: VERIFY INTEGRITY ---
with tab3:
    st.header("Step 3: Verify Integrity (The Future)")
    
    st.markdown("Use this panel to prove that a document you possess is the **exact, unedited original** sealed on the ledger.")
    
    verify_hash_id = st.text_input("1. Paste the Original Notarized Hash ID", key="verify_hash_id")
    
    verify_document_text = st.text_area(
        "2. Paste the Document Text You Want to Check",
        height=200,
        key="verify_text_area",
        placeholder="Paste the content of the document you want to verify here."
    )
    
    if st.button("Verify Document Hash & Time-Lock"):
        if not verify_hash_id or not verify_document_text:
            st.error("Please provide both the Hash ID and the document text to check.")
        else:
            stored_record = st.session_state.ledger.get(verify_hash_id)
            
            if not stored_record:
                st.error(f"🔴 Verification Failed: Hash ID **{verify_hash_id[:10]}...** was not found on the permanent ledger (Forged ID).")
            else:
                # --- TIME-LOCK CHECK (STEP 7) ---
                release_date_dt = datetime.strptime(stored_record['release_date'], '%Y-%m-%d')
                
                if datetime.now() < release_date_dt:
                    st.warning(f"🔒 Verification Locked! The time-lock for this document is still active.")
                    st.info(f"Cannot verify content until the release date: **{release_date_dt.strftime('%B %d, %Y')}**")
                else:
                    # --- INTEGRITY CHECK (STEP 6) ---
                    current_hash = sha256_hash(verify_document_text)
                    
                    if current_hash == verify_hash_id:
                        st.success(f"""
                            ### 🟢 SUCCESS: Document Integrity Verified!
                            The content matches the exact document sealed by **{stored_record['signer_id']}** on {datetime.strptime(stored_record['seal_date'].split('.')[0], '%Y-%m-%dT%H:%M:%S').strftime('%B %d, %Y at %I:%M %p')}.
                            
                            The Digital Notary confirms the content is 100% original and unchanged since the sealing date.
                        """)
                    else:
                        st.error(f"""
                            ### 🔴 FAILED: Document Tampered/Altered!
                            The document's current fingerprint does not match the sealed record.
                            - Original Hash: `{verify_hash_id[:15]}...`
                            - Current Hash: `{current_hash[:15]}...`
                            
                            **Even a single character change invalidates the seal.**
                        """)
