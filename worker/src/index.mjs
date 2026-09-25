// Raisey Lab — form endpoint (Cloudflare Worker).
// Receives the website's two forms and sends email through Resend:
//   source "contact"        -> notification to TO_EMAIL (hello@raiseylab.com), Reply-To = the visitor
//   source "presence-scan"  -> the visitor's Raisey Scan results (rendered here from scores only) + a notification to TO_EMAIL
// ("presence-scan" is the payload label the site has always sent; it is internal, never shown to visitors.)
//
// Secrets: RESEND_API_KEY is a Cloudflare secret (`wrangler secret put RESEND_API_KEY`). It is never in this repository
// or in the website. Everything else is public configuration in wrangler.toml [vars].
//
// Abuse protection: allowed Origins only (CORS), JSON only, size cap, strict field validation, honeypot field,
// minimum fill time, EXACT per-IP and per-recipient rate limits (one Durable Object counter per key), no HTML ever accepted
// from the browser, and generic error messages. Logs never contain personal data.
import { renderEmail, validate } from '../../email/render.mjs';
import { renderScanNotification, renderContactNotification } from '../../email/notify.mjs';
import copy from '../../scan_copy.json' with { type: 'json' };

const MAX_BODY = 32 * 1024;
const MIN_FILL_MS = 3000;            // a human needs more than 3 s between page load and submit
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}$/;
const RESEND_URL = 'https://api.resend.com/emails';

const clean = (v, max) => String(v ?? '').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '').replace(/[<>]/g, '').trim().slice(0, max);
const oneLine = (v, max) => clean(v, max).replace(/[\r\n]+/g, ' ');

function corsHeaders(env, origin) {
  const allowed = String(env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  return allowed.includes(origin) ? { 'Access-Control-Allow-Origin': origin, Vary: 'Origin' } : null;
}

export const LIMITS = { ip: { limit: 5, windowMs: 60_000 }, to: { limit: 2, windowMs: 60_000 } };

// Exact sliding-window counter: one Durable Object per key ("ip:1.2.3.4", "to:someone@x.com"). A Durable Object
// handles its requests one at a time, so the count is exact (Cloudflare's built-in rate limiter is approximate).
export class RateLimiter {
  constructor(state) { this.state = state; }
  async fetch(req) {
    const u = new URL(req.url), limit = Number(u.searchParams.get('limit')), windowMs = Number(u.searchParams.get('window'));
    const now = Date.now();
    const hits = ((await this.state.storage.get('hits')) || []).filter(t => now - t < windowMs);
    const allowed = hits.length < limit;
    if (allowed) hits.push(now);
    await this.state.storage.put('hits', hits);
    return new Response(allowed ? 'ok' : 'limited', { status: allowed ? 200 : 429 });
  }
}

async function limited(env, kind, key) {
  const ns = env.LIMITER, cfg = LIMITS[kind];
  if (!ns) { console.error('config: LIMITER binding missing, rate limiting disabled'); return false; }
  try {
    const r = await ns.get(ns.idFromName(kind + ':' + key)).fetch('https://limiter/hit?limit=' + cfg.limit + '&window=' + cfg.windowMs);
    return r.status === 429;
  } catch (e) { console.error('limiter error:', e.message); return false; }   // never block real visitors because of a limiter fault
}

async function sendEmail(env, msg) {
  const r = await fetch(env.RESEND_API_URL || RESEND_URL, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify(msg),
  });
  if (!r.ok) throw new Error('resend ' + r.status);
}

function contactFields(p) {
  const f = {
    name: oneLine(p.name, 120), clinic: oneLine(p.clinic, 160), email: oneLine(p.email, 254).toLowerCase(),
    phone: oneLine(p.phone, 40), specialty: oneLine(p.specialty, 80), tier: oneLine(p.practitioner_tier, 20),
    message: clean(p.message, 3000), interest: oneLine(p.interest, 40).replace(/[^a-z0-9-]/g, ''), lang: p.lang === 'fr' ? 'fr' : 'en',
  };
  const errors = [];
  if (!f.name) errors.push('name');
  if (!f.clinic) errors.push('clinic');
  if (!EMAIL_RE.test(f.email)) errors.push('email');
  return { f, errors };
}

