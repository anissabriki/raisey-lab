// Guards the rules agreed for the results email. Exit code 1 on any violation.
//   node email/check.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { renderEmail, validate, DIMS } from './render.mjs';
import { SAMPLES } from './samples.mjs';

const copy = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'scan_copy.json'), 'utf8'));
const bad = [];
const FORBIDDEN = [/diagnostic/i, /search visibility/i, /you should/i, /vous devriez/i, /your website shows/i, /your online presence demonstrates/i,
  /(?:presence|raisey) review\b[^.]{0,30}\b(sent|delivered|instant|automated|automatisé|envoyé|instantané)\b/i];
for (const [name, payload] of Object.entries(SAMPLES)) {
  const r = renderEmail(copy, payload, { ctaUrl: 'https://x.invalid/', privacyUrl: 'https://x.invalid/p' });
  const lang = payload.lang, c = copy[lang];
  const plain = r.text;
  for (const re of FORBIDDEN) if (re.test(plain)) bad.push(`${name}: forbidden phrase ${re}`);
  if (!plain.includes(c.transp.replace(/ ([?!:;])/g, ' $1'))) bad.push(name + ': transparency line missing');
  if (!/mailing list|liste de diffusion/.test(plain)) bad.push(name + ': one-off / no-mailing-list notice missing');
  if (!r.html.includes('lang="' + lang + '"')) bad.push(name + ': wrong html lang');
  // Q7/Q8 are context only: changing them must not change anything about the scored parts.
  const other = structuredClone(payload); other.scan.answers = { growth: ['team', 'market'], treatments: ['surgery'] };
  const a = renderEmail(copy, payload), b = renderEmail(copy, other);
  const scored = h => h.slice(h.indexOf(c.email.hOverall.slice(0, 8)), h.indexOf(c.email.hContext.slice(0, 8)) > 0 ? h.indexOf(c.email.hContext.slice(0, 8)) : undefined);
  if (r.tier !== b.tier) bad.push(name + ': context changed the tier');
  if (a.text.split(c.email.hNext.toUpperCase())[0].split(c.email.hDims.toUpperCase())[1].split(c.email.hContext.toUpperCase())[0] !==
      b.text.split(c.email.hNext.toUpperCase())[0].split(c.email.hDims.toUpperCase())[1].split(c.email.hContext.toUpperCase())[0]) bad.push(name + ': context changed the scored sections');
}
// untrusted input must be rejected or neutralised
if (validate({ scan: { scores: { medical: 9 } } }, copy).ok) bad.push('out-of-range score accepted');
const evil = structuredClone(SAMPLES['strong-en']); evil.scan.other.treatments = '<script>alert(1)</script>'; evil.scan.answers.treatments = ['other'];
const html = renderEmail(copy, evil).html; if (/<script/i.test(html.replace(/<title>.*?<\/title>/, ''))) bad.push('unescaped input reached the HTML');
// scoring rules (shared source: scan_scoring.mjs) and parity with the copy inlined in the site
import { dimensions, levelOf, tierOf, nuances, FACETS } from '../scan_scoring.mjs';
const F = (o = {}) => ({ medical: 2, digital: 2, brand: 2, search: 2, contentPov: 2, contentStrategy: 2, journeyBooking: 2, journeyLead: 2, journeyRelationship: 2, ...o });
if (Object.keys(dimensions(F())).length !== 6 || FACETS.length !== 9) bad.push('radar must have exactly 6 dimensions fed by 9 scored questions');
if (levelOf(dimensions(F({ contentPov: 3, contentStrategy: 0 })).content) === 'established') bad.push('posting without direction reached Established');
if (levelOf(dimensions(F({ contentPov: 3, contentStrategy: 3 })).content) !== 'established') bad.push('content 3+3 should be Established');
if (levelOf(dimensions(F({ journeyBooking: 1, journeyLead: 1, journeyRelationship: 3 })).journey) !== 'elevate') bad.push('a CRM alone compensated for weak booking + follow-up');
if (levelOf(dimensions(F({ journeyBooking: 3, journeyLead: 3, journeyRelationship: 3 })).journey) !== 'established') bad.push('journey 3/3/3 should be Established');
if (nuances(F({ contentPov: 3, contentStrategy: 1 }))[0]?.key !== 'povStrong') bad.push('content nuance (point of view strong) missing');
if (nuances(F({ journeyBooking: 3, journeyLead: 1, journeyRelationship: 3 }))[0]?.key !== 'lead') bad.push('journey nuance (lead weakest) missing');
if (nuances(F({ journeyBooking: 2, journeyLead: 3, journeyRelationship: 2 })).length) bad.push('nuance shown without a 2-point gap');
{
  const html = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'index.html'), 'utf8');
  const code = html.slice(html.indexOf('/* SCAN_SCORING:begin'), html.indexOf('/* SCAN_SCORING:end'));
  const site = new Function(code + '; return { dimensions, levelOf, tierOf };')();
  for (let n = 0; n < 4000; n++) {
    const f = Object.fromEntries(FACETS.map(k => [k, Math.floor(Math.random() * 4)]));
    const a = JSON.stringify(dimensions(f)), b = JSON.stringify(site.dimensions(f));
    if (a !== b || tierOf(dimensions(f)) !== site.tierOf(site.dimensions(f))) { bad.push('site and email scoring differ for ' + JSON.stringify(f)); break; }
  }
}
// every dimension x level has two sentences in both languages, and no observation claims
for (const lang of ['en', 'fr']) for (const k of DIMS) for (const lv of ['established', 'potential', 'elevate']) {
  const t = copy[lang].I[k][lv]; if (t.length !== 2 || t.some(s => !s.trim())) bad.push(`${lang}.${k}.${lv}: needs 2 sentences`);
  if (!/^(Your answers|Your responses|Vos réponses)/.test(t[0])) bad.push(`${lang}.${k}.${lv}: must open with an answer-based phrase`);
}
console.log(bad.length ? 'FAILED:\n - ' + bad.join('\n - ') : 'email checks passed (' + Object.keys(SAMPLES).length + ' samples, EN + FR)');
process.exit(bad.length ? 1 : 0);
