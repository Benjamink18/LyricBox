# YouTube Cookies Setup

## Why This Is Needed
YouTube is blocking transcript requests from your IP (even with VPN). Using browser cookies bypasses this.

## Quick Setup (2 minutes)

### Step 1: Install Browser Extension
**Chrome/Brave:**
https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

**Firefox:**
https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

### Step 2: Export Cookies
1. Go to https://www.youtube.com (logged in)
2. Click extension icon
3. Click "Export"
4. Save as: `/Users/benkohn/Desktop/LyricBox/backend/youtube_cookies.txt`

### Step 3: Restart & Test
The scraper will automatically use the cookies file!

## Security
⚠️ Don't share or commit the cookies file (already in .gitignore)
