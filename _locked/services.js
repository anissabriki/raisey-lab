/* 🔒 LOCKED · services accordion + diagnostic CTA behaviour: approved, do not change. */
/* ---------- services: exclusive accordion; diagnostic CTA opens the Raisey Review ---------- */
(function(){
  const rows=[...document.querySelectorAll('.row')];
  rows.forEach(r=>{const b=r.querySelector('.r-btn');b.addEventListener('click',()=>{const was=b.getAttribute('aria-expanded')==='true';rows.forEach(o=>{o.dataset.open='false';o.querySelector('.r-btn').setAttribute('aria-expanded','false')});if(!was){r.dataset.open='true';b.setAttribute('aria-expanded','true')}})});
  document.querySelectorAll('[data-startdiag]').forEach(a=>a.addEventListener('click',e=>{
    e.preventDefault(); const t=document.getElementById('takeDiag'); const cta=document.querySelector('.rv-cta');
    if(t&&cta&&!cta.hidden) t.click(); else document.getElementById('scan').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  }));
})();