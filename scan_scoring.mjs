// Presence Scan scoring: ONE source of truth, used by the site (inlined into index.html between SCAN_SCORING markers by
// build_fr.py / scan_copy.py) and by the results-email renderer (email/render.mjs). Pure functions, no dependencies.
//
// Nine scored questions ("facets", each 0-3) feed exactly SIX dimensions. Growth objectives and treatment focus are context
// only and never appear here, so they cannot move the radar.
export const DIMS = ['medical', 'digital', 'brand', 'search', 'content', 'journey'];
export const FACETS = ['medical', 'digital', 'brand', 'search', 'contentPov', 'contentStrategy', 'journeyBooking', 'journeyLead', 'journeyRelationship'];
const r2 = x => Math.round(x * 100) / 100;

// Status of a dimension score (0-3): unchanged thresholds, so single-question dimensions behave exactly as before.
export const levelOf = v => (v >= 2.5 ? 'established' : v >= 1.5 ? 'potential' : 'elevate');

// Six dimension scores from the nine facets.
//  - Content Potential   = mean(point of view, editorial strategy): posting alone cannot make content "established".
//  - Patient Journey     = mean(booking, lead follow-up, relationship), equal weights, BUT the relationship (CRM / email) stage
//    counts only up to the average of the two earlier stages: a CRM cannot compensate for a weak booking or follow-up journey.
export function dimensions(f) {
  const rel = Math.min(f.journeyRelationship, (f.journeyBooking + f.journeyLead) / 2);
  return {
    medical: f.medical, digital: f.digital, brand: f.brand, search: f.search,
    content: r2((f.contentPov + f.contentStrategy) / 2),
    journey: r2((f.journeyBooking + f.journeyLead + rel) / 3),
  };
}

// Overall tier: same thresholds as before (sum of the six dimension scores, max 18).
export const tierOf = d => { const s = DIMS.reduce((a, k) => a + d[k], 0); return s >= 14 ? 'established' : s >= 7 ? 'potential' : 'elevate'; };

// Which facet of a two/three-part dimension stands apart? Returns { dim, key } or null. Only compares the user's own answers.
export function nuance(f) {
  if (Math.abs(f.contentPov - f.contentStrategy) >= 2) return [{ dim: 'content', key: f.contentPov > f.contentStrategy ? 'povStrong' : 'strategyStrong' }];
  return [];
}
export function journeyNuance(f) {
  const parts = [['booking', f.journeyBooking], ['lead', f.journeyLead], ['relationship', f.journeyRelationship]];   // tie order: booking, lead, relationship
  const max = Math.max(...parts.map(p => p[1])), min = Math.min(...parts.map(p => p[1]));
  if (max - min < 2) return [];
  return [{ dim: 'journey', key: parts.find(p => p[1] === min)[0] }];
}
export const nuances = f => [...nuance(f), ...journeyNuance(f)];
