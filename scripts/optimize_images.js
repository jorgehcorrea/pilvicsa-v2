/**
 * Converts all images in images/raw/ to WebP 800x600 in images/productos/
 * Usage: node scripts/optimize_images.js
 * Requires: npm install sharp
 */
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const RAW_DIR = path.join(__dirname, '..', 'images', 'raw');
const OUT_DIR = path.join(__dirname, '..', 'images', 'productos');
const SUPPORTED = ['.jpg','.jpeg','.png','.webp','.heic','.tiff'];

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

const files = fs.readdirSync(RAW_DIR).filter(f =>
  SUPPORTED.includes(path.extname(f).toLowerCase())
);

(async () => {
  for (const file of files) {
    const name = path.parse(file).name;
    const outPath = path.join(OUT_DIR, name + '.webp');
    try {
      await sharp(path.join(RAW_DIR, file))
        .resize(800, 600, { fit: 'cover', position: 'centre' })
        .webp({ quality: 82 })
        .toFile(outPath);
      console.log(`✓ ${file} → ${name}.webp`);
    } catch(e) {
      console.error(`✗ ${file}: ${e.message}`);
    }
  }
  console.log(`Done. ${files.length} images processed.`);
})();
