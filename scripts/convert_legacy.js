/**
 * Converts /c/xampp/htdocs/pilvicsa/pilvicsa-data.js  →  data/products.json
 * Maps old JS object schema to the v2 JSON schema defined in PILVICSA_CLAUDE_CODE_BRIEF.md §5
 */
const fs   = require('fs');
const path = require('path');
const vm   = require('vm');

const SRC  = 'C:\\xampp\\htdocs\\pilvicsa\\pilvicsa-data.js';
const DEST = path.join(__dirname, '..', 'data', 'products.json');

// pagina remap: old → new
const PAGE_MAP = { frutales: 'frutalesforestales' };

// specs key → v2 field (all lowercased for matching)
const SPEC_MAP = {
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
};

// Extra resistance keys that append into resistencias with a prefix label
const RESIST_KEYS = { 'resist. alta': 'Alta', 'resist. intermedia': 'Intermedia' };

function parseSpecs(raw) {
  const out = { color:'', forma:'', sistema:'', densidad:'', resistencias:'', ciclo:'', tamano:'', nota:'' };
  if (!raw) return out;

  const notaParts = [];
  for (const pair of raw.split('||')) {
    const sep = pair.indexOf('|');
    if (sep === -1) continue;
    const k   = pair.slice(0, sep).trim();
    const kl  = k.toLowerCase();
    const val = pair.slice(sep + 1).trim().replace(/&quot;/g, '"');

    if (SPEC_MAP[kl]) {
      const field = SPEC_MAP[kl];
      out[field] = out[field] ? out[field] + '; ' + val : val;
    } else if (RESIST_KEYS[kl]) {
      const label = RESIST_KEYS[kl] + ': ' + val;
      out.resistencias = out.resistencias ? out.resistencias + '; ' + label : label;
    } else {
      // goes to nota
      notaParts.push(k + ': ' + val);
    }
  }
  out.nota = notaParts.join('; ');
  return out;
}

// Load the legacy JS file via vm to avoid eval scope pollution
const code = fs.readFileSync(SRC, 'utf8');
const ctx  = {};
vm.createContext(ctx);
vm.runInContext(code, ctx);
const legacy = ctx.PILV_DB;

const products = legacy.map(p => {
  const specs  = parseSpecs(p.specs);
  const pagina = PAGE_MAP[p.page] || p.page;
  const estado = p.status === 'potential' ? 'potential' : 'confirmed';
  const imagen = p.img ? path.basename(p.img) : '';
  // Merge specs.nota with any explicit note from old record
  const nota   = [specs.nota, p.note].filter(Boolean).join('; ');

  return {
    id:           p.id,
    nombre:       p.name,
    latin:        p.latin || '',
    categoria:    p.cat,
    pagina,
    pageLabel:    p.pageLabel,
    color:        specs.color,
    forma:        specs.forma,
    sistema:      specs.sistema,
    densidad:     specs.densidad,
    resistencias: specs.resistencias,
    ciclo:        specs.ciclo,
    tamano:       specs.tamano,
    imagen,
    youtube_id:   '',
    fb_video_id:  '',
    ig_post_id:   '',
    estado,
    nota,
  };
});

fs.writeFileSync(DEST, JSON.stringify(products, null, 2));
console.log(`Written ${products.length} products to ${DEST}`);
