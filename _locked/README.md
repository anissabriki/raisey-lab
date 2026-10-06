# 🔒 Locked component: "How we build your presence" (services)

Approved by the owner. Do NOT redesign, restyle, recolour, restructure or rewrite unless explicitly asked.

Locked: layout and proportions, typography and hierarchy, blush/optical-white neutral treatment, the four service rows and wording,
spacing, dividers, circular arrows and interactions (expand, hover, mobile accordion), the Presence Review CTA, desktop and mobile structure.

Never reintroduce: coloured service icons/markers, decorative waves, illustrations or any extra visual elements.

If a global CSS/component change affects it, adjust the *global* change so this section looks and behaves identically.
Check: `python3 _locked/verify.py`  ·  Restore: copy the blocks in this folder back into index.html between the same markers.


## Authorised copy change · 2026-09
The owner authorised changing ONLY the mid-page CTA copy (heading, micro-line, button label and the button's link target) to match the Presence Scan journey. No layout, spacing, visual design or other Services content changed. Snapshot and checksum were refreshed accordingly.


## Raisey Lab preview · 2026-09-25
In this PREVIEW copy only, the product names inside the locked block were renamed (Presence Scan → Raisey Scan, Presence Review → Raisey Review; comment included). Nothing else changed; snapshot and checksums refreshed. The live WEBSITE-V2 lock is untouched.
Preview only, owner-approved 2026-09-25: services heading "How we build your presence." → "How we raise your profile." (FR "Comment nous élevons votre profil."). Heading text only; layout/styling unchanged.
Preview only, owner-approved 2026-09-25: heading adjusted to "How we raise your presence." (FR "Comment nous élevons votre présence.").
2026-09-25: Scan anchor renamed #presence-scan → #raisey-scan (CTA href only). Nothing else changed.

## Art direction 2026-09-25 (owner-approved)
The owner approved the new Raisey Lab art direction, including a "stone/cream Services treatment". Only the site-wide colour tokens changed (blush -> stone, optical cream); the locked services HTML/CSS/JS text is unchanged and still verified by checksum.

## RAISEY copy audit 2026-09-25 (owner-approved "OK for all, including 🔒 items")
Wording only, EN + FR: row 01 "Digital Presence" → "Visibility" ("Raise your visibility where patients are already looking."),
row 03 "Ongoing Presence" → "Sustained Visibility" ("Keep your practice visible, relevant and rising after launch."),
mid CTA eyebrow "Not sure where to start?" → "What could you raise first?". Layout, styling, CSS and JS unchanged; services.html snapshot + checksum refreshed.

## RISE/RAISE copy audit v2 · 2026-09-25 (owner-approved "OK v2")
Mid CTA wording only, EN + FR: eyebrow "What could you raise first?" → "Not sure where to start?", heading "See what your answers reveal." → "See what you can raise."
Layout, styling, CSS and JS unchanged; services.html snapshot + checksum refreshed.

## Mobile collapsed rows · 2026-09-26 (owner-requested)
Below 720 px only: each collapsed row now always shows the burgundy descriptor (e.g. "Be found" / "Être trouvé") and the keyword line under the service name; the arrow opens description, detailed services and CTA. Desktop unchanged. services.html + services.css snapshots and checksums refreshed.


## Services lede · 2026-09-29 (owner-approved SEO wording)
EN: "From visibility to patient experience, we build the digital strategy that shapes how an aesthetic practice is found, perceived and chosen." FR mirrored. Text only; snapshot + checksum refreshed.


## Image-band layout · 2026-09-29 (owner-requested redesign, mobile + desktop, EN + FR)
Each row gets a background image (inline --svc-img), rows become editorial image bands (name + keywords + circular arrow; descriptor/description stay in the panel). Accordion behaviour unchanged. Override CSS lives outside the locked block; snapshot + checksums refreshed.


## Heading whitespace · 2026-09-29 (owner-approved, action 7)
One space added between `<span class="l1">` and `<span class="l2">` in the Services H2 (EN + FR) so text extraction reads "How we raise your presence" instead of "raiseyour". Both spans are display:block: no visual change (verified by pixel comparison). services.html snapshot + checksum refreshed.

## Kinassay Lab rename · 2026-10-02 (owner request "décline le site avec le nouveau nom")
Brand name only: "Raisey Scan" → "Kinassay Scan" (CTA label) and "Raisey Review" → "Kinassay Review" (JS comment). Anchor #raisey-scan kept. Layout, styling, CSS and JS behaviour unchanged; services.html/services.js snapshots + checksums refreshed.

## Homepage lead-gen restructure · 2026-10-05
The locked services block is untouched (owner chose to keep it locked). Sections around it changed, so verify.py now ends the HTML snapshot at an explicit `<!-- 🔒 END LOCKED services -->` marker placed where the old studies marker was; the snapshot bytes and checksum are unchanged.

## Services Scan CTA made secondary · 2026-10-05 (owner-approved "ok pour 6a")
Outline style for `.svc-cta .btn` (scoped override outside `_locked/`, in the CTA colour block). Locked HTML/CSS/JS text unchanged; checksums unchanged.

## Expertise page · 2026-10-06 (owner brief "page Expertise / Services")
The owner reopened the component to move it onto its own page (/expertise/, /fr/expertise/). Same layout, styles and accordion behaviour. Content renamed per the brief: heading "How we build your presence." (now the page's h1), lede with "found, perceived and chosen" highlighted, four bands Visibility & acquisition / Website & patient journey / Content & presence / Strategy & growth (ids #visibility #website #content #growth), detailed lists in the panels, the per-band "Discuss this" links removed, one Scan CTA at the end. On the homepage the block sits inside an inert `<template id="expertise-src">` that build_expertise.py turns into the page; build_site.py strips it from the shipped homepages. New CSS (h1, highlight, filled CTA) lives outside the locked block. services.html snapshot + checksum refreshed; CSS/JS unchanged.
