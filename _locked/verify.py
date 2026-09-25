#!/usr/bin/env python3
"""Verifies the locked "How we build your presence" section in ../index.html is byte-identical to the approved snapshot.
Run:  python3 _locked/verify.py   (exit 0 = untouched, 1 = changed)"""
import hashlib, json, os, sys
here=os.path.dirname(os.path.abspath(__file__)); s=open(os.path.join(here,'..','index.html')).read()
sums=json.load(open(os.path.join(here,'checksums.json')))
def cut(a,b,end_inclusive=''):
    i=s.index(a); j=s.index(b,i); return s[i:j+len(end_inclusive)]
cur={'services.css':cut('/* 🔒 LOCKED · APPROVED COMPONENT','/* ============ 05 STUDIES ============ */'),
     'services.html':cut('<!-- 🔒 LOCKED · APPROVED COMPONENT: services','<!-- ============ 05 · SELECTED PRESENCE STUDIES ============ -->'),
     'services.js':cut('/* 🔒 LOCKED · services accordion','})();','})();')}
bad=[k for k,v in cur.items() if hashlib.sha256(v.encode()).hexdigest()!=sums[k]]
print('LOCKED SECTION INTACT' if not bad else 'CHANGED: '+', '.join(bad)); sys.exit(1 if bad else 0)
