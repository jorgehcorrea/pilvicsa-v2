# Pilvicsa Website Rebuild — Setup Instructions
**For Jorge | Account: pilvicsaec@gmail.com**

Complete these steps before handing the brief to Claude Code. Each step has a checkbox. Takes approximately 45-60 minutes total.

---

## STEP 1 — Node.js and npm
*Required for Tailwind CSS build and image optimization script*

1. Go to `https://nodejs.org`
2. Download the **LTS** version (currently v20+)
3. Install it — accept all defaults
4. Verify installation by opening a terminal and running:
   ```
   node --version
   npm --version
   ```
   Both should return version numbers.

---

## STEP 2 — Python
*Required for the Google Sheets fetch script*

1. Go to `https://python.org/downloads`
2. Download Python 3.11 or newer
3. Install — **check "Add Python to PATH"** during installation
4. Verify:
   ```
   python --version
   pip --version
   ```

---

## STEP 3 — Install project dependencies

Open a terminal inside your `pilvicsa` repo folder and run these one by one:

```bash
# Install Tailwind CSS
npm install tailwindcss --save-dev

# Install Flowbite (Tailwind plugin)
npm install flowbite --save-dev

# Install Sharp (image optimizer)
npm install sharp

# Install Python requests library
pip install requests
```

Verify Sharp installed:
```bash
node -e "require('sharp'); console.log('Sharp OK')"
```

---

## STEP 4 — Google Sheets setup
*This is where you manage all products — no coding needed to add/remove varieties*

### 4a. Create the products spreadsheet
1. Go to `https://sheets.google.com` logged in as `pilvicsaec@gmail.com`
2. Create a new spreadsheet named `Pilvicsa — Catálogo de Productos`
3. In **Row 1**, type these exact column headers (one per cell, A through S):
   ```
   id | nombre | latin | categoria | pagina | pageLabel | color | forma | sistema | densidad | resistencias | ciclo | tamano | imagen | youtube_id | fb_video_id | ig_post_id | estado | nota
   ```
4. Copy all 221 products from the current `pilvicsa-data.js` into this sheet — Claude Code can help convert the format if needed

### 4b. Publish the sheet as CSV
1. In Google Sheets: **File → Share → Publish to web**
2. Under "Link" tab, select the sheet tab name and choose **Comma-separated values (.csv)**
3. Click **Publish**
4. Copy the URL that appears — it looks like:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&...
   ```
5. **Save this URL** — you will paste it into `scripts/fetch_sheet.py` where it says `REPLACE_WITH_PUBLISHED_CSV_URL`

### 4c. Note your Sheet ID
The Sheet ID is the long string in the URL between `/d/` and `/edit`:
```
https://docs.google.com/spreadsheets/d/THIS_IS_THE_SHEET_ID/edit
```
**Write it here:** ________________________________

---

## STEP 5 — Facebook oEmbed setup
*Required to embed Facebook videos in product modals*

Facebook videos embed via a simple iframe URL — no API key needed for public videos.

The embed URL format is:
```
https://www.facebook.com/plugins/video.php?href=https://www.facebook.com/piloneslavictoria/videos/{VIDEO_ID}/&width=500&show_text=false
```

**To find a video ID:**
1. Go to `https://www.facebook.com/piloneslavictoria/`
2. Click on any video
3. The URL will be: `facebook.com/piloneslavictoria/videos/619070722815580/`
4. The number `619070722815580` is the video ID
5. Add it to the `fb_video_id` column in your Google Sheet for that product

**Currently known:**
- Lechugas video ID: `619070722815580`

No developer account or API key is needed for public video embeds.

---

## STEP 6 — Instagram post embed setup
*Required to embed Instagram posts in product modals*

Instagram posts embed via iframe — no API key needed for public posts.

The embed URL format is:
```
https://www.instagram.com/p/{POST_ID}/embed/
```

**To find a post ID:**
1. Go to `https://www.instagram.com/pilvicsa/`
2. Click on any post
3. The URL will be: `instagram.com/p/DPCyjf7DFnL/`
4. The string `DPCyjf7DFnL` is the post ID
5. Add it to the `ig_post_id` column in your Google Sheet for that product

**Currently known:**
- Recent reel: `DPCyjf7DFnL` (Innovar es...)
- Recent reel: `DEzbWhaJE8i` (Nosotros somos Pilvicsa)

Browse your Instagram feed and find posts that show specific products (arándanos, tomates, balsa, etc.) — add those IDs to the corresponding rows in the sheet.

---

## STEP 7 — YouTube video inventory
*Assign YouTube videos to products in the sheet*

Add the video ID to the `youtube_id` column in Google Sheets for these products:

| Product to find in sheet | YouTube ID to add |
|--------------------------|-------------------|
| Any Arándano variety | `b8_80NvRIAI` |
| Homepage (index) — not a product | `MScYlxfqeac` |

To find more videos:
1. Go to `https://www.youtube.com/@pilvicsa/videos`
2. For each relevant video, click on it
3. The video ID is the part after `?v=` in the URL:
   `youtube.com/watch?v=b8_80NvRIAI` → ID is `b8_80NvRIAI`

---

## STEP 8 — Hero video
*The full-screen autoplay video on the homepage*

