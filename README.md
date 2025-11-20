# 🔒 Digital Notary  
### A Modern Time-Locked Document Verification System

---

## 🧾 Overview

**Digital Notary** is a secure, premium, Stripe-inspired platform that allows users to seal documents using cryptographic hashing, time-lock them for future verification, and generate password-protected certificates.

It features:

- Identity Verification (KYC)
- SHA-256 document sealing
- Password-protected PDF certificate generation
- Time-lock based release system
- Integrity verification
- A personal profile dashboard
- Modern, animated Stripe-style UI with glassmorphism

---

## 🎯 Why This Project Was Created

This project was built to solve an important challenge:

**“How can someone prove a document existed earlier without exposing the document itself?”**

Digital Notary provides a private, secure, and elegant solution for:

- Predictions
- Inventions or intellectual property
- Digital wills or agreements
- Secure time capsules
- Confidential future reveals
- Timestamped proofs

This app helps users:

- Create cryptographic proof without storing documents online  
- Lock documents until a chosen future date  
- Prove content integrity anytime  
- Generate a PDF certificate for safe storage  

You own your content.  
You control the evidence.  
No files ever leave your device.

---

## 🧩 How It Works

### 1. Identity Verification (KYC)
User enters a name to simulate a verified identity.

### 2. Seal Document
- User enters document text.
- The system creates a **SHA-256 hash** (document fingerprint).
- User sets a future **release date**.
- User receives a **password-protected PDF certificate** (password = hash).
- Document hash + metadata is stored temporarily in session.

### 3. Verify Document
- User enters the hash + the document text.
- System recomputes SHA-256 and validates match.
- Checks if the time-lock (release date) has expired.
- Confirms whether the document is original or tampered.

### 4. Profile
Shows all documents sealed during the session with:
- Hash  
- Signer  
- Seal date  
- Release date  
- Original content (never uploaded to any server)

---

## 👨‍💻 Contributors

| Name | Contribution |
|------|-------------|
| **Chaitanya** | Core idea, UI direction, project vision |
| **Aarsh** | Development support, logical structure |
| **Harsh** | UI improvements, testing, feedback |

Your teamwork made this app premium, functional, and polished.

---

## 🚀 Features

- Animated Stripe gradient background  
- Glassmorphism UI (premium card container)  
- Modern Inter font  
- SHA-256 hashing  
- Time-locked documents  
- Password-protected PDF certificates  
- Identity verification  
- Integrity checking  
- Profile dashboard  
- Fully private (no backend database needed)  

---

## 🛠 Tech Stack

- Python  
- Streamlit  
- PyPDF2  
- SHA-256 cryptographic hashing  
- HTML + CSS for animations and effects  

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/digital-notary.git
cd digital-notary
```

### 2. Install required packages
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

---

## 🌐 Deploying on Streamlit Cloud

1. Push the project to GitHub  
2. Go to: https://share.streamlit.io  
3. Select your repository  
4. Deploy  

The app is fully compatible with Streamlit Community Cloud.

---

## 🛡 Security Notice

- No document data is uploaded or stored externally  
- All text is processed locally in the user session  
- Only cryptographic hashes are used  
- The PDF certificate is protected with SHA-256 hash  
- User must save their certificate (it is not stored)

Digital Notary prioritizes privacy and client-side trust.

---

## ❤️ Support

If you like this project:

- ⭐ Star the repository  
- 🐛 Report bugs  
- 💡 Suggest improvements  
- 🤝 Contribute to the project  

---

