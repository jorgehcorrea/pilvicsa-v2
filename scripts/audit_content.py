#!/usr/bin/env python3
# audit_content.py — Pilvicsa v2 content migration pipeline
# Usage: python scripts/audit_content.py [scrape|diff|patch]
import sys, json, re, time, subprocess
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent
AUDIT_DIR  = ROOT / 'audit'
LIVE_JSON  = AUDIT_DIR / 'live_content.json'
DIFF_JSON  = AUDIT_DIR / 'diff_data.json'
DIFF_MD    = AUDIT_DIR / 'diff_report.md'
PATCH_LOG  = AUDIT_DIR / 'patch_log.md'
BACKUP_DIR = AUDIT_DIR / 'backups'

for _d in (AUDIT_DIR, BACKUP_DIR):
    _d.mkdir(exist_ok=True)

# ── Live site pages & v2 file map ─────────────────────────────────────────────
PAGES = [
    ('index',                        'https://pilvicsa.com.ec/index.html'),
    ('localizaciones',               'https://pilvicsa.com.ec/localizaciones.html'),
    ('productos-florescorte',        'https://pilvicsa.com.ec/productos-florescorte.html'),
    ('productos-cultivoscosta',      'https://pilvicsa.com.ec/productos-cultivoscosta.html'),
    ('productos-frutalesforestales', 'https://pilvicsa.com.ec/productos-frutalesforestales.html'),
    ('productos-especies',           'https://pilvicsa.com.ec/productos-especies.html'),
    ('productos-otras',              'https://pilvicsa.com.ec/productos-otras.html'),
    ('producto-hortalizas',          'https://pilvicsa.com.ec/producto-hortalizas.html'),
    ('herramientas-planificacion',   'https://pilvicsa.com.ec/herramientas-planificacion.html'),
    ('herramientas-cuidado',         'https://pilvicsa.com.ec/herramientas-cuidado.html'),
    ('herramientas-conversion',      'https://pilvicsa.com.ec/herramientas-conversion.html'),
]

V2_FILES = {k: k + '.html' if k != 'producto-hortalizas' else 'producto-hortalizas.html'
            for k, _ in PAGES}

PHONE_RE  = re.compile(r'\+?[\d\s\-]{7,}')
SOCIAL_RE = re.compile(r'(facebook\.com|instagram\.com|youtube\.com|tiktok\.com|linkedin\.com)', re.I)


# ── SHARED: content extractor (works on both live HTML and v2 files) ──────────

