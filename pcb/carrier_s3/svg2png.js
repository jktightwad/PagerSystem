const { chromium } = require('playwright');
(async () => {
  const [,, src, dst, scale] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: Number(scale || 1.5) });
  const fs = require('fs'); const svg = fs.readFileSync(src, 'utf8');
  await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  const el = await p.$('svg'); await el.screenshot({ path: dst, omitBackground: false });
  await b.close();
})();
