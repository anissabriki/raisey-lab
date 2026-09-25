# Presence Scan results email

`render.mjs` turns **structured scores** into the results email (HTML + plain text) in EN or FR. It is a pure function with no dependencies, so it runs unchanged in Node, a Cloudflare Worker, a Lambda or a Netlify/Vercel function.

## Payload contract (what the site posts for `source: "presence-scan"`)
```json
{ "source": "presence-scan", "lang": "fr", "name": "...", "email": "...", "web": "...", "specialty": "...",
  "scan": { "scores": { "medical": 0-3, "digital": 0-3, "brand": 0-3, "search": 0-3, "contentPov": 0-3, "contentStrategy": 0-3,
                        "journeyBooking": 0-3, "journeyLead": 0-3, "journeyRelationship": 0-3 },
            "answers": { "growth": ["patients"], "treatments": ["fillers", "other"] }, "other": { "treatments": "free text" } } }
```
Only `scan.scores` (nine integers), `answers.growth`, `answers.treatments`, `other.treatments` and `lang` are used. **Dimension values and the tier sent by the browser are ignored and recomputed** from the scores with `../scan_scoring.mjs`.

## Rules the endpoint must keep
- Never accept HTML or copy from the browser (phishing risk). Render only with `renderEmail(copy, payload, { ctaUrl, privacyUrl })`.
- One-off transactional email. Do not subscribe the visitor to any list.
- Send the founder notification separately; keep the API key in the provider/edge environment, never in this repository.
- Add bot protection (Turnstile/hCaptcha or similar) and per-IP / per-address rate limits.
- `ctaUrl` = `https://raiseylab.com/#contact` (EN) or `https://raiseylab.com/fr/#contact` (FR); `privacyUrl` = `https://raiseylab.com/privacy.html` or `https://raiseylab.com/fr/confidentialite.html`.
- Sender: `Raisey Lab <hello@raiseylab.com>` (or a sending subdomain on raiseylab.com), `Reply-To: hello@raiseylab.com`. Verify SPF/DKIM/DMARC for raiseylab.com at the email provider.
- The mailbox password, SMTP credentials and provider API key live ONLY in the provider / serverless environment. Never in this repository or in the site's JavaScript.

## Preview and checks
`node email/preview.mjs` then open `email/preview/index.html`. `node email/check.mjs` verifies the agreed rules (transparency line, no mailing-list promise, answer-based wording, context questions never change scores, scoring parity with the site).
