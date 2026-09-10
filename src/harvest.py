"""Harvest glyph instances of Layton's Coptic type from 600dpi page scans."""
import glob, pickle, sys, os
import face
import numpy as np
from PIL import Image
from scipy import ndimage
import score as S

LETTERS = S.LETTERS
TPL = {}                       # 32x32 box-normalised templates from Table 1
def boxify(m, n=32):
    return np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((n,n), Image.LANCZOS)) > 127
for k,v in S.ref.items(): TPL[k] = boxify(v)
TK = list(TPL); TA = np.stack([TPL[k].ravel() for k in TK])

def classify(m):
    b = boxify(m).ravel()
    inter = (TA & b).sum(1); union = (TA | b).sum(1)
    sc = inter/np.maximum(union,1)
    i = int(np.argmax(sc)); o = np.sort(sc)[-2]
    return TK[i], float(sc[i]), float(sc[i]-o)

def page_glyphs(path):
    a = np.asarray(Image.open(path).convert("L"))
    ink = a < 128
    lab,n = ndimage.label(ink)
    objs = ndimage.find_objects(lab)
    boxes=[]
    for i,o in enumerate(objs):
        h=o[0].stop-o[0].start; w=o[1].stop-o[1].start
        if h<8 or w<3 or h>200 or w>200: continue
        boxes.append((i+1,o,h,w))
    if not boxes: return []
    hs = np.array([b[2] for b in boxes])
    hmed = float(np.median(hs))
    # keep body-text sized components
    keep = [b for b in boxes if 0.70*hmed <= b[2] <= 2.35*hmed and b[3] <= 2.3*hmed]
    # group into lines by vertical overlap of bbox centres
    keep.sort(key=lambda b: (b[1][0].start+b[1][0].stop)/2)
    lines=[]; cur=[]
    for b in keep:
        c=(b[1][0].start+b[1][0].stop)/2
        if cur and c - (cur[-1][1][0].start+cur[-1][1][0].stop)/2 > 0.7*hmed:
            lines.append(cur); cur=[]
        cur.append(b)
    if cur: lines.append(cur)
    out=[]
    for line in lines:
        if len(line) < 6: continue                       # skip headings / short runs
        line.sort(key=lambda b: b[1][1].start)
        base = float(np.median([b[1][0].stop for b in line]))
        lh   = float(np.median([b[2] for b in line]))
        cls  = [classify(lab[b[1]]==b[0]) for b in line]
        good = sum(1 for c in cls if c[1] > 0.72)
        if good/len(line) < 0.55: continue                # not a Coptic line
        for b,(name,scv,marg) in zip(line, cls):
            if scv < 0.72 or marg < 0.03: continue
            m = (lab[b[1]]==b[0])
            out.append(dict(letter=name, score=scv, margin=marg, mask=m,
                            h=b[2], w=b[3], x0=b[1][1].start, x1=b[1][1].stop,
                            bottom=b[1][0].stop, base=base, lh=lh, page=path))
    return out

if __name__ == "__main__":
    allg=[]
    for p in sorted(glob.glob(os.path.join(face.PAGES, "*.png"))):
        g = page_glyphs(p)
        allg += g
        pass
    print("TOTAL:", len(allg))
    from collections import Counter
    c = Counter(g["letter"] for g in allg)
    print("per letter:", {k:c[k] for k in LETTERS})
    pickle.dump(allg, open(os.path.join(face.WORK, "instances.pkl"),"wb"))
