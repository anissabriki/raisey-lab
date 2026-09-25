# Raisey Lab — forms & email setup (Resend + Cloudflare Worker)

How it fits together:

```
Website form ──POST──▶ Cloudflare Worker (raisey-forms) ──API──▶ Resend ──▶ inboxes
                         · checks origin, spam, rate limits          · Contact form  → hello@raiseylab.com (Reply-To = the doctor)
                         · renders the Scan email itself              · Raisey Scan   → the doctor's own address (Reply-To = hello@)
                                                                      · + a notification to hello@raiseylab.com
```

What does NOT change: raiseylab.com stays at OVH (domain, DNS), and hello@raiseylab.com stays your OVH mailbox (you read and reply there).
Resend only *sends* the website's automatic emails. The API key only ever lives in Cloudflare's secret store: never in the website, never in this folder, never in a chat.

---

## Step 1 · Resend account + domain (≈10 min, then DNS propagation)
1. Create a free account at resend.com.
2. **Domains → Add domain** → `raiseylab.com` → Region: **EU (Ireland)** (keeps email data in the EU).
3. Resend shows 3–4 DNS records. Add them at **OVH → Web Cloud → Domain names → raiseylab.com → DNS zone → Add an entry**, exactly as shown:
   - a **TXT** record named `resend._domainkey` (DKIM signature),
   - an **MX** and a **TXT** record on the `send` subdomain (bounce handling + SPF for Resend).
   These are all on sub-names. **Do not change** the existing `MX` records of `raiseylab.com` itself (they deliver hello@ to OVH) or its existing SPF record.
4. DMARC: if the zone has no `_dmarc` record yet, add a TXT record `_dmarc` with value `v=DMARC1; p=none; rua=mailto:hello@raiseylab.com`.
5. Back in Resend, click **Verify**. It can take from a few minutes to a few hours. Wait until the domain shows **Verified**.

## Step 2 · Resend API key (2 min)
**API Keys → Create** → name `raisey-forms` → Permission **Sending access** → Domain **raiseylab.com**. Copy it somewhere temporary.
Do not paste it into chat or into any file. You'll give it directly to Cloudflare in step 4.

## Step 3 · Cloudflare account (2 min)
Create a free account at dash.cloudflare.com. You do **not** need to move raiseylab.com or its DNS to Cloudflare.
On first visit to **Workers & Pages**, Cloudflare asks you to choose a free `*.workers.dev` subdomain (e.g. `raiseylab`).

## Step 4 · Connect this computer + store the key (5 min, in the macOS **Terminal** app)
```
cd worker
npx wrangler login                      # opens the browser: click "Allow"
npx wrangler secret put RESEND_API_KEY  # paste the Resend key when asked (input stays hidden), press Enter
```
(If `secret put` says the Worker doesn't exist yet, run `npx wrangler deploy` once first, then repeat the `secret put` line.)

## Step 5 · Tell Claude "step 4 done"
Claude then deploys the Worker (the website stays offline), puts its URL in the site's `FORM_ENDPOINT`, rebuilds, and runs the real tests:
contact form → hello@raiseylab.com, Raisey Scan → the test address you choose, error handling, EN + FR.
For the tests only, the local preview's address is temporarily allowed to use the Worker, then removed again.

---

## Protection in place
- Only pages on `https://raiseylab.com` / `https://www.raiseylab.com` may use the Worker (`ALLOWED_ORIGINS` in `worker/wrangler.toml`).
- JSON only, 32 KB maximum, strict validation of every field; HTML from the browser is never accepted; Scan emails are rebuilt from the scores only.
- Invisible honeypot field + minimum 3 s on the page: bots get a fake "ok" and nothing is sent.
- Rate limits (exact, one Durable Object counter per key): 5 submissions per minute per IP address (invalid ones count too); 2 Scan-results emails per minute per recipient address. Refused attempts do not extend the window.
- Logs contain no names, emails or messages.
- Possible later upgrade if spam appears: Cloudflare Turnstile (an invisible challenge; needs a small script on the site).

## Useful commands (in `worker/`)
```
node test/worker.test.mjs      # 45 offline tests (fake Resend, no email sent)
npx wrangler deploy            # publish Worker changes
npx wrangler tail              # live logs while testing
npx wrangler secret put RESEND_API_KEY   # rotate the key (then delete the old one in Resend)
```
