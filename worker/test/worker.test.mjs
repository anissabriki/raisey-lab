// Offline tests: runs the real Worker with a fake Resend and fake rate limiters.   node worker/test/worker.test.mjs
import worker, { RateLimiter } from '../src/index.mjs';
let sent = [], resendStatus = 200, waits = [];
globalThis.fetch = async (url, init) => { sent.push({ url, ...JSON.parse(init.body), auth: init.headers.Authorization }); return new Response('{}', { status: resendStatus }); };
// In-memory Durable Object namespace running the real RateLimiter class (one instance + storage per key)
const doNamespace = () => { const objs = {}; return { idFromName: n => n, get: id => objs[id] || (objs[id] = (() => { const store = new Map();
  const o = new RateLimiter({ storage: { get: async k => store.get(k), put: async (k, v) => { store.set(k, v); } } }); return { fetch: u => o.fetch(new Request(u)) }; })()) }; };
const mkEnv = (o = {}) => ({ RESEND_API_KEY: 're_test_dummy', ALLOWED_ORIGINS: 'https://raiseylab.com,https://www.raiseylab.com', FROM_EMAIL: 'Raisey Lab <hello@raiseylab.com>',
  TO_EMAIL: 'hello@raiseylab.com', SITE_URL: 'https://raiseylab.com', LIMITER: doNamespace(), ...o });
const ctx = { waitUntil: p => waits.push(p) };
let ip = 0;
const call = async (body, { env = mkEnv(), origin = 'https://raiseylab.com', method = 'POST', path = '/submit', type = 'application/json', sameIp = false } = {}) => {
  sent = []; waits = [];
  const headers = { Origin: origin, 'Content-Type': type, 'CF-Connecting-IP': sameIp ? '9.9.9.9' : '10.0.0.' + (++ip) };
  const r = await worker.fetch(new Request('https://raisey-forms.test' + path, { method, headers, body: method === 'POST' ? (typeof body === 'string' ? body : JSON.stringify(body)) : undefined }), env, ctx);
  await Promise.all(waits);
  return { status: r.status, body: await r.text(), acao: r.headers.get('Access-Control-Allow-Origin'), sent };
};
const scores = { medical: 3, digital: 2, brand: 1, search: 1, contentPov: 0, contentStrategy: 3, journeyBooking: 2, journeyLead: 1, journeyRelationship: 1 };
const scan = lang => ({ name: 'Dr Test', email: 'visitor@example.org', specialty: '', web: '@testclinic', scan: { answers: { growth: ['visibility'], treatments: ['other'] }, other: { treatments: 'lasers' }, tier: 'potential', scores }, source: 'presence-scan', lang, _t: 90000 });
const contact = lang => ({ interest: 'founder', name: 'Dr Test', clinic: 'Test Clinic', email: 'Visitor@Example.org', phone: '0600000000', specialty: 'Dermatologist', message: 'Hello\nsecond line', source: 'contact', lang, _t: 20000 });
let pass = 0, fail = 0;
const ok = (name, cond, info = '') => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + name + (cond || !info ? '' : '  → ' + info)); };

// transport / CORS
let r = await call(null, { method: 'OPTIONS' }); ok('preflight from raiseylab.com → 204 + CORS', r.status === 204 && r.acao === 'https://raiseylab.com');
r = await call(null, { method: 'OPTIONS', origin: 'https://raiseylab.club' }); ok('preflight from raiseylab.club → 403', r.status === 403);
r = await call(contact('en'), { origin: 'https://evil.example' }); ok('POST from unknown origin → 403, nothing sent', r.status === 403 && !r.sent.length);
r = await call(contact('en'), { origin: 'https://www.raiseylab.com' }); ok('POST from www.raiseylab.com allowed', r.status === 200);
r = await call(null, { method: 'GET' }); ok('GET → 405', r.status === 405);
r = await call(contact('en'), { path: '/' }); ok('wrong path → 404', r.status === 404);
r = await call('name=x', { type: 'application/x-www-form-urlencoded' }); ok('non-JSON → 415', r.status === 415);
r = await call('{bad json'); ok('malformed JSON → 400', r.status === 400);
r = await call({ ...contact('en'), message: 'x'.repeat(40000) }); ok('oversized body → 413', r.status === 413 && !r.sent.length);
r = await call(contact('en'), { env: mkEnv({ RESEND_API_KEY: '' }) }); ok('missing secret → 500, nothing sent', r.status === 500 && !r.sent.length);