function scanFields(p) {
  const f = {
    name: oneLine(p.name, 120), email: oneLine(p.email, 254).toLowerCase(), web: oneLine(p.web, 300),
    specialty: oneLine(p.specialty, 80), tier: oneLine(p.practitioner_tier, 20), lang: p.lang === 'fr' ? 'fr' : 'en',
  };
  const errors = [];
  if (!f.name) errors.push('name');
  if (!f.web) errors.push('web');
  if (!EMAIL_RE.test(f.email)) errors.push('email');
  return { f, errors };
}

const line = (k, v) => (v ? k + ': ' + v + '\n' : '');

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const origin = req.headers.get('Origin') || '';
    const cors = corsHeaders(env, origin);
    const json = (status, body) => new Response(JSON.stringify(body), {
      status, headers: { ...(cors || {}), 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' },
    });

    if (url.pathname !== '/submit') return json(404, { ok: false });
    if (req.method === 'OPTIONS') {
      if (!cors) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: { ...cors, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type, Accept', 'Access-Control-Max-Age': '86400' } });
    }
    if (req.method !== 'POST') return json(405, { ok: false });
    if (!cors) return json(403, { ok: false, error: 'origin' });
    if (!(req.headers.get('Content-Type') || '').toLowerCase().startsWith('application/json')) return json(415, { ok: false });
    if (Number(req.headers.get('Content-Length') || 0) > MAX_BODY) return json(413, { ok: false });
    if (!env.RESEND_API_KEY) { console.error('config: RESEND_API_KEY secret missing'); return json(500, { ok: false }); }

    const ip = req.headers.get('CF-Connecting-IP') || 'unknown';
    if (await limited(env, 'ip', ip)) return json(429, { ok: false, error: 'rate' });

    const raw = await req.text();
    if (raw.length > MAX_BODY) return json(413, { ok: false });
    let p;
    try { p = JSON.parse(raw); } catch { return json(400, { ok: false }); }
    if (!p || typeof p !== 'object' || Array.isArray(p)) return json(400, { ok: false });

    // Bots: honeypot filled or submitted faster than a human could. Answer "ok" so they learn nothing; send nothing.
    if (clean(p.website_url, 200) || (typeof p._t === 'number' && p._t < MIN_FILL_MS)) {
      console.log('dropped: bot signal');
      return json(200, { ok: true });
    }

    const to = String(env.TO_EMAIL || '').trim();
    const from = String(env.FROM_EMAIL || '').trim();
    const site = String(env.SITE_URL || 'https://raiseylab.com').replace(/\/$/, '');

    try {
      if (p.source === 'contact') {
        const { f, errors } = contactFields(p);
        if (errors.length) return json(400, { ok: false, error: 'invalid' });
        // HTML lead sheet + text version, built from the already-cleaned fields (and escaped again inside the template)
        const note = renderContactNotification({ ...f, practitioner_tier: f.tier });
        await sendEmail(env, { from, to: [to], reply_to: f.email, subject: oneLine(note.subject, 180), html: note.html, text: note.text });
        return json(200, { ok: true });
      }

      if (p.source === 'presence-scan') {
        const { f, errors } = scanFields(p);
        const v = validate({ ...p, lang: f.lang }, copy);
        if (errors.length || !v.ok) return json(400, { ok: false, error: 'invalid' });
        if (await limited(env, 'to', f.email)) return json(429, { ok: false, error: 'rate' });
        const base = site + (f.lang === 'fr' ? '/fr/' : '/');
        const mail = renderEmail(copy, { ...p, lang: f.lang }, {
          ctaUrl: base + '#contact',
          privacyUrl: base + (f.lang === 'fr' ? 'confidentialite.html' : 'privacy.html'),
        });
        await sendEmail(env, { from, to: [f.email], reply_to: to, subject: mail.subject, html: mail.html, text: mail.text });
        const note = renderScanNotification(copy, { ...p, name: f.name, email: f.email, web: f.web, specialty: f.specialty, practitioner_tier: f.tier, lang: f.lang });
        ctx.waitUntil(sendEmail(env, { from, to: [to], reply_to: f.email, subject: oneLine(note.subject, 180), html: note.html, text: note.text })
          .catch(e => console.error('notify failed:', e.message)));
        return json(200, { ok: true });
      }

      return json(400, { ok: false, error: 'source' });
    } catch (e) {
      console.error('send failed:', e.message);            // status code only, no personal data
      return json(502, { ok: false, error: 'send' });
    }
  },
};
