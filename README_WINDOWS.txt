AUTOPOST AI STARTER — WINDOWS SETUP

What this starter can do:
- Upload and preview ordinary MP4/MOV/WebM videos
- Prepare captions and hashtags
- Generate a basic topic-based script and storyboard (template-based, not a paid AI API)
- Prepare a simple publishing checklist

Not included yet:
- Realistic AI motion video generation
- Public user accounts / multi-user storage
- Automatic publishing to TikTok, YouTube, or Facebook
These need additional services, official API permissions, and may have free-tier limits or costs.

RUN ON WINDOWS
1. Install Python 3.11 or newer: https://www.python.org/downloads/
   During setup, tick "Add Python to PATH".
2. Extract AUTOPOST_AI_STARTER.zip.
3. Open the extracted folder.
4. Click the File Explorer address bar, type cmd, press Enter.
5. Run these commands one at a time:

   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py

6. Open http://localhost:8501 if it does not open automatically.
7. Stop the app with Ctrl+C in the command window.

PUBLIC WEBSITE
This folder is a starter project, not a live public website yet.
To make it public, the project must be uploaded to a code host and deployed to a hosting provider.
A free hosting tier can be used for a small demo, but it has limits and may sleep or restrict storage/CPU.
Do not upload private videos or sensitive account information to a public demo.

IMPORTANT
No service can honestly promise unlimited AI motion-video generation and unlimited social auto-posting for $0.
Build the public upload/editor first, then add each official publishing integration after account authorization and API review.
