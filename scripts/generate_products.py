#!/usr/bin/env python3
"""
Generate static product pages and sitemap.xml for Pilvicsa v2.
Usage:  python scripts/generate_products.py
Output: productos/*.html  +  sitemap.xml  (both relative to repo root)
"""
import html as _html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT    = Path(__file__).resolve().parent.parent
DATA    = ROOT / 'data' / 'products.json'
OUT_DIR = ROOT / 'productos'
SITE    = 'https://pilvicsa.com.ec'
TODAY   = date.today().isoformat()

PAGE_URLS = {
    'hortalizas':         'producto-hortalizas.html',
    'florescorte':        'productos-florescorte.html',
    'cultivoscosta':      'productos-cultivoscosta.html',
    'frutalesforestales': 'productos-frutalesforestales.html',
    'especies':           'productos-especies.html',
    'otras':              'productos-otras.html',
}
PAGE_LABELS = {
    'hortalizas':         'Hortalizas',
    'florescorte':        'Flores de Corte',
    'cultivoscosta':      'Cultivos de Costa',
    'frutalesforestales': 'Frutales y Forestales',
    'especies':           'Especies y Aromaticas',
    'otras':              'Cultivos Especiales',
}
STATIC_PAGES = [
    ('',                                  1.0, 'monthly'),
    ('producto-hortalizas.html',          0.9, 'weekly'),
    ('productos-florescorte.html',        0.9, 'weekly'),
    ('productos-cultivoscosta.html',      0.9, 'weekly'),
    ('productos-frutalesforestales.html', 0.9, 'weekly'),
    ('productos-especies.html',           0.9, 'weekly'),
    ('productos-otras.html',              0.9, 'weekly'),
    ('buscar.html',                       0.8, 'weekly'),
    ('localizaciones.html',               0.7, 'monthly'),
    ('herramientas-planificacion.html',   0.6, 'monthly'),
    ('herramientas-cuidado.html',         0.6, 'monthly'),
    ('herramientas-conversion.html',      0.6, 'monthly'),
]


def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def esc(t):
    return _html.escape(str(t), quote=True)


def meta_desc(p):
    name  = p['nombre']
    latin = p.get('latin', '')
    cat   = p.get('categoria', '')
    specs = []
    if p.get('tamano'): specs.append(p['tamano'])
    if p.get('ciclo'):  specs.append('ciclo ' + p['ciclo'])
    head = 'Plantulas de ' + name
    if latin: head += ' (' + latin + ')'
    parts = [head]
    if cat:   parts.append(cat)
    if specs: parts.append(', '.join(specs))
    parts.append('Vivero Pilvicsa Ecuador.')
    return ' - '.join(parts)


def img_url(p):
    img = p.get('imagen', '')
    if not img: return ''
    return img if img.startswith('http') else SITE + '/' + img