You need one MP4 video file for the homepage hero:
- **Format:** MP4 (H.264)
- **Target size:** Under 8MB (compress if larger)
- **Resolution:** 1920×1080 or 1280×720
- **Duration:** 15-30 seconds of vivero footage that loops well
- **Content:** Greenhouse, seedlings, hands working — no sound needed (it autoplays muted)

**Place the file at:** `images/videos/hero.mp4`

If you have footage on Instagram or TikTok, you can download it using tools like `yt-dlp`:
```bash
pip install yt-dlp
yt-dlp https://www.instagram.com/reel/DPCyjf7DFnL/ -o images/videos/hero.mp4
```

If no video is ready yet, the site will fall back to a static hero image automatically.

---

## STEP 9 — Cloudflare setup (after site is built and deployed)
*Free CDN that dramatically speeds up the site*

1. Create a free account at `https://cloudflare.com`
2. Click **Add a Site** → enter `pilvicsa.com.ec`
3. Select the **Free plan**
4. Cloudflare will scan your DNS records and show them — verify they look correct
5. Cloudflare will give you 2 nameservers that look like:
   ```
   xxx.ns.cloudflare.com
   yyy.ns.cloudflare.com
   ```
6. Log into your domain registrar (wherever pilvicsa.com.ec is registered)
7. Replace the current nameservers with the Cloudflare ones
8. Wait 24-48 hours for DNS propagation
9. In Cloudflare dashboard:
   - Enable **Auto Minify** (CSS, JS, HTML)
   - Enable **Brotli compression**
   - Set cache level to **Standard**
   - Enable **Always HTTPS**

---

## STEP 10 — Google Search Console verification
*Lets Google index your site properly*

The DNS TXT verification record is already ready:
```
google-site-verification=i3jlzv1WvJIvskcPkBkoF5ZanKgd8Lnw6SO8ZYJK9eM
```

1. Log into `https://search.google.com/search-console`
2. Add property `pilvicsa.com.ec` if not already there
3. Choose **DNS verification**
4. In **cPanel → Zone Editor** → add a TXT record:
   - Name: `@` (or `pilvicsa.com.ec`)
   - Value: `google-site-verification=i3jlzv1WvJIvskcPkBkoF5ZanKgd8Lnw6SO8ZYJK9eM`
5. Click **Verify** in Search Console (may take a few minutes)
6. Once verified, submit sitemap: `https://pilvicsa.com.ec/sitemap.xml`

---

## STEP 11 — GitHub repo setup

Make sure your local repo is ready:

```bash
# Make sure you are on the dev branch
git checkout dev

# Pull latest
git pull origin dev

# Verify you have the right structure
ls
```

When Claude Code finishes building, commit to `dev`:
```bash
git add .
git commit -m "rebuild: complete site rebuild v2.0"
git push origin dev
```

Then test locally via XAMPP at `http://localhost/pilvicsa/` before merging to `main` and deploying to cPanel.

---

## STEP 12 — Image preparation

Before running the image optimizer:

1. Create the folder `images/raw/` in your repo if it doesn't exist
2. Copy all product photos into `images/raw/` — any format (JPG, PNG, HEIC from phone)
3. Name them to match the `id` in your spreadsheet:
   - Example: the photo for `hortalizas_001` (Tomate Lupitas) should be named `hortalizas_001.jpg`
4. Run the optimizer: `node scripts/optimize_images.js`
5. Check `images/productos/` — you should see `.webp` files for each input

---

## Quick reference — key numbers and IDs

| Item | Value |
|------|-------|
| Google account | pilvicsaec@gmail.com |
| YouTube channel ID | UCeCVD_GxctRBbUej5ycIljg |
| YouTube handle | @pilvicsa |
| Facebook page | piloneslavictoria |
| Instagram handle | @pilvicsa |
| TikTok handle | @pilvicsa |
| LinkedIn | /company/pilvicsa |
| Phone main | +593 032 235 011 |
| Phone mobile | +593 0997 609 747 |
| GSC verification | google-site-verification=i3jlzv1WvJIvskcPkBkoF5ZanKgd8Lnw6SO8ZYJK9eM |
| YouTube video — institucional | MScYlxfqeac |
| YouTube video — arándano | b8_80NvRIAI |
| YouTube video — empresa | pwLc7KfNk6k |
| Facebook video — lechugas | 619070722815580 |
| Instagram reel 1 | DPCyjf7DFnL |
| Instagram reel 2 | DEzbWhaJE8i |
| Google Sheets CSV URL | (fill in after Step 4b) |
| Google Sheet ID | (fill in after Step 4c) |

---

## Daily update workflow (once site is live)

When you want to add, remove, or edit a product:

1. Open the Google Sheet at `https://sheets.google.com`
2. Make your changes (add row, edit specs, add video ID, etc.)
3. Open terminal in repo folder:
   ```bash
   python scripts/fetch_sheet.py
   npm run build
   ```
4. Upload the changed files to cPanel
5. Done — no code changes, no Claude needed

When you want to add new product images:
1. Drop photo files into `images/raw/`
2. Run: `node scripts/optimize_images.js`
3. Upload `images/productos/` changes to cPanel