// contact
for (const lang of ['en', 'fr']) {
  r = await call(contact(lang)); const m = r.sent[0] || {};
  ok(`contact ${lang}: 200, one email`, r.status === 200 && r.sent.length === 1, r.status + ' ' + r.body);
  ok(`contact ${lang}: to hello@, from Raisey Lab <hello@>, reply-to visitor`, m.to?.[0] === 'hello@raiseylab.com' && m.from === 'Raisey Lab <hello@raiseylab.com>' && m.reply_to === 'visitor@example.org');
  ok(`contact ${lang}: HTML lead sheet + text carry every field`, /NEW ENQUIRY/.test(m.html) && ['Dr Test', 'Test Clinic', 'visitor@example.org', '0600000000', 'Dermatologist', 'Talk to the founder', 'second line', lang === 'fr' ? 'French' : 'English'].every(s => m.text.includes(s) && m.html.includes(s)) && m.html.includes('second line') && m.html.includes('Reply to lead'));
  ok(`contact ${lang}: API key only in Authorization header`, m.auth === 'Bearer re_test_dummy' && !JSON.stringify({ ...m, auth: 0 }).includes('re_test'));
}
r = await call({ ...contact('en'), email: 'not-an-email' }); ok('contact bad email → 400', r.status === 400 && !r.sent.length);
r = await call({ ...contact('en'), clinic: '' }); ok('contact missing clinic → 400', r.status === 400 && !r.sent.length);
r = await call({ ...contact('en'), name: 'Evil\r\nBcc: x@y.z <script>', clinic: 'A\nB' }); ok('header/HTML injection neutralised (one-line subject, no < >)', r.status === 200 && !/[\r\n<>]/.test(r.sent[0].subject) && !/<script/.test(r.sent[0].text), r.sent[0]?.subject);
r = await call({ ...contact('en'), name: '<img src=x onerror=alert(1)>', message: '<a href="javascript:x">click</a>\n"quoted"' }); ok('lead sheet escapes visitor HTML (no injected tags/links)', r.status === 200 && (r.sent[0].html.match(/<img\b[^>]*>/gi) || []).every(t => t.includes('src="cid:raisey-mark"')) && !/<a href="javascript|<script/i.test(r.sent[0].html) && !/<img\b|<script/i.test(r.sent[0].text), '');
r = await call({ ...scan('en'), web: 'javascript:alert(1)' }); ok('website field never becomes a javascript: link', r.status === 200 && !/href="javascript/i.test(r.sent[1].html));

// scan
for (const lang of ['en', 'fr']) {
  r = await call(scan(lang)); const [v, n] = r.sent;
  ok(`scan ${lang}: 200, visitor email + founder notification`, r.status === 200 && r.sent.length === 2, r.status + ' ' + r.body);
  ok(`scan ${lang}: results to visitor, reply-to hello@`, v?.to?.[0] === 'visitor@example.org' && v.reply_to === 'hello@raiseylab.com' && v.from === 'Raisey Lab <hello@raiseylab.com>');
  ok(`scan ${lang}: correct language subject + html + text`, (lang === 'fr' ? /Raisey Scan/.test(v.subject) && /résultats/.test(v.subject) : v.subject === 'Your Raisey Scan results') && v.html.includes('<html lang="' + lang + '"') && v.text.length > 500, v?.subject);
  ok(`scan ${lang}: links point to raiseylab.com in the right language`, v.html.includes('https://raiseylab.com/' + (lang === 'fr' ? 'fr/#contact' : '#contact')) && v.html.includes(lang === 'fr' ? 'https://raiseylab.com/fr/confidentialite.html' : 'https://raiseylab.com/privacy.html'));
  ok(`scan ${lang}: no placeholders / legacy brand`, !/\{\w+\}|undefined|NaN|Presence (Lab|Scan|Review)|example\.invalid/.test(v.html + v.text));
  ok(`scan ${lang}: notification to hello@, reply-to visitor, HTML lead sheet (result, 6 dimensions, context, date, reply)`, n?.to?.[0] === 'hello@raiseylab.com' && n.reply_to === 'visitor@example.org' && /NEW RAISEY SCAN/.test(n.html) && n.html.includes('@testclinic') && ['Medical Authority','Digital Authority','Brand Expression','Discoverability','Content Potential','Patient Journey'].every(d => n.html.includes(d)) && n.html.includes('Other (their words)') && n.html.includes('lasers') && n.html.includes('(Paris)') && n.html.includes('Reply to lead') && n.text.includes('SIX DIMENSIONS'));
}
r = await call({ ...scan('en'), scan: { ...scan('en').scan, scores: { ...scores, medical: 9 } } }); ok('scan with out-of-range score → 400', r.status === 400 && !r.sent.length);
r = await call({ ...scan('en'), web: '' }); ok('scan missing website → 400', r.status === 400);
r = await call({ ...scan('en'), scan: { ...scan('en').scan, tier: 'established', dimensions: { medical: 3, digital: 3, brand: 3, search: 3, content: 3, journey: 3 } } });
ok('scan: browser-sent tier/dimensions ignored (recomputed from scores)', r.sent[0].text.includes('Strong Potential'));
r = await call({ ...scan('en'), source: 'other' }); ok('unknown source → 400', r.status === 400);

// The old circular symbol is deprecated: no image and no attachment in any email (wordmark only, until the & monogram files exist)
for (const lang of ['en', 'fr']) {
  for (const payload of [scan(lang), contact(lang)]) {
    r = await call(payload);
    ok(`no legacy symbol ${lang} ${payload.source}: no <img>, no attachment, RAISEY LAB wordmark present`, r.sent.length >= 1 && r.sent.every(m => !/<img\b/i.test(m.html) && !m.attachments && /letter-spacing:\.3em;text-transform:uppercase[^>]*>Raisey Lab</.test(m.html)));
  }
}

// abuse
r = await call({ ...contact('en'), website_url: 'http://spam' }); ok('honeypot filled → 200 but nothing sent', r.status === 200 && !r.sent.length);
r = await call({ ...contact('en'), _t: 800 }); ok('submitted in < 3 s → 200 but nothing sent', r.status === 200 && !r.sent.length);
{ const env = mkEnv(); const st = []; for (let i = 0; i < 8; i++) st.push((await call(contact('en'), { env, sameIp: true })).status);
  ok('per-IP limit: exactly 5 per minute, then 429', st.join() === '200,200,200,200,200,429,429,429', st.join()); }
{ const env = mkEnv(); const st = []; for (let i = 0; i < 4; i++) st.push((await call(scan('en'), { env })).status);
  ok('per-recipient limit: 2 results emails per minute, then 429', st.join() === '200,200,429,429', st.join()); }
resendStatus = 500; r = await call(contact('en')); ok('Resend failure → 502 (site shows its error message)', r.status === 502); resendStatus = 200;
r = await call(scan('en'), { env: mkEnv({ LIMITER: undefined }) }); ok('works if the limiter binding is absent (fails open, logged)', r.status === 200);
{ const env = mkEnv(); const st = []; for (let i = 0; i < 6; i++) st.push((await call('{"source":"contact"}', { env, sameIp: true })).status);
  ok('invalid requests also count towards the per-IP limit', st.join() === '400,400,400,400,400,429', st.join()); }
{ const o = new RateLimiter({ storage: { get: async () => [Date.now() - 61_000, Date.now() - 61_000, Date.now() - 61_000, Date.now() - 61_000, Date.now() - 61_000], put: async () => {} } });
  ok('window slides: hits older than 60 s no longer count', (await o.fetch(new Request('https://limiter/hit?limit=5&window=60000'))).status === 200); }

console.log(`\n${pass} passed, ${fail} failed`); process.exit(fail ? 1 : 0);