def page_html(p, slug):
    pagina    = p.get('pagina', 'hortalizas')
    cat_url   = PAGE_URLS.get(pagina, 'producto-hortalizas.html')
    cat_label = PAGE_LABELS.get(pagina, p.get('pageLabel', 'Productos'))
    desc      = meta_desc(p)
    canonical = SITE + '/productos/' + slug + '.html'
    img       = img_url(p)
    wa_msg    = quote('Hola, me interesa ' + p['nombre'], safe='')

    spec_fields = [
        ('Nombre cientifico', p.get('latin', '')),
        ('Categoria',         p.get('categoria', '')),
        ('Color',             p.get('color', '')),
        ('Forma',             p.get('forma', '')),
        ('Tamano',            p.get('tamano', '')),
        ('Ciclo',             p.get('ciclo', '')),
        ('Sistema',           p.get('sistema', '')),
        ('Densidad',          p.get('densidad', '')),
        ('Resistencias',      p.get('resistencias', '')),
        ('Nota',              p.get('nota', '')),
    ]
    rows_html = '\n          '.join(
        '<tr><td class="py-2 pr-4 text-sm font-semibold text-pilvicsa-primary w-40 align-top whitespace-nowrap">'
        + k + '</td><td class="py-2 text-sm text-gray-700">' + esc(v) + '</td></tr>'
        for k, v in spec_fields if v
    )

    ld_product = json.dumps({
        '@context': 'https://schema.org', '@type': 'Product',
        'name': p['nombre'], 'description': desc,
        'brand': {'@type': 'Brand', 'name': 'Pilvicsa'},
        'category': p.get('categoria', ''),
        **(({'image': img}) if img else {}),
        'offers': {
            '@type': 'Offer',
            'availability': 'https://schema.org/InStock',
            'priceCurrency': 'USD',
            'seller': {'@type': 'Organization', 'name': 'Pilvicsa', 'url': SITE},
        },
    }, ensure_ascii=False, indent=None)

    ld_breadcrumb = json.dumps({
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Inicio',        'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': cat_label,       'item': SITE + '/' + cat_url},
            {'@type': 'ListItem', 'position': 3, 'name': p['nombre'],     'item': canonical},
        ],
    }, ensure_ascii=False, indent=None)

    img_tag    = ('<img src="' + esc(img) + '" alt="' + esc(p['nombre']) +
                  '" class="w-full h-64 object-cover rounded-xl mb-6"'
                  ' onerror="this.style.display=\'none\'">') if img else ''
    latin_line = ('<p class="text-white/50 text-sm italic">' + esc(p['latin']) + '</p>') if p.get('latin') else ''
    og_image   = '<meta property="og:image" content="' + esc(img) + '">' if img else ''

    return (
        '<!DOCTYPE html>\n'
        '<html lang="es-EC" dir="ltr">\n'
        '<head>\n'
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '  <title>' + esc(p['nombre']) + ' - Plantulas | Pilvicsa Ecuador</title>\n'
        '  <meta name="description" content="' + esc(desc) + '">\n'
        '  <link rel="canonical" href="' + canonical + '">\n'
        '  <link rel="icon" href="../images/pilvicsa.ico" type="image/x-icon">\n'
        '  <meta property="og:type" content="product">\n'
        '  <meta property="og:site_name" content="Pilvicsa">\n'
        '  <meta property="og:title" content="' + esc(p['nombre']) + ' | Pilvicsa">\n'
        '  <meta property="og:description" content="' + esc(desc) + '">\n'
        '  <meta property="og:url" content="' + canonical + '">\n'
        '  <meta property="og:locale" content="es_EC">\n'
        '  ' + og_image + '\n'
        '  <meta name="twitter:card" content="summary_large_image">\n'
        '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&family=Syne:wght@700;800&display=swap" rel="stylesheet">\n'
        '  <link rel="stylesheet" href="../dist/css/style.css">\n'
        '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.css">\n'
        '  <style>#main-navbar { background-color:#fff; box-shadow:0 1px 8px rgba(0,0,0,0.07); }</style>\n'
        '  <script type="application/ld+json">' + ld_product + '</script>\n'
        '  <script type="application/ld+json">' + ld_breadcrumb + '</script>\n'
        '</head>\n'
        '<body class="font-sans text-gray-900 bg-gray-50">\n'
        '\n'
        '<nav id="main-navbar" class="fixed top-0 left-0 right-0 z-50">\n'
        '  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
        '    <div class="flex items-center justify-between h-16">\n'
        '      <a href="../index.html" class="flex items-center gap-3 flex-shrink-0">\n'
        '        <img src="../images/logo@2x.png" alt="Pilvicsa" class="h-9 w-auto">\n'
        '      </a>\n'
        '      <div class="hidden lg:flex items-center gap-1">\n'
        '        <a href="../index.html" class="px-3 py-2 text-sm font-semibold text-pilvicsa-primary hover:text-pilvicsa-accent transition">Inicio</a>\n'
        '        <div class="relative group">\n'
        '          <button class="px-3 py-2 text-sm font-semibold text-pilvicsa-accent border-b-2 border-pilvicsa-accent inline-flex items-center gap-1">Productos <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg></button>\n'
        '          <div class="absolute top-full left-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 py-1">\n'
        '            <a href="../producto-hortalizas.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-pilvicsa-surface hover:text-pilvicsa-primary transition">Hortalizas</a>\n'
        '            <a href="../productos-florescorte.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-pilvicsa-surface hover:text-pilvicsa-primary transition">Flores de Corte</a>\n'
        '            <a href="../productos-cultivoscosta.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-pilvicsa-surface hover:text-pilvicsa-primary transition">Cultivos de Costa</a>\n'
        '            <a href="../productos-frutalesforestales.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-pilvicsa-surface hover:text-pilvicsa-primary transition">Frutales y Forestales</a>\n'
        '            <a href="../productos-especies.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-pilvicsa-surface hover:text-pilvicsa-primary transition">Especies y Aromaticas</a>\n'
        '            <a href="../productos-otras.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-pilvicsa-surface hover:text-pilvicsa-primary transition">Cultivos Especiales</a>\n'
        '          </div>\n'
        '        </div>\n'
        '        <a href="../buscar.html" class="px-3 py-2 text-sm font-semibold text-pilvicsa-primary hover:text-pilvicsa-accent transition">Buscar</a>\n'
        '        <a href="../localizaciones.html" class="px-3 py-2 text-sm font-semibold text-pilvicsa-primary hover:text-pilvicsa-accent transition">Contacto</a>\n'
        '      </div>\n'
        '      <a href="../buscar.html" class="hidden lg:inline-flex items-center gap-2 bg-pilvicsa-accent text-pilvicsa-dark px-5 py-2.5 rounded-lg text-sm font-bold hover:bg-pilvicsa-light hover:text-white transition">Explorar Variedades <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg></a>\n'
        '      <button data-collapse-toggle="mobile-menu-prod" type="button" class="lg:hidden p-2 rounded-lg text-pilvicsa-primary hover:bg-pilvicsa-surface transition" aria-controls="mobile-menu-prod" aria-expanded="false">\n'
        '        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>\n'
        '      </button>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div id="mobile-menu-prod" class="hidden lg:hidden bg-white border-t border-gray-100 shadow-sm">\n'
        '    <div class="px-4 py-3 space-y-1">\n'
        '      <a href="../index.html" class="block px-3 py-2 text-sm font-semibold text-pilvicsa-primary">Inicio</a>\n'
        '      <a href="../' + cat_url + '" class="block px-3 py-2 text-sm font-semibold text-pilvicsa-accent">' + esc(cat_label) + '</a>\n'
        '      <a href="../buscar.html" class="block px-3 py-2 text-sm font-semibold text-pilvicsa-primary">Buscar</a>\n'
        '      <a href="../localizaciones.html" class="block px-3 py-2 text-sm font-semibold text-pilvicsa-primary">Contacto</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</nav>\n'
        '\n'
        '<div class="bg-pilvicsa-dark pt-16">\n'
        '  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">\n'
        '    <nav class="text-xs text-white/40 mb-4" aria-label="Breadcrumb">\n'
        '      <a href="../index.html" class="hover:text-white/70 transition">Inicio</a>\n'
        '      <span class="mx-2">/</span>\n'
        '      <a href="../' + cat_url + '" class="hover:text-white/70 transition">' + esc(cat_label) + '</a>\n'
        '      <span class="mx-2">/</span>\n'
        '      <span class="text-white/70">' + esc(p['nombre']) + '</span>\n'
        '    </nav>\n'
        '    <h1 class="font-display font-black text-3xl lg:text-4xl text-white mb-1">' + esc(p['nombre']) + '</h1>\n'
        '    ' + latin_line + '\n'
        '    <p class="text-pilvicsa-accent text-sm font-semibold mt-2">' + esc(cat_label) + '</p>\n'
        '  </div>\n'
        '</div>\n'
        '\n'
        '<main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">\n'
        '  ' + img_tag + '\n'
        '  <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">\n'
        '    <div class="px-6 py-5 bg-pilvicsa-surface border-b border-gray-100">\n'
        '      <p class="text-xs font-bold uppercase tracking-widest text-pilvicsa-primary">Ficha del Producto</p>\n'
        '    </div>\n'
        '    <div class="px-6 py-4">\n'
        '      <table class="w-full">\n'
        '        <tbody>\n'
        '          ' + rows_html + '\n'
        '        </tbody>\n'
        '      </table>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="mt-8 bg-pilvicsa-dark rounded-2xl p-6 text-white">\n'
        '    <h2 class="font-bold text-lg mb-2">Interesado en ' + esc(p['nombre']) + '?</h2>\n'
        '    <p class="text-white/60 text-sm mb-5">Contacta con nuestros asesores para disponibilidad, precios y cantidades.</p>\n'
        '    <div class="flex flex-wrap gap-3">\n'
        '      <a href="https://wa.me/593997609747?text=' + wa_msg + '" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition">WhatsApp</a>\n'
        '      <a href="../' + cat_url + '" class="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition">Ver mas ' + esc(cat_label) + '</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</main>\n'
        '\n'
        '<footer class="bg-pilvicsa-dark text-white">\n'
        '  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">\n'
        '    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 mb-10">\n'
        '      <div><a href="../index.html" class="flex items-center gap-3 mb-4"><img src="../images/logo@2x.png" alt="Pilvicsa" class="h-10 w-auto"></a><p class="text-white/40 text-sm leading-relaxed">Germinando desde 1999.<br>Vivero y pilonera lider del Ecuador.</p></div>\n'
        '      <div><h4 class="text-xs font-bold uppercase tracking-widest text-pilvicsa-accent mb-4">Productos</h4><ul class="space-y-2 text-sm text-white/55"><li><a href="../producto-hortalizas.html" class="hover:text-white transition">Hortalizas</a></li><li><a href="../productos-florescorte.html" class="hover:text-white transition">Flores de Corte</a></li><li><a href="../productos-frutalesforestales.html" class="hover:text-white transition">Frutales y Forestales</a></li><li><a href="../buscar.html" class="text-pilvicsa-accent/70 hover:text-pilvicsa-accent transition">Ver todas</a></li></ul></div>\n'
        '      <div><h4 class="text-xs font-bold uppercase tracking-widest text-pilvicsa-accent mb-4">Herramientas</h4><ul class="space-y-2 text-sm text-white/55"><li><a href="../herramientas-planificacion.html" class="hover:text-white transition">Planificacion</a></li><li><a href="../herramientas-cuidado.html" class="hover:text-white transition">Cuidado del Cultivo</a></li><li><a href="../herramientas-conversion.html" class="hover:text-white transition">Conversion de Unidades</a></li></ul></div>\n'
        '      <div><h4 class="text-xs font-bold uppercase tracking-widest text-pilvicsa-accent mb-4">Contacto</h4><ul class="space-y-2.5 text-sm text-white/55 mb-5"><li><a href="tel:+593322235011" class="hover:text-white transition">032 235 011</a></li><li><a href="mailto:pilvicsaec@gmail.com" class="hover:text-white transition">pilvicsaec@gmail.com</a></li></ul><a href="https://wa.me/593997609747" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-lg text-xs font-semibold transition">WhatsApp</a></div>\n'
        '    </div>\n'
        '    <div class="border-t border-white/10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">\n'
        '      <p class="text-white/35 text-sm">2025 Pilvicsa &middot; <a href="https://pilvicsa.com.ec" class="hover:text-white/55 transition">pilvicsa.com.ec</a></p>\n'
        '      <div class="flex gap-6 text-sm text-white/35"><a href="../sitemap.xml" class="hover:text-white/55 transition">Sitemap</a><a href="../localizaciones.html" class="hover:text-white/55 transition">Contacto</a></div>\n'
        '    </div>\n'
        '  </div>\n'
        '</footer>\n'
        '\n'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js"></script>\n'
        '</body>\n'
        '</html>\n'
    )


