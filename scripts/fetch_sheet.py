"""
Fetches Pilvicsa product data from Google Sheets published CSV.
Usage: python scripts/fetch_sheet.py
Output: data/products.json
"""
import requests, csv, json, io, os

SHEET_CSV_URL = "REPLACE_WITH_PUBLISHED_CSV_URL"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')

COLUMNS = ['id','nombre','latin','categoria','pagina','pageLabel','color','forma',
           'sistema','densidad','resistencias','ciclo','tamano','imagen',
           'youtube_id','fb_video_id','ig_post_id','estado','nota']

def fetch():
    r = requests.get(SHEET_CSV_URL, timeout=30)
    r.raise_for_status()
    reader = csv.DictReader(io.StringIO(r.text))
    products = []
    for row in reader:
        p = {col: row.get(col, '').strip() for col in COLUMNS}
        if p['id'] and p['nombre']:  # skip empty rows
            products.append(p)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"Written {len(products)} products to {OUTPUT_PATH}")

if __name__ == '__main__':
    fetch()
