# Deploying Raisey Lab to GitHub Pages

**Status: prepared, not deployed.** Nothing here runs until you push to GitHub and enable Pages.

## How it works
`build_site.py` builds a clean `dist/` folder (only the publishable files) and GitHub Actions publishes that folder.
The source design files are never modified. There are **no secrets** anywhere: GitHub Pages is static hosting, so anything in the
site is public. Public settings (form URL, contact email, site URL) are injected at build time from repository *Variables*.

## One-time setup
1. Create a **new GitHub repository whose root is this folder** (`WEBSITE-V2`), never its parent folder
   (it holds prospects and CRM data that must stay private).
2. Repo → **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Repo → **Settings → Secrets and variables → Actions → Variables** (not "Secrets"): add
   `FORM_ENDPOINT`, `CONTACT_EMAIL`, `SITE_URL` (and `BASE_PATH` only if using `https://user.github.io/repo/`, then `/repo/`).
4. Fill `site.config.json`: `legalName`, `postalAddress`, `contactEmail`, `host`, `retention`, `siteUrl`, `customDomain` (optional).
5. Push to `main`. The workflow builds and deploys. It **fails on purpose** while any launch requirement below is missing.

## Commands
```
python3 build_site.py                # preview build, lists warnings
python3 build_site.py --production   # release gates (what CI runs)
python3 -m http.server 8940 -d dist  # look at the built site locally
python3 _locked/verify.py            # approved services section still intact
```

## Launch checklist (needs an external service or a decision)
- [ ] **Form service** for the two forms (GitHub Pages cannot process forms). Put its public URL in `FORM_ENDPOINT`.
- [ ] **A mailbox** on your own domain for `CONTACT_EMAIL` (privacy requests + fallback message).
- [ ] **Legal details** in `site.config.json`, reviewed by a lawyer (privacy policy + French *mentions légales*).
- [ ] **Domain** (recommended) → set `customDomain`, DNS at your registrar, enable "Enforce HTTPS" in Pages settings.
- [ ] **Real founder photo** and an optional `images/og.jpg` (1200×630) for link previews.
- [ ] Decide repo visibility (see "What a public repo exposes" below).

## What a public repo exposes
The site is public either way. A public repository also shows `PRODUCT.md` (positioning notes), `site.config.json`, build scripts and git
history. None are secrets; if you prefer to keep them private use a private repo (GitHub Pages from a private repo needs a paid plan)
or move `PRODUCT.md` out before pushing.

## Not possible on GitHub Pages (by design)
Custom HTTP headers (the build adds a CSP + referrer `<meta>` instead), server code, server-side redirects, runtime environment
variables, form processing, password protection.


## Presence Scan results email (needs an external service before launch)
The site cannot email visitors by itself. `FORM_ENDPOINT` must be an endpoint that, for `source: "presence-scan"` submissions, (1) notifies the founder and (2) sends the visitor the results email using `email/render.mjs`. A plain form service (Formspree and similar) only notifies you; it does not send the results email.
Requirements: an email provider (API key stored server-side only, never in this repository); a sending domain with SPF, DKIM and DMARC; server-side rendering from scores (never accept HTML from the browser); bot protection and rate limiting; the provider named in `site.config.json` -> `emailProvider` and in the privacy policy. The email is one-off and transactional: no mailing-list subscription. See `email/README.md` for the payload contract.

## Legal wording is a draft
`privacy.html` / `fr/confidentialite.html` describe the Scan -> first conversation -> Review data use. The wording and the GDPR bases have NOT been reviewed by a lawyer. Have them reviewed before launch.
