const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [svgPath, pdfPath] = process.argv.slice(2);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const W = svg.match(/width="([\d.]+)(pt|px)?"/), H = svg.match(/height="([\d.]+)(pt|px)?"/);
  const k = (W[2] === 'pt') ? 4 / 3 : 1, w = Math.ceil(+W[1] * k), h = Math.ceil(+H[1] * k);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await p.pdf({ path: pdfPath, width: w + 'px', height: h + 'px', printBackground: true, pageRanges: '1' });
  await b.close(); console.log(pdfPath, w, h);
})();
