// Renders the sample emails to email/preview/*.html so they can be reviewed in a browser before any provider is wired.
//   node email/preview.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { renderEmail } from './render.mjs';
import { SAMPLES } from './samples.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const copy = JSON.parse(readFileSync(join(here, '..', 'scan_copy.json'), 'utf8'));
mkdirSync(join(here, 'preview'), { recursive: true });
let index = '<!doctype html><meta charset="utf-8"><title>Scan email previews</title><body style="font:16px Arial;margin:40px"><h1>Raisey Scan results email: previews</h1><ul>';
for (const [name, payload] of Object.entries(SAMPLES)) {
  const r = renderEmail(copy, payload, { ctaUrl: 'https://example.invalid/#contact', privacyUrl: 'https://example.invalid/privacy.html' });
  writeFileSync(join(here, 'preview', name + '.html'), r.html);
  writeFileSync(join(here, 'preview', name + '.txt'), 'Subject: ' + r.subject + '\n\n' + r.text);
  index += `<li><a href="${name}.html">${name}</a> · tier ${r.tier} · <a href="${name}.txt">text version</a></li>`;
}
writeFileSync(join(here, 'preview', 'index.html'), index + '</ul></body>');
console.log('previews written to email/preview/');
