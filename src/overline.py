import glob, json, os
import face
import numpy as np
from PIL import Image
from scipy import ndimage
TARGET=256
gaps, bottoms, ths, lns = [], [], [], []
for p in sorted(glob.glob(os.path.join(face.PAGES, face.CFG["bars_glob"]))):
    a=np.asarray(Image.open(p).convert("L")); ink=a<128
    lab,n=ndimage.label(ink); objs=ndimage.find_objects(lab)
    hs=[o[0].stop-o[0].start for o in objs if 8<=o[0].stop-o[0].start<=200]
    hmed=float(np.median(hs))
    letters=[(o,i+1) for i,o in enumerate(objs) if 0.7*hmed<=o[0].stop-o[0].start<=1.6*hmed]
    bars=[(o,i+1) for i,o in enumerate(objs)
          if 2<=o[0].stop-o[0].start<=0.25*hmed and 0.3*hmed<=o[1].stop-o[1].start<=3.5*hmed
          and (lab[o]==i+1).mean()>0.75]
    for bo,_ in bars:
        bx0,bx1 = bo[1].start, bo[1].stop
        # letters whose horizontal span overlaps this bar and whose top is below it
        below=[lo for lo,_ in letters
               if lo[1].start < bx1 and lo[1].stop > bx0 and lo[0].start >= bo[0].stop
               and lo[0].start - bo[0].stop < 0.8*hmed]
        if not below: continue
        top = min(l[0].start for l in below)
        base = float(np.median([l[0].stop for l in below]))
        gaps.append((top - bo[0].stop)/hmed*TARGET)          # clearance above letter top
        bottoms.append((base - bo[0].stop)/hmed*TARGET)      # bar bottom over baseline
        ths.append((bo[0].stop-bo[0].start)/hmed*TARGET)
        lns.append((bx1-bx0)/hmed*TARGET)
print(f"overlines matched to a letter below: n={len(gaps)}")
print(f"  clearance above letter top : {np.median(gaps):5.1f} units")
print(f"  bar bottom above baseline  : {np.median(bottoms):5.1f} units  (letter height 256)")
print(f"  thickness                  : {np.median(ths):5.1f} units")
print(f"  length                      : {np.median(lns):5.1f} units")
b=json.load(open(os.path.join(face.DATA, "bars.json")))
b["overline"]=dict(th=float(np.median(ths)), ln=float(np.median(lns)),
                   y=float(np.median(bottoms)), clearance=float(np.median(gaps)))
json.dump(b, open(os.path.join(face.DATA, "bars.json"),"w"), indent=1)
