# Converts legacy pilvicsa-data.js to data/products.json (v2 schema)
import json, os

SRC  = r'C:\xampp\htdocs\pilvicsa\pilvicsa-data.js'
DEST = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')

PAGE_MAP = {'frutales': 'frutalesforestales'}

SPEC_MAP = {
    'color':                'color',
    'forma':                'forma',
    'sistema':              'sistema',
    'densidad':             'densidad',
    'densidad de siembra':  'densidad',
    'resistencias':         'resistencias',
    'ciclo':                'ciclo',
    'ciclo productivo':     'ciclo',
    'tiempo de cultivo':    'ciclo',
    'tamaño':               'tamano',
    'tamaño / rendimiento': 'tamano',
    'tamaño ramo':          'tamano',
}
RESIST_KEYS = {'resist. alta': 'Alta', 'resist. intermedia': 'Intermedia'}


def between(line, start, end):
    """Extract text that lies between two fixed delimiters."""
    s = line.find(start)
    if s == -1:
        return ''
    s += len(start)
    e = line.find(end, s)
    return line[s:e] if e != -1 else line[s:]


def parse_specs(raw):
    out = {f: '' for f in ['color', 'forma', 'sistema', 'densidad', 'resistencias', 'ciclo', 'tamano']}
    nota_parts = []
    if not raw:
        return out, ''
    for pair in raw.split('||'):
        sep = pair.find('|')
        if sep == -1:
            continue
        k   = pair[:sep].strip()
        kl  = k.lower()
        val = pair[sep + 1:].strip().replace('&quot;', '"')
        if kl in SPEC_MAP:
            f = SPEC_MAP[kl]
            out[f] = (out[f] + '; ' + val) if out[f] else val
        elif kl in RESIST_KEYS:
            label = RESIST_KEYS[kl] + ': ' + val
            out['resistencias'] = (out['resistencias'] + '; ' + label) if out['resistencias'] else label
        else:
            nota_parts.append(k + ': ' + val)
    return out, '; '.join(nota_parts)


products = []
with open(SRC, encoding='utf-8') as f:
    for raw_line in f:
        line = raw_line.strip()
        if not line.startswith("{id:'"):
            continue

        pid      = between(line, "{id:'",       "',name:'")
        nombre   = between(line, ",name:'",      "',latin:'")
        latin    = between(line, ",latin:'",     "',cat:'")
        cat      = between(line, ",cat:'",       "',page:'")
        page     = between(line, ",page:'",      "',pageLabel:'")
        plabel   = between(line, ",pageLabel:'", "',file:'")
        specs_r  = between(line, ",specs:'",     "',status:'")
        status   = between(line, ",status:'",    "',note:'")
        note_old = between(line, ",note:'",      "',img:'")
        img      = between(line, ",img:'",       "'},")
        if not img:                               # last item ends with '}' not '},'
            img = between(line, ",img:'", "'}]")

        pagina = PAGE_MAP.get(page, page)
        estado = 'potential' if status == 'potential' else 'confirmed'
        imagen = os.path.basename(img) if img else ''

        specs, nota_specs = parse_specs(specs_r)
        nota = '; '.join(filter(None, [nota_specs, note_old]))

        products.append({
            'id':           pid,
            'nombre':       nombre,
            'latin':        latin,
            'categoria':    cat,
            'pagina':       pagina,
            'pageLabel':    plabel,
            'color':        specs['color'],
            'forma':        specs['forma'],
            'sistema':      specs['sistema'],
            'densidad':     specs['densidad'],
            'resistencias': specs['resistencias'],
            'ciclo':        specs['ciclo'],
            'tamano':       specs['tamano'],
            'imagen':       imagen,
            'youtube_id':   '',
            'fb_video_id':  '',
            'ig_post_id':   '',
            'estado':       estado,
            'nota':         nota,
        })

with open(DEST, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f'Written {len(products)} products to {DEST}')
