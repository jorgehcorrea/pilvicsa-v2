#!/bin/bash
echo "→ Fetching products from Google Sheets..."
python scripts/fetch_sheet.py

echo "→ Optimizing images..."
node scripts/optimize_images.js

echo "→ Building Tailwind CSS..."
npx @tailwindcss/cli -i src/input.css -o dist/css/style.css --minify

echo "✓ Build complete. Upload dist/ and all HTML files to cPanel."
