// Sample payloads used by preview.mjs and check.mjs (shape = what the site's Scan form posts as `scan`).
// scores = the nine scored questions (0-3 each). Growth objectives / treatments are context only.
const S = (medical, digital, brand, search, contentPov, contentStrategy, journeyBooking, journeyLead, journeyRelationship) =>
  ({ medical, digital, brand, search, contentPov, contentStrategy, journeyBooking, journeyLead, journeyRelationship });
const mk = (lang, scores, growth = [], treatments = [], other = '') => ({ lang, scan: { scores, answers: { growth, treatments }, other: { treatments: other } } });
export const SAMPLES = {
  'strong-en': mk('en', S(3, 3, 2, 3, 3, 2, 3, 3, 2), ['authority', 'social'], ['dermatology']),
  'mixed-fr': mk('fr', S(2, 1, 0, 1, 3, 0, 3, 1, 2), ['patients', 'visibility', 'market'], ['botox', 'fillers', 'other'], 'Peelings médicaux'),
  'crm-only-en': mk('en', S(2, 2, 2, 2, 2, 2, 1, 1, 3), ['retention'], ['none']),
  'early-fr': mk('fr', S(0, 1, 1, 0, 1, 0, 1, 0, 0), [], []),
};
