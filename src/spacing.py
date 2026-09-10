import pickle, json, glob, os
import face
import numpy as np
from PIL import Image
from scipy import ndimage
import score as S
TARGET = 256

insts = pickle.load(open(os.path.join(face.WORK, "instances.pkl"),"rb"))
MS = face.CFG.get("metrics_source")            # metrics come from one printed setting only
if MS: insts = [g for g in insts if g.get("source","") == MS]
lines = {}
for g in insts: lines.setdefault((g["page"], g["base"]), []).append(g)
adv, gaps = {}, []
for key, L in lines.items():
    L.sort(key=lambda g: g["x0"])
    for a,b in zip(L, L[1:]):
        sc = TARGET/a["lh"]
        gap = (b["x0"] - a["x1"])*sc
        if not (-4 < gap < 0.55*TARGET): continue      # same word
        adv.setdefault(a["letter"], []).append((b["x0"]-a["x0"])*sc)
        gaps.append(gap)
gap_med = float(np.median(gaps))
print(f"inter-letter gap: median {gap_med:.1f} units (letter height = {TARGET}), n={len(gaps)}")
out={}
for k,v in adv.items():
    out[k]=dict(advance=float(np.median(v)), n=len(v))
for k in S.LETTERS:
    if k in out: print(f"  {k:9s} advance {out[k]['advance']:6.1f}  (n={out[k]['n']})")
    else: print(f"  {k:9s} advance   --   (no pairs)")
pitch = float(np.median([a for v in adv.values() for a in v]))
spread = float(np.std([o["advance"] for o in out.values()]))
print(f"pitch (median of all pair advances) {pitch:.1f}; std of per-letter medians {spread:.1f} -> {'fixed pitch' if spread < 8 else 'proportional'}")
json.dump(dict(gap=gap_med, adv=out, pitch=pitch, spread=spread), open(os.path.join(face.DATA, "spacing.json"),"w"), indent=1)

# --- bars: supralinear stroke and hyphen, measured from the pages
th, ln, above, mid = [], [], [], []
for p in sorted(glob.glob(os.path.join(face.PAGES, face.CFG["spacing_glob"]))):
    a = np.asarray(Image.open(p).convert("L")); ink = a<128
    lab,n = ndimage.label(ink); objs = ndimage.find_objects(lab)
    hs = [o[0].stop-o[0].start for o in objs if 8<=o[0].stop-o[0].start<=200]
    hmed = float(np.median(hs))
    for i,o in enumerate(objs):
        h=o[0].stop-o[0].start; w=o[1].stop-o[1].start
        if h<2 or w<0.35*hmed or w>3*hmed: continue
        if h > 0.22*hmed: continue
        m=(lab[o]==i+1)
        if m.mean() < 0.75: continue          # solid bar
        th.append(h); ln.append(w/hmed)
print(f"\nbars: n={len(th)}  thickness median {np.median(th):.1f}px "
      f"({np.median(th)/hmed*TARGET:.1f} units)  length median {np.median(ln)*TARGET:.0f} units")
json.dump(dict(thickness_units=float(np.median(th)/hmed*TARGET),
               length_units=float(np.median(ln)*TARGET)), open(os.path.join(face.DATA, "bars.json"),"w"), indent=1)
