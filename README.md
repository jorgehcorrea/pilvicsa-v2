# Pilvicsa — Website v2

Official website for **Pilvicsa (Pilones La Victoria S.A.)**, an Ecuadorian plant nursery and propagation company founded in 1999. Specializing in seedling production, grafts, cuttings, and meristematic hardening for small, medium, and large-scale farmers across Ecuador.

🌐 **Live site:** [pilvicsa.com.ec](https://pilvicsa.com.ec)  
🔗 **Preview (GitHub Pages):** [jorgehcorrea.github.io/pilvicsa-v2](https://jorgehcorrea.github.io/pilvicsa-v2)

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| CSS framework | Tailwind CSS v4 |
| Components | Flowbite 2.3 |
| Search | Fuse.js 7 (fuzzy search) |
| Animations | GSAP 3.12 + ScrollTrigger |
| Image optimization | Sharp (Node.js) |
| Data pipeline | Python + Google Sheets CSV |
| Hosting | EcuaHosting cPanel |
| CDN | Cloudflare (free tier) |

---

## Project structure

```
pilvicsa-v2/
├── data/
│   └── products.json          ← 221 product varieties (generated from Google Sheets)
├── images/
│   ├── raw/                   ← drop new product photos here (any format)
│   ├── productos/             ← optimized WebP output (800×600px)
│   ├── featured/              ← category hero images
│   ├── pages/                 ← product page headers
│   ├── slider/                ← homepage hero fallback
│   ├── carousel/              ← services section
│   ├── sections/              ← full-bleed backgrounds
│   └── videos/                ← hero.mp4 autoplay loop
├── scripts/
│   ├── fetch_sheet.py         ← Google Sheets CSV → data/products.json
│   ├── optimize_images.js     ← images/raw/ → images/productos/ WebP
│   └── build.sh               ← full build pipeline
├── src/
│   └── input.css              ← Tailwind source
├── dist/
│   └── css/style.css          ← compiled Tailwind output
├── index.html                 ← Homepage
├── buscar.html                ← Product search (221 varieties, Fuse.js)
├── producto-hortalizas.html
├── productos-florescorte.html
├── productos-cultivoscosta.html
├── productos-frutalesforestales.html
├── productos-especies.html
├── productos-otras.html
├── localizaciones.html
├── herramientas-planificacion.html
├── herramientas-cuidado.html
├── herramientas-conversion.html
├── sitemap.xml
├── robots.txt
└── .htaccess
```

---

## Product database

All 221 product varieties are stored in `data/products.json`. The database covers:

| Category | Varieties |
|----------|-----------|
| Hortalizas | 107 |
| Frutales y Forestales | 38 |
| Flores de Corte | 26 |
| Especies y Aromáticas | 21 |
| Cultivos Especiales | 17 |
| Cultivos de Costa | 12 |
| **Total** | **221** |

---

## Update products (no code required)

### Via Google Sheets
1. Open the [Pilvicsa Products Sheet](REPLACE_WITH_SHEET_URL) (pilvicsaec@gmail.com)
2. Add, edit, or remove rows
3. Run: `python scripts/fetch_sheet.py`
4. Run: `npm run build`
5. Upload `data/products.json` and `dist/css/style.css` to cPanel

### Via CSV
1. Edit `data/products_backup.csv` directly
2. Run: `python scripts/fetch_sheet.py --local`
3. Run: `npm run build`

---

## Add product images

1. Drop photos (any format — JPG, PNG, HEIC) into `images/raw/`
2. Name each file to match the product ID: e.g. `hortalizas_001.jpg`
3. Run: `node scripts/optimize_images.js`
4. Images are automatically converted to WebP 800×600px in `images/productos/`
5. Upload `images/productos/` to cPanel

---

## Local development

```bash
# Install dependencies (one time)
npm install
pip install requests

# Watch Tailwind CSS
npm run watch

# Open in browser
# http://localhost/pilvicsa-v2/index.html (via XAMPP)
```

---

## Build and deploy

```bash
# Full build
bash scripts/build.sh

# Or step by step:
python scripts/fetch_sheet.py    # pull latest products from Google Sheets
node scripts/optimize_images.js  # process new images
npm run build                    # compile Tailwind CSS

# Deploy: upload all files to cPanel public_html/
# Or: git push → cPanel Git Version Control pull
```

---

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production — deployed to pilvicsa.com.ec |
| `dev2` | Development — active working branch |

Always work on `dev2`. Merge to `main` only after testing.

---

## Contact

**Pilvicsa — Pilones La Victoria S.A.**  
📞 +593 032 235 011 / +593 0997 609 747  
📧 pilvicsaec@gmail.com  
🌐 pilvicsa.com.ec  
📍 Latacunga (Sierra) · Santo Domingo (Costa)

---

## Social media

- [Facebook](https://www.facebook.com/piloneslavictoria/)
- [Instagram](https://www.instagram.com/pilvicsa/)
- [YouTube](https://www.youtube.com/@pilvicsa)
- [TikTok](https://www.tiktok.com/@pilvicsa)
- [LinkedIn](https://www.linkedin.com/company/pilvicsa)

---

*© 2025 Pilvicsa — Pilones La Victoria S.A. All rights reserved.*
