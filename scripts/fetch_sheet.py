# Fetches Pilvicsa products from Google Sheets → data/products.json
# Usage: python scripts/fetch_sheet.py
import requests, csv, json, io, os

SHEET_ID  = '1S5fN0z-mpQxGTCXlFRuPgvAXFKQ77uxzCLV07Hxy0qw'
SHEET_TAB = 'productos_google_sheets'
SHEET_CSV_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={SHEET_TAB}'

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')

# Extra sheet columns that get merged into nota
EXTRA_COLS = ['descripcion', 'colores_disponibles', 'recomendaciones', 'familia', 'uso', 'disponibilidad']
EXTRA_LABELS = {
    'descripcion':        '',
    'colores_disponibles':'Colores: ',
    'recomendaciones':    'Recomendaciones: ',
    'familia':            'Familia: ',
    'uso':                'Uso: ',
    'disponibilidad':     'Disponibilidad: ',
}

CORE = ['id','nombre','latin','categoria','pagina','pageLabel','color','forma',
        'sistema','densidad','resistencias','ciclo','tamano','imagen',
        'youtube_id','fb_video_id','ig_post_id','estado','nota']

def fetch():
    r = requests.get(SHEET_CSV_URL, timeout=30)
    r.raise_for_status()
    r.encoding = 'utf-8'
    reader = csv.DictReader(io.StringIO(r.text))
    products = []
    for row in reader:
        if not row.get('id','').strip() or not row.get('nombre','').strip():
            continue
        p = {col: row.get(col, '').strip() for col in CORE}
        # merge extra columns into nota
        extra_parts = [
            EXTRA_LABELS[col] + row.get(col,'').strip()
            for col in EXTRA_COLS
            if row.get(col,'').strip()
        ]
        if extra_parts:
            p['nota'] = '; '.join(filter(None, [p['nota']] + extra_parts))
        if not p['estado']:
            p['estado'] = 'confirmed'
        products.append(p)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f'Written {len(products)} products to {OUTPUT_PATH}')

if __name__ == '__main__':
    fetch()
