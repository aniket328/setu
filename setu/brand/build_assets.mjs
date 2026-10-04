// Setu brand assets -> every Twenty icon path, at each file's own pixel size (names kept so merges never touch callers).
// Run: node setu/brand/build_assets.mjs   (needs `playwright` + system Chrome)
import { chromium } from 'playwright';
import { readdirSync, statSync, writeFileSync, readFileSync } from 'fs';
import { execFileSync } from 'child_process';
import path from 'path';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const C = '#f472b6', TILE = '#1f0c17';
// a bridge: deck + three hangers (faint), the arch that carries them, and the two parties it joins
export const glyph = (c = C) => `<g transform="translate(0 -4)"><g stroke="${c}" stroke-linecap="round" opacity="0.5"><line x1="22" y1="66" x2="78" y2="66" stroke-width="5"/><line x1="36" y1="51" x2="36" y2="66" stroke-width="3"/><line x1="50" y1="45" x2="50" y2="66" stroke-width="3"/><line x1="64" y1="51" x2="64" y2="66" stroke-width="3"/></g><path d="M22 66Q50 24 78 66" stroke="${c}" stroke-width="7" stroke-linecap="round" fill="none"/><circle cx="22" cy="66" r="5.5" fill="${c}"/><circle cx="78" cy="66" r="5.5" fill="${c}"/></g>`;
const tile = (w, h = w) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet"><rect width="100" height="100" rx="22" fill="${TILE}"/>${glyph()}</svg>`;
const FONT = `Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif`;
const og = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#0b0809"/><circle cx="980" cy="120" r="320" fill="${C}" opacity="0.07"/><g transform="translate(110 175) scale(1.9)"><rect width="100" height="100" rx="22" fill="${TILE}"/>${glyph()}</g><text x="340" y="290" font-family="${FONT}" font-size="120" font-weight="700" letter-spacing="-4" fill="#f5f5f4">Setu</text><text x="640" y="290" font-family="'Kohinoor Devanagari','Noto Sans Devanagari',sans-serif" font-size="80" fill="${C}">सेतु</text><text x="344" y="350" font-family="${FONT}" font-size="34" fill="#a8a29e">The CRM that bridges you and your customers.</text><text x="112" y="545" font-family="${FONT}" font-size="22" letter-spacing="5" fill="#78716c">BY CWI STUDIO</text></svg>`;

const jobs = [];
const walk = (d) => readdirSync(d).flatMap(f => { const p = path.join(d, f); return statSync(p).isDirectory() ? walk(p) : [p]; });
for (const f of walk(path.join(ROOT, 'packages/twenty-front/public/images/icons')).filter(f => f.endsWith('.png'))) {
  const [w, h] = execFileSync('sips', ['-g', 'pixelWidth', '-g', 'pixelHeight', f]).toString().match(/\d+/g).slice(-2).map(Number);
  jobs.push({ svg: tile(Math.min(w, h)), w, h, file: f });
}
const out = (rel) => path.join(ROOT, rel);
jobs.push({ svg: og, w: 1200, h: 630, file: out('packages/twenty-front/public/images/setu-og.png'), opaque: true });
writeFileSync(out('packages/twenty-front/public/images/integrations/twenty-logo.svg'), tile(100));
writeFileSync(out('setu/brand/setu-mark.svg'), tile(512));

const b = await chromium.launch({ channel: 'chrome' });
for (const j of jobs) {
  const p = await b.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
  const svg = j.svg.replace(/width="\d+" height="\d+"/, `width="${j.w}" height="${j.h}"`);
  await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
  await p.screenshot({ path: j.file, omitBackground: !j.opaque, clip: { x: 0, y: 0, width: j.w, height: j.h } });
  await p.close();
}
await b.close();
console.log('icons written:', jobs.length);
