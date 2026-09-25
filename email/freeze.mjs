// FROZEN email templates (owner approval, 25 Sept 2026): the visitor Raisey Scan results email, the internal NEW ENQUIRY
// sheet and the internal NEW RAISEY SCAN sheet. This check renders each one from fixed inputs and compares a SHA-256
// fingerprint with email/frozen.json. Any change to their HTML, text or subject fails the check.
//   node email/freeze.mjs            verify (exit 1 if a frozen template changed)
//   node email/freeze.mjs --update   re-snapshot ONLY after an explicit owner request to change a frozen template
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { renderEmail } from './render.mjs';
import { renderScanNotification, renderContactNotification } from './notify.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const copy = JSON.parse(readFileSync(join(here, '..', 'scan_copy.json'), 'utf8'));
const at = new Date('2026-09-25T12:00:00Z');
const scores = { medical: 3, digital: 2, brand: 1, search: 1, contentPov: 0, contentStrategy: 3, journeyBooking: 2, journeyLead: 1, journeyRelationship: 1 };
const scan = lang => ({ source: 'presence-scan', lang, name: 'Dr Camille Martin', email: 'camille@example.org', web: '@cliniquemartin', specialty: 'Dermatologist', practitioner_tier: 'tier1',
  scan: { answers: { growth: ['patients', 'visibility'], treatments: ['fillers', 'skinboosters', 'other'] }, other: { treatments: 'Lasers' }, scores } });
const contact = lang => ({ source: 'contact', lang, name: 'Dr Sarah Cohen', clinic: 'Maison Cohen', email: 'sarah@example.org', phone: '+33 6 12 34 56 78', specialty: 'Aesthetic physician',
  practitioner_tier: 'tier1', interest: 'founder', message: 'Hello,\nsecond line' });
const h = m => createHash('sha256').update(m.subject + '\n' + m.html + '\n' + m.text).digest('hex');
const cur = {};
for (const lang of ['en', 'fr']) {
  const base = 'https://raiseylab.com/' + (lang === 'fr' ? 'fr/' : '');
  cur['visitor-results-' + lang] = h(renderEmail(copy, scan(lang), { ctaUrl: base + '#contact', privacyUrl: base + (lang === 'fr' ? 'confidentialite.html' : 'privacy.html') }));
  cur['internal-new-raisey-scan-' + lang] = h(renderScanNotification(copy, scan(lang), { receivedAt: at }));
  cur['internal-new-enquiry-' + lang] = h(renderContactNotification(contact(lang), { receivedAt: at }));
}
const file = join(here, 'frozen.json');
if (process.argv.includes('--update')) { writeFileSync(file, JSON.stringify(cur, null, 1) + '\n'); console.log('frozen snapshot updated'); process.exit(0); }
const frozen = JSON.parse(readFileSync(file, 'utf8'));
const changed = Object.keys(cur).filter(k => cur[k] !== frozen[k]);
console.log(changed.length ? 'FROZEN EMAIL TEMPLATE CHANGED: ' + changed.join(', ') : 'frozen email templates intact (6 renders: visitor results, NEW RAISEY SCAN, NEW ENQUIRY × EN/FR)');
process.exit(changed.length ? 1 : 0);