def generate_sitemap(products, slug_map):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, priority, freq in STATIC_PAGES:
        loc = SITE + '/' + path if path else SITE + '/'
        lines += [
            '  <url>',
            '    <loc>' + loc + '</loc>',
            '    <lastmod>' + TODAY + '</lastmod>',
            '    <changefreq>' + freq + '</changefreq>',
            '    <priority>' + str(priority) + '</priority>',
            '  </url>',
        ]
    for p in products:
        slug = slug_map.get(p.get('id', ''), '')
        if not slug: continue
        lines += [
            '  <url>',
            '    <loc>' + SITE + '/productos/' + slug + '.html</loc>',
            '    <lastmod>' + TODAY + '</lastmod>',
            '    <changefreq>yearly</changefreq>',
            '    <priority>0.7</priority>',
            '  </url>',
        ]
    lines.append('</urlset>')
    return '\n'.join(lines)


def main():
    products = json.loads(DATA.read_text(encoding='utf-8'))
    OUT_DIR.mkdir(exist_ok=True)

    seen, slug_map = set(), {}
    for p in products:
        base = slugify(p['nombre'])
        slug, n = base, 2
        while slug in seen:
            slug = base + '-' + str(n)
            n += 1
        seen.add(slug)
        slug_map[p['id']] = slug

    for p in products:
        slug = slug_map[p['id']]
        (OUT_DIR / (slug + '.html')).write_text(page_html(p, slug), encoding='utf-8')

    print('Generated', len(products), 'product pages in productos/')

    sitemap = generate_sitemap(products, slug_map)
    (ROOT / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    total = len(STATIC_PAGES) + len(products)
    print('Generated sitemap.xml with', total, 'URLs')


if __name__ == '__main__':
    main()
