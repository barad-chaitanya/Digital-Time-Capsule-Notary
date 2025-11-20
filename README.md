🔒 Digital Notary
A simple, beautiful, and secure way to seal your words, ideas, and memories.
🧾 What is Digital Notary?

Digital Notary is a project built to help people prove that a document existed at a certain moment in time — without storing the document anywhere or exposing its contents.

It lets you:

Verify your identity (simple KYC)

Seal any message or document using SHA-256 hashing

Time-lock it so it can only be verified in the future

Download a password-protected certificate

Check authenticity later

View everything you’ve sealed in a clean profile dashboard

Everything happens on your device, nothing is uploaded, and the app uses a simple, premium Stripe-inspired UI with animated gradients and glass effects.



🎯 Why I Created This

I built Digital Notary because I wanted something:

Private

Simple

And actually useful

Something that lets you prove your words today, for tomorrow, without handing over your personal thoughts to a server or a big company.

Maybe you want to record:

A prediction

A promise

An idea you don’t want stolen

A personal note

A message for your future self

Something only you should reveal later

I wanted a tool that makes this easy, secure, and beautiful to use.

So I built one.



🧩 How It Works (Simple Version)
1. You verify your name

Just a quick KYC name field — no real identity checks.

2. You write a document

Could be anything: a secret, a memory, an idea, a promise.

3. The app creates a SHA-256 hash

This is like a fingerprint of your document —
unique, permanent, and impossible to fake.

4. You pick a release date

Until then, your document stays “time-locked.”

5. You get a certificate

A PDF file that is protected using your document’s hash as the password.

6. Later, you verify it

Paste the original text again and the app will confirm if it’s a perfect match.

7. Everything stays on your device

No servers, no databases, no leakable files.



👨‍💻 The People Behind This Project

A project feels empty without people.
So here’s everyone who contributed to building it:

Chaitanya

Core idea, design direction, vision of how the UI and experience should feel.

Aarsh

Helped shape the logic, fixed issues, and improved the core workflow.

Harsh

Improved UI details, tested features, and made the experience smoother.

This project exists because of everyone above — their ideas, time, and effort.



🚀 Features

Stripe-like animated gradient background

Glassmorphism premium UI

Clean Inter font

KYC (simple name verification)

SHA-256 document sealing

Time-lock system

Password-protected PDF certificates

Integrity verification

Profile dashboard

Fully private — nothing stored online



🛠 Tech It Uses

Python

Streamlit

PyPDF2

SHA-256 hashing

Custom HTML/CSS for animations



📦 How to Install

Clone the project

git clone https://github.com/yourusername/digital-notary.git
cd digital-notary


Install dependencies

pip install -r requirements.txt


Run the app

streamlit run app.py



🌐 Deploying on Streamlit Cloud

It works perfectly on Streamlit’s free hosting.

Just push it to GitHub
→ Connect it on Streamlit Cloud
→ Deploy
→ Done.



🛡 Privacy & Safety

This app does not save:

Your documents

Your certificates

Your hash

Your identity

Anything to any database

Everything lives inside your session only, and you download your own certificate.
You own all your data.



❤️ Want to Support?

If you find this tool useful or inspiring:

Give it a ⭐ on GitHub

Report bugs

Suggest ideas

Or contribute

It’s a small project but built with a lot of thought and care.
