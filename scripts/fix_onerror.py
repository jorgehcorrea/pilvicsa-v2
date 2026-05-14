import re, os

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

PAGES = [
    'buscar.html',
    'producto-hortalizas.html',
    'productos-cultivoscosta.html',
    'productos-especies.html',
    'productos-florescorte.html',
    'productos-frutalesforestales.html',
    'productos-otras.html',
]

HELPER = '\nfunction pilvImgErr(el){el.parentElement.innerHTML=PLACEHOLDER_SVG;}\n'

# Matches: onerror="this.parentElement.innerHTML='${PLACEHOLDER_SVG.replace(...)....}';"
# with optional whitespace before it
ONERROR_RE = re.compile(
    r"""\s*onerror="this\.parentElement\.innerHTML='\$\{PLACEHOLDER_SVG\.replace\([^)]+\)\.replace\([^)]+\)}';">""",
    re.DOTALL
)
REPLACEMENT = ' onerror="pilvImgErr(this)">'

for page in PAGES:
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # Inject helper after PLACEHOLDER_SVG definition (once)
    if 'pilvImgErr' not in content and 'const PLACEHOLDER_SVG' in content:
        idx = content.find('const PLACEHOLDER_SVG')
        # find the closing backtick+semicolon of the template literal
        tick_start = content.find('`', idx + len('const PLACEHOLDER_SVG'))
        tick_end = content.find('`;', tick_start + 1)
        if tick_end != -1:
            insert_at = tick_end + 2
            content = content[:insert_at] + HELPER + content[insert_at:]

    content, n = ONERROR_RE.subn(REPLACEMENT, content)

    if content != original:
        with open(page, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed ({n} onerror): {page}')
    else:
        print(f'No change:           {page}')
