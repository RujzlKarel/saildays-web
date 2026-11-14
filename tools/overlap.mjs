// Kontrola po zmene vzhledu: nadpis, text a tlacitka uvodu nesmi prekryvat fotku, zadny vodorovny scroll, na sirkach 360-1920 px
// ve vsech 5 jazycich. Playwright z webdesigner skillu (~/.claude/skills/webdesigner/scripts/node_modules), server: cd dist && python3 -m http.server 8765
//   node tools/overlap.mjs http://127.0.0.1:8765
import { chromium } from '/Users/miniai/.claude/skills/webdesigner/scripts/node_modules/playwright/index.mjs';
const base = process.argv[2] || 'http://127.0.0.1:8765';
const widths = [360, 390, 414, 600, 768, 820, 821, 1024, 1280, 1440, 1680, 1920];
const langs = ['', 'cs/', 'de/', 'fr/', 'es/'];
const browser = await chromium.launch();
let bad = 0;
for (const lang of langs) {
  for (const w of widths) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
    const page = await ctx.newPage();
    await page.route(/(googletagmanager\.com|google-analytics\.com)/, (r) => r.abort());
    await page.goto(base + '/' + lang, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const r = await page.evaluate(() => {
      const box = (el) => { const b = el.getBoundingClientRect(); return { l: b.left, t: b.top, r: b.right, b: b.bottom }; };
      const photo = box(document.querySelector('.hero-photo img'));
      const texts = ['.hero h1', '.hero .btn', '.hero .more', '.hero .note', '.hero-copy p'].flatMap((s) => [...document.querySelectorAll(s)].map(box));
      const inter = texts.filter((t) => t.l < photo.r - 0.5 && t.r > photo.l + 0.5 && t.t < photo.b - 0.5 && t.b > photo.t + 0.5);
      const band = document.querySelector('.band img').getBoundingClientRect();
      const hdr = document.querySelector('.header-row').getBoundingClientRect();
      return { inter: inter.length, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
        photoH: Math.round(photo.b - photo.t), photoW: Math.round(photo.r - photo.l), photoTop: Math.round(photo.t),
        bandH: Math.round(band.height), hdrH: Math.round(hdr.height) };
    });
    const ok = r.inter === 0 && r.sw <= r.cw;
    if (!ok) bad++;
    console.log(`${ok ? 'ok  ' : 'FAIL'} ${lang || 'en/'} ${w}px prunik=${r.inter} scroll=${r.sw}/${r.cw} foto=${r.photoW}x${r.photoH}@${r.photoTop} pas=${r.bandH} hlavicka=${r.hdrH}`);
    await ctx.close();
  }
}
await browser.close();
process.exit(bad ? 1 : 0);
