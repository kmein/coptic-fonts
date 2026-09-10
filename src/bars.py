import glob, json, pickle, os
import face
import numpy as np
from PIL import Image
from scipy import ndimage
TARGET=256
over, hyph = [], []
for p in sorted(glob.glob(os.path.join(face.PAGES, face.CFG["bars_glob"]))):
    a=np.asarray(Image.open(p).convert("L")); ink=a<128
    lab,n=ndimage.label(ink); objs=ndimage.find_objects(lab)
    hs=[o[0].stop-o[0].start for o in objs if 8<=o[0].stop-o[0].start<=200]
    hmed=float(np.median(hs))
    # line baselines from the normal-sized components
    comps=[(o,i+1) for i,o in enumerate(objs) if 0.7*hmed<=o[0].stop-o[0].start<=1.5*hmed]
    comps.sort(key=lambda c:(c[0][0].start+c[0][0].stop)/2)
    lines=[]; cur=[]
    for c in comps:
        y=(c[0][0].start+c[0][0].stop)/2
        if cur and y-(cur[-1][0][0].start+cur[-1][0][0].stop)/2 > 0.7*hmed: lines.append(cur); cur=[]
        cur.append(c)
    if cur: lines.append(cur)
    bases=[(np.median([c[0][0].stop for c in L]), L) for L in lines if len(L)>=6]
    for i,o in enumerate(objs):
        h=o[0].stop-o[0].start; w=o[1].stop-o[1].start
        if h<2 or h>0.25*hmed or w<0.3*hmed or w>3.5*hmed: continue
        m=(lab[o]==i+1)
        if m.mean()<0.75: continue
        yc=(o[0].start+o[0].stop)/2
        cand=[b for b,_ in bases if -1.8*hmed < yc-b < 0.2*hmed]
        if not cand: continue
        b=min(cand, key=lambda b: abs(yc-b))
        rel=(b-yc)/hmed                        # height above baseline in letter-heights
        rec=dict(th=h/hmed*TARGET, ln=w/hmed*TARGET, rel=rel*TARGET)
        if rel > 0.95: over.append(rec)
        elif 0.2 < rel < 0.65: hyph.append(rec)
for nm,L in (("overline",over),("hyphen",hyph)):
    if not L: print(nm,"none"); continue
    print(f"{nm:9s} n={len(L):5d}  thickness {np.median([r['th'] for r in L]):5.1f}  "
          f"length {np.median([r['ln'] for r in L]):6.1f}  height above baseline {np.median([r['rel'] for r in L]):6.1f}")
# word space: gaps larger than the intra-word cutoff
insts=pickle.load(open(os.path.join(face.WORK, "instances.pkl"),"rb"))
MS = face.CFG.get("metrics_source")
if MS: insts = [g for g in insts if g.get("source","") == MS]
lines={}
for g in insts: lines.setdefault((g["page"],g["base"]),[]).append(g)
ws=[]
for L in lines.values():
    L.sort(key=lambda g:g["x0"])
    for a,b in zip(L,L[1:]):
        gp=(b["x0"]-a["x1"])*TARGET/a["lh"]
        if 0.55*TARGET < gp < 1.6*TARGET: ws.append(gp)
print(f"word gap median {np.median(ws):.1f} units (n={len(ws)})")
json.dump(dict(overline=dict(th=float(np.median([r['th'] for r in over])),
                             ln=float(np.median([r['ln'] for r in over])),
                             y=float(np.median([r['rel'] for r in over]))),
               hyphen=dict(th=float(np.median([r['th'] for r in hyph])),
                           ln=float(np.median([r['ln'] for r in hyph])),
                           y=float(np.median([r['rel'] for r in hyph]))),
               word_gap=float(np.median(ws))), open(os.path.join(face.DATA, "bars.json"),"w"), indent=1)
