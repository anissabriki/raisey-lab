# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static site, no framework and no runtime dependencies: a single-page `index.html` (English) and `fr/index.html` (French), with `privacy.html` and `fr/confidentialite.html`. French and the legal pages are generated from the English source (`build_fr.py`, `build_legal.py`). Fonts are self-hosted (Fraunces, Inter). No cookies, analytics or third-party requests.

## Users

Aesthetic doctors, surgeons, nurse prescribers and clinic owners in Paris, London, Dubai and wider international markets, with real medical authority but a digital presence that does not reflect it. They are deciding whether to trust an outside studio with their reputation. Job: request a Presence Review.

## Product Purpose

PRESENCE LAB is a digital presence studio for aesthetic medicine. It turns medical expertise into a presence patients can find, trust and choose. The site earns one action: taking the Presence Scan, which leads to a first conversation and then a Presence Review.

## Positioning

Audit before action. "We don't make doctors look like influencers. We make expertise visible."

The journey, in this order, and the three names must never be confused:

**Presence Scan → results by email → first conversation → Presence Review → recommendation → transformation / ongoing presence**

- **Presence Scan**: automated, about 4 minutes, 11 questions, based ONLY on the visitor's answers. Immediate first insight on screen; complete results by email within minutes. It never inspects the website, Google, social profiles, CRM or content.
- **First conversation**: a human conversation about the practice, positioning, objectives and priorities. A journey step, not a branded product. Reply within two business days.
- **Presence Review**: a personalised human strategic analysis prepared after the conversation, where the real digital ecosystem is examined. Never automated, instant or emailed by the Scan. Timing agreed after the conversation.

## Operating Context

Boutique, selective studio (markets served: Paris, London, Dubai; not offices). Conversion path: Presence Scan → first insight → full results by email (transactional, one-off, no mailing list) → request a first conversation (contact form). Copy for the Scan lives in `scan_copy.json`; scoring in `scan_scoring.mjs`; the results email in `email/`.

## Capabilities and Constraints

- Sections: 01 Studio (hero), 02 Presence Scan, 03 Our approach, Services (locked), 05 Selected Presence Studies (anonymous composite archetypes, never real clients), 06 Founder, 07 Founding partners (six), 08 Contact.
- Languages: English and French. "Presence Review" stays untranslated as a brand term.
- Scan result is qualitative (Established / Strong Potential / To Elevate); never a medical, clinical or scientific score. Six dimensions: Medical Authority, Digital Authority, Brand Expression, Discoverability (FR: Visibilité), Content Potential (point of view + editorial strategy), Patient Journey (booking + lead follow-up + CRM/email relationship, with the relationship stage capped by the first two). Growth objectives and treatment focus are context only and never move the radar.
- No outcome guarantees or before/after claims (medical-advertising sensitivity).
- Forms send JSON to `FORM_ENDPOINT` (still to be set). Legal identity, address, contact email and host live in `site.config.json` and must be filled before launch.

## Brand Commitments

Visual system approved and locked: cream / aubergine / raspberry palette, Fraunces + Inter, the concentric-arc mark, squared buttons, hairline rules. The "How we build your presence" services section is a LOCKED approved component (`_locked/`, verify with `python3 _locked/verify.py`).

## Evidence on Hand

Founder: Anissa Sabrina Briki (FILLMED Laboratories, Google, GroupM). No client testimonials, case studies, measured results or pricing exist; none may be invented. The founder portrait is a placeholder cropped from a design board; replace with a real photo.

## Product Principles

1. Audit before action.
2. Medical authority first.
3. Independent studies, never sold results.
4. Selective and quiet.
5. Localisation by structure: EN is the source of truth, FR is generated and checked against it.

## Accessibility & Inclusion

WCAG AA target: text contrast, 44px touch targets, visible focus, labelled forms with linked errors, reduced-motion support. Nothing important set below 11px.