def extract_content(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    nav  = soup.find('nav')
    foot = soup.find('footer')
    excluded = [e for e in (nav, foot) if e is not None]

    def in_excluded(tag):
        for p in tag.parents:
            if p in excluded:
                return True
        return False

    # Meta
    t         = soup.find('title')
    title     = t.get_text(strip=True) if t else ''
    dm        = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
    meta_desc = dm.get('content', '').strip() if dm else ''

    # Headings outside nav/footer
    headings = [
        {'tag': h.name, 'text': h.get_text(strip=True)}
        for h in soup.find_all(['h1', 'h2', 'h3'])
        if not in_excluded(h)
    ]

    # Paragraphs outside nav/footer
    paragraphs = [
        p.get_text(strip=True)
        for p in soup.find_all('p')
        if not in_excluded(p) and p.get_text(strip=True)
    ]

    # Phones from full body text
    body_text = soup.get_text(' ')
    phones = sorted(set(
        ph.strip() for ph in PHONE_RE.findall(body_text)
        if len(ph.strip()) >= 7
    ))

    # Addresses — tags that mention location keywords
    addresses = []
    for tag in soup.find_all(['p', 'div', 'address', 'span']):
        txt = tag.get_text(' ', strip=True)
        if re.search(
            r'(calle|av\.|avenida|\bkm\b|dirección|quito|latacunga|ambato|guayaquil|ecuador)',
            txt, re.I
        ) and 20 < len(txt) < 300 and txt not in addresses:
            addresses.append(txt)

    # Google Maps iframes
    maps_iframes = [
        i.get('src', '')
        for i in soup.find_all('iframe')
        if 'google.com/maps' in i.get('src', '') or 'maps.google' in i.get('src', '')
    ]

    # Internal nav links
    nav_links = []
    if nav:
        for a in nav.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('http', 'mailto', 'tel', '#')):
                nav_links.append({'href': href, 'text': a.get_text(strip=True)})

    # Footer links
    footer_links = (
        [{'href': a['href'], 'text': a.get_text(strip=True)}
         for a in foot.find_all('a', href=True)]
        if foot else []
    )

    # Social links anywhere on page
    social_links = []
    for a in soup.find_all('a', href=True):
        m = SOCIAL_RE.search(a['href'])
        if m:
            social_links.append({
                'href': a['href'],
                'platform': m.group(1).split('.')[0].lower(),
            })

    # Images outside nav
    nav_srcs = {i.get('src', '') for i in (nav.find_all('img') if nav else [])}
    images = [
        i.get('src', '')
        for i in soup.find_all('img')
        if i.get('src', '') not in nav_srcs
    ]

    # Copyright text in footer
    copyright_text = ''
    if foot:
        for tag in foot.find_all(['p', 'span', 'div']):
            txt = tag.get_text(strip=True)
            if '©' in txt or 'copyright' in txt.lower():
                copyright_text = txt
                break

    return {
        'title':        title,
        'meta_desc':    meta_desc,
        'headings':     headings,
        'paragraphs':   paragraphs,
        'phones':       phones,
        'addresses':    addresses,
        'maps_iframes': maps_iframes,
        'nav_links':    nav_links,
        'footer_links': footer_links,
        'social_links': social_links,
        'images':       images,
        'copyright':    copyright_text,
    }


# ── MODE 1 — SCRAPE ───────────────────────────────────────────────────────────

def mode_scrape():
    import requests
    print('MODE 1 — SCRAPE\n' + '═' * 60)
    results = {}

    for key, url in PAGES:
        print(f'\n→ {url}')
        try:
            r = requests.get(url, timeout=20, headers={'User-Agent': 'PilvicsaAudit/1.0'})
            r.raise_for_status()
            r.encoding = 'utf-8'
            data = extract_content(r.text)
            data.update({'key': key, 'url': url})
            results[key] = data
            print(f'  title   : {data["title"][:70]}')
            print(f'  desc    : {data["meta_desc"][:70]}')
            print(f'  headings: {len(data["headings"])}  paras: {len(data["paragraphs"])}'
                  f'  phones: {len(data["phones"])}  maps: {len(data["maps_iframes"])}'
                  f'  social: {len(data["social_links"])}')
            if data['phones']:
                print(f'  phones  : {data["phones"]}')
            if data['maps_iframes']:
                print(f'  maps    : {len(data["maps_iframes"])} iframe(s) found')
        except Exception as e:
            print(f'  ERROR: {e}')
            results[key] = {'key': key, 'url': url, 'error': str(e)}
        time.sleep(1.5)

    LIVE_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n✓ Saved → {LIVE_JSON}')

    # Summary table
    print('\n' + '─' * 72)
    print(f'{"PAGE":<38}  {"H":>3}  {"P":>4}  {"PH":>3}  {"MAPS":>4}  {"SOC":>3}')
    print('─' * 72)
    for key, d in results.items():
        if 'error' in d:
            print(f'{key:<38}  ERROR: {d["error"][:28]}')
        else:
            print(f'{key:<38}  {len(d["headings"]):>3}  {len(d["paragraphs"]):>4}'
                  f'  {len(d["phones"]):>3}  {len(d["maps_iframes"]):>4}  {len(d["social_links"]):>3}')
    print('─' * 72)


# ── MODE 2 — DIFF ─────────────────────────────────────────────────────────────

