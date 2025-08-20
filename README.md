# Hybrid Finance/Business Auto-Poster (Complete Package)

This is a full, ready-to-run hybrid bot that **automatically** posts one faceless finance/business YouTube Short per day.
It alternates between **evergreen tips** and **current news**, creates a vertical video (TTS + captions + background), generates a thumbnail, and uploads to YouTube.

## One-time setup (10-20 minutes)
1. Create a **public GitHub repository** and push this project (upload the unzipped files).
2. In Google Cloud Console:
   - Enable **YouTube Data API v3** for a project.
   - Create **OAuth Client ID** (Desktop App). Save the Client ID & Client Secret.
3. On your local machine, run the helper to obtain a **refresh token**:
   ```bash
   python tools/get_refresh_token.py
   ```
   Sign in to the YouTube account you want to upload from and copy the printed refresh token.
4. In your GitHub repo → **Settings → Secrets and variables → Actions** add these secrets:
   - `YT_CLIENT_ID`
   - `YT_CLIENT_SECRET`
   - `YT_REFRESH_TOKEN`
   - (optional) `PEXELS_API_KEY` for nicer b-roll
   - (optional) `AFFILIATE_LINK` to append to descriptions
5. Workflow will run daily at 09:00 UTC by default. Change the cron in `.github/workflows/publish.yml` if needed.

## Local testing
Install dependencies and system tools:
- Python 3.11+
- ffmpeg and espeak-ng (macOS: `brew install ffmpeg espeak`; Ubuntu: `sudo apt-get install -y ffmpeg espeak-ng`)

Then run:
```bash
pip install -r requirements.txt
python main.py   # creates assets in ./out and uploads if env secrets set
```

## Files
- main.py - local orchestrator
- scripts/generate_content.py - builds script, TTS, captions, video, thumbnail, metadata
- scripts/upload_to_youtube.py - uploads using refresh token
- scripts/utils.py - helper functions for media creation
- scripts/sources.py - news feeds & evergreen loader
- tools/get_refresh_token.py - helper to get refresh token locally
- data/evergreen.csv - evergreen tips
- .github/workflows/publish.yml - Action to run daily

---
Make sure to respect platform policies and avoid repeated spammy content. This tool is provided as-is; customize responsibly.
