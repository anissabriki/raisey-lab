// Reads the website leads kept by the form endpoint (Cloudflare KV "LEADS") and writes them as Kinassay CRM
// prospect records, one JSON file each, ready to be added to the CRM's database.
//   node worker/sync_leads.mjs <out-dir> [--since 2026-10-07]
// Read-only on Cloudflare: nothing is deleted there (entries expire on their own after 24 months).
import { execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const out = process.argv[2];
if (!out) { console.error('usage: node worker/sync_leads.mjs <out-dir> [--since YYYY-MM-DD]'); process.exit(2); }
const sinceArg = process.argv.indexOf('--since');
const since = sinceArg > -1 ? process.argv[sinceArg + 1] : '';
const cwd = dirname(fileURLToPath(import.meta.url));
const wrangler = (...args) => execFileSync('npx', ['wrangler', 'kv', ...args, '--binding', 'LEADS', '--remote'], { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });

const keys = JSON.parse(wrangler('key', 'list', '--prefix', 'lead:')).map(k => k.name).filter(k => !since || k.slice(5, 15) >= since);
mkdirSync(out, { recursive: true });
const SOURCE = { scan: 'kinassay.com — Kinassay Scan', contact: 'kinassay.com — Contact form' };
const manifest = [];
for (const key of keys.sort()) {
  const l = JSON.parse(wrangler('key', 'get', key, '--text'));
  const day = l.at.slice(0, 10);
  const id = 'lead-' + key.slice(5).replace(/[^0-9A-Za-z]+/g, '-').replace(/-+$/, '');
  const web = l.web || '';
  const ig = /^@|instagram\.com/i.test(web);
  const scores = l.scores && Object.keys(l.scores).length ? Object.entries(l.scores).map(([k, v]) => k + ' ' + v).join(', ') : '';
  const note = [
    l.kind === 'scan' ? `Kinassay Scan completed (${l.lang.toUpperCase()}), results emailed.` : `Contact form (${l.lang.toUpperCase()})${l.interest ? ', came from: ' + l.interest : ''}.`,
    l.scanTier ? 'Scan level: ' + l.scanTier + (scores ? ' · scores: ' + scores : '') : '',
    l.message ? 'Message: ' + l.message : '',
    l.tier ? 'Practitioner type: ' + l.tier : '',
  ].filter(Boolean).join('\n');
  const rec = {
    id, name: l.name, clinic: l.clinic || '', city: '', country: '',
    email: l.email, phone: l.phone || '', phoneNote: '',
    website: !ig && web ? { url: /^https?:\/\//.test(web) ? web : 'https://' + web, status: 'found' } : { url: '', status: 'not_found' },
    instagram: ig ? { url: web.startsWith('@') ? 'https://www.instagram.com/' + web.slice(1) + '/' : web, status: 'found' } : { url: '', status: 'not_found' },
    linkedin: { url: '', status: 'not_found' },
    specialty: l.specialty || '', specialtyDetail: '', stage: 'INBOUND', priority: 'P1', tier: 'HOT', score: null,
    source: SOURCE[l.kind] + ' — ' + day, leadSource: SOURCE[l.kind], leadKey: key,
    salesAngle: '', status: '', lastContact: '', nextAction: 'Reply within 24 h', nextActionDate: day,
    notes: [{ date: day, text: note }], proposalValue: null, probability: null, files: [], redFlag: '', reviewDismissed: false,
    activities: [], outreachRank: null, salesBrief: null, clinicShared: [], validationWave: null, salesValidation: null, deal: null, eventLinks: [],
  };
  writeFileSync(join(out, id + '.json'), JSON.stringify(rec));
  manifest.push({ id, email: l.email, name: l.name, kind: l.kind, at: l.at });
}
writeFileSync(join(out, 'manifest.json'), JSON.stringify(manifest, null, 1));
console.log(`${manifest.length} lead(s) written to ${out}`);