def mode_diff():
    if not LIVE_JSON.exists():
        sys.exit('Run scrape first: audit/live_content.json not found')

    live_all = json.loads(LIVE_JSON.read_text(encoding='utf-8'))
    auto_patches, manual_items, correct_items = [], [], []
    md_auto, md_manual, md_ok = [], [], []

    for key, v2_file in V2_FILES.items():
        live = live_all.get(key, {})
        section_header = f'### {key}\n'

        if 'error' in live:
            manual_items.append({'page': key, 'reason': f'live fetch error: {live["error"]}'})
            md_manual.append(section_header + f'- Live fetch error: `{live["error"]}`\n')
            continue

        v2_path = ROOT / v2_file
        if not v2_path.exists():
            manual_items.append({'page': key, 'reason': f'v2 file missing: {v2_file}'})
            md_manual.append(section_header + f'- v2 file not yet created: `{v2_file}`\n')
            continue

        v2 = extract_content(v2_path.read_text(encoding='utf-8'))
        pa, pm, pk = [], [], []   # auto / manual / ok for this page

        # Meta description
        if live['meta_desc'] and live['meta_desc'] != v2['meta_desc']:
            patch = {'type': 'meta_desc', 'page': key, 'file': v2_file,
                     'old': v2['meta_desc'], 'new': live['meta_desc']}
            pa.append(patch)
        elif live['meta_desc'] == v2['meta_desc']:
            pk.append('meta_desc matches')

        # Meta title — manual only (SEO impact)
        if live['title'] and live['title'] != v2['title']:
            pm.append(f'title differs | live: `{live["title"][:55]}` | v2: `{v2["title"][:55]}`')
        elif live['title'] == v2['title']:
            pk.append('title matches')

        # Phones
        live_ph, v2_ph = set(live.get('phones', [])), set(v2.get('phones', []))
        for ph in live_ph - v2_ph:
            pa.append({'type': 'phone', 'page': key, 'file': v2_file, 'value': ph})
        if live_ph and not (live_ph - v2_ph):
            pk.append(f'phones match ({len(live_ph)})')

        # Google Maps iframes
        live_maps, v2_maps = live.get('maps_iframes', []), v2.get('maps_iframes', [])
        if live_maps and live_maps != v2_maps:
            for i, src in enumerate(live_maps):
                if src not in v2_maps:
                    pa.append({'type': 'maps_iframe', 'page': key, 'file': v2_file,
                               'old': v2_maps[i] if i < len(v2_maps) else '', 'new': src})
        elif live_maps and live_maps == v2_maps:
            pk.append(f'maps iframes match ({len(live_maps)})')

        # Social links
        live_soc = {s['platform']: s['href'] for s in live.get('social_links', [])}
        v2_soc   = {s['platform']: s['href'] for s in v2.get('social_links', [])}
        for plat, href in live_soc.items():
            if plat not in v2_soc or v2_soc[plat] != href:
                pa.append({'type': 'social_link', 'page': key, 'file': v2_file,
                           'platform': plat, 'old': v2_soc.get(plat, ''), 'new': href})
            else:
                pk.append(f'social/{plat} matches')

        # Copyright
        if live.get('copyright') and live['copyright'] != v2.get('copyright'):
            pa.append({'type': 'copyright', 'page': key, 'file': v2_file,
                       'old': v2.get('copyright', ''), 'new': live['copyright']})
        elif live.get('copyright') and live['copyright'] == v2.get('copyright'):
            pk.append('copyright matches')

        # Nav links — manual (structure may be intentionally different)
        live_nav = {a['href']: a['text'] for a in live.get('nav_links', [])}
        v2_nav   = {a['href']: a['text'] for a in v2.get('nav_links', [])}
        for href, txt in live_nav.items():
            if href not in v2_nav:
                pm.append(f'nav missing link: `{txt}` → `{href}`')
            elif v2_nav[href] != txt:
                pm.append(f'nav text differs: `{txt}` vs `{v2_nav[href]}`')

        # Paragraphs — auto if >60% word overlap with a v2 paragraph
        for lp in live.get('paragraphs', []):
            if len(lp) < 50:
                continue
            lwords = set(lp.lower().split())
            best_vp, best_score = None, 0.0
            for vp in v2.get('paragraphs', []):
                vw = set(vp.lower().split())
                if not vw:
                    continue
                score = len(lwords & vw) / max(len(lwords), len(vw))
                if score > best_score:
                    best_score, best_vp = score, vp
            if best_score > 0.6 and best_vp and best_vp != lp:
                pa.append({'type': 'paragraph', 'page': key, 'file': v2_file,
                           'old': best_vp, 'new': lp})
            elif best_score < 0.3 and len(lp) > 80:
                pm.append(f'paragraph not in v2: `{lp[:75]}…`')

        auto_patches.extend(pa)
        manual_items.extend({'page': key, 'reason': r} for r in pm)
        correct_items.extend({'page': key, 'item': i} for i in pk)

        if pa:
            md_auto.append(section_header + '\n'.join(
                f'- **{p["type"]}**: `{str(p.get("old",""))[:55]}` → `{str(p.get("new",""))[:55]}`'
                for p in pa) + '\n')
        if pm:
            md_manual.append(section_header + '\n'.join(f'- {r}' for r in pm) + '\n')
        if pk:
            md_ok.append(section_header + '\n'.join(f'- {i}' for i in pk) + '\n')

    # Write machine-readable diff for PATCH mode
    DIFF_JSON.write_text(
        json.dumps({'generated': datetime.now().isoformat(),
                    'auto_patches': auto_patches,
                    'manual_items': [i.get('reason', str(i)) for i in manual_items]},
                   ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    # Write human-readable report
    ts  = datetime.now().strftime('%Y-%m-%d %H:%M')
    md  = (f'# Pilvicsa v2 Content Diff\nGenerated: {ts}\n\n'
           f'**{len(auto_patches)} auto-patchable | '
           f'{len(manual_items)} manual review | '
           f'{len(correct_items)} already correct**\n\n'
           f'## Auto-patchable (safe to update automatically)\n\n'
           + ('\n'.join(md_auto) or '_None_') +
           '\n\n## Manual review required (Jorge must approve)\n\n'
           + ('\n'.join(md_manual) or '_None_') +
           '\n\n## Already correct (no action needed)\n\n'
           + ('\n'.join(md_ok) or '_None_') + '\n')
    DIFF_MD.write_text(md, encoding='utf-8')

    print(f'\n✓ {len(auto_patches)} auto-patchable  |  {len(manual_items)} manual review  |  {len(correct_items)} already correct')
    print(f'  Report → {DIFF_MD}')
    print(f'  Data   → {DIFF_JSON}')


# ── MODE 3 — PATCH helpers ────────────────────────────────────────────────────

def _in_protected_zone(html, pos):
    # Reject if inside <section id="hero"> or class="*hero*">
    for m in re.finditer(
        r'<section\b[^>]*(?:id=["\']hero["\']|class=["\'][^"\']*\bhero\b[^"\']*["\'])[^>]*>',
        html, re.I
    ):
        close = html.find('</section>', m.end())
        if close != -1 and m.start() <= pos <= close:
            return True
    # Reject if inside a <script> that contains gsap
    for m in re.finditer(r'<script\b[^>]*>', html, re.I):
        close = html.find('</script>', m.end())
        if close != -1 and m.start() <= pos <= close:
            if 'gsap' in html[m.end():close].lower():
                return True
    return False


def _apply_patch(html, patch):
    """Return (new_html, log_str) or (html, None) if nothing changed."""
    ptype = patch['type']

    if ptype == 'meta_desc':
        def _fix_desc(m):
            tag = m.group(0)
            return re.sub(r'(content=["\'])([^"\']*?)(["\'])',
                          lambda c: c.group(1) + patch['new'] + c.group(3), tag, count=1)
        new_html = re.sub(
            r'<meta\b[^>]*\bname=["\']description["\'][^>]*/?>',
            _fix_desc, html, count=1, flags=re.I
        )
        if new_html != html:
            return new_html, f'meta_desc: `{patch["old"][:55]}` → `{patch["new"][:55]}`'

    elif ptype == 'maps_iframe':
        old, new = patch.get('old', ''), patch.get('new', '')
        if old and old in html:
            return html.replace(old, new, 1), f'maps_iframe src replaced'

    elif ptype == 'social_link':
        old, new = patch.get('old', ''), patch.get('new', '')
        if old and old in html:
            new_html = html.replace(f'href="{old}"', f'href="{new}"', 1)
            if new_html == html:
                new_html = html.replace(f"href='{old}'", f"href='{new}'", 1)
            if new_html != html:
                return new_html, f'social/{patch.get("platform","")}: `{old[:55]}` → `{new[:55]}`'

    elif ptype == 'copyright':
        old, new = patch.get('old', ''), patch.get('new', '')
        if old and old in html:
            return html.replace(old, new, 1), f'copyright updated'

    elif ptype == 'paragraph':
        old, new = patch.get('old', ''), patch.get('new', '')
        if old and old in html:
            idx = html.find(old)
            if not _in_protected_zone(html, idx):
                return html.replace(old, new, 1), f'paragraph: `{old[:55]}…`'

    return html, None


# ── MODE 3 — PATCH ────────────────────────────────────────────────────────────

def mode_patch():
    if not DIFF_JSON.exists():
        sys.exit('Run diff first: audit/diff_data.json not found')

    patches = json.loads(DIFF_JSON.read_text(encoding='utf-8')).get('auto_patches', [])
    if not patches:
        print('No auto-patchable items. Nothing to do.')
        return

    by_file = {}
    for p in patches:
        by_file.setdefault(p['file'], []).append(p)

    log_lines     = [f'# Patch Log\nGenerated: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n']
    total_changes = 0
    patched_files = []

    for v2_file, file_patches in by_file.items():
        path = ROOT / v2_file
        if not path.exists():
            print(f'  SKIP (not found): {v2_file}')
            continue

        html = path.read_text(encoding='utf-8')
        bak  = BACKUP_DIR / (v2_file + '.bak')
        bak.write_text(html, encoding='utf-8')
        print(f'\n→ {v2_file}  [backup: {bak.name}]')

        file_log = [f'\n## {v2_file}']
        changed  = False

        for patch in file_patches:
            new_html, note = _apply_patch(html, patch)
            if note:
                print(f'  ✓ {note}')
                file_log.append(f'- {note}')
                html    = new_html
                changed = True
                total_changes += 1
            else:
                print(f'  – skipped ({patch["type"]}: pattern not matched or in protected zone)')

        if changed:
            path.write_text(html, encoding='utf-8')
            patched_files.append(v2_file)
            log_lines.extend(file_log)

    PATCH_LOG.write_text('\n'.join(log_lines), encoding='utf-8')
    print(f'\n✓ {total_changes} change(s) applied across {len(patched_files)} file(s)')
    print(f'  Log → {PATCH_LOG}')

    if not patched_files:
        return

    print('\nCommitting to dev2…')
    try:
        subprocess.run(['git', 'add'] + patched_files, cwd=ROOT, check=True)
        subprocess.run(
            ['git', 'commit', '-m',
             'content: migrate text content from live site via audit patch\n\n'
             'Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>'],
            cwd=ROOT, check=True
        )
        subprocess.run(['git', 'push', 'origin', 'dev2'], cwd=ROOT, check=True)
        print('✓ Pushed to dev2')
    except subprocess.CalledProcessError as e:
        print(f'  git error: {e}')


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else ''
    if   mode == 'scrape': mode_scrape()
    elif mode == 'diff':   mode_diff()
    elif mode == 'patch':  mode_patch()
    else:
        print('Usage: python scripts/audit_content.py [scrape|diff|patch]')
        sys.exit(1)
