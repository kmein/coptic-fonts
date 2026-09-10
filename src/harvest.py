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
GEOM = face.CFG["geom"]      # letter -> (ink height / letter height, descent / letter height)
FLAT = {n for n,(r,d) in GEOM.items() if r < 1.1 and abs(d) < 0.05}   # these define baseline and letter height
def plausible(name, h, bottom, base, lh):
    """geometry a correctly segmented instance must have; rejects merged overlines,
    broken glyphs and look-alikes such as the editorial line-division bar read as iota"""
    r0, d0 = GEOM[name]
    return abs(h/lh - r0) < (0.15 if r0 < 1.5 else 0.22) and abs((bottom-base)/lh - d0) < 0.12

def classify(m):
    b = boxify(m).ravel()
    inter = (TA & b).sum(1); union = (TA | b).sum(1)
    sc = inter/np.maximum(union,1)
    i = int(np.argmax(sc)); o = np.sort(sc)[-2]
    return TK[i], float(sc[i]), float(sc[i]-o)

def threshold(a):
    """128 for a bilevel scan; Otsu's threshold for a greyscale one, whose ink is often
    light and whose fixed-cutoff core would be eroded to a thin skeleton"""
    hist = np.bincount(a.ravel(), minlength=256).astype(np.float64)
    if hist[1:255].sum() < 0.02*hist.sum(): return 128
    p = hist/hist.sum(); w = np.cumsum(p); m = np.cumsum(p*np.arange(256)); mt = m[-1]
    var = (mt*w - m)**2 / np.maximum(w*(1-w), 1e-12)
    return int(np.argmax(var))

def page_glyphs(path):
    a = np.asarray(Image.open(path).convert("L"))
    ink = a < threshold(a)
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
    # group into lines: a component joins the current line if its centre is within
    # 0.5 letter heights of the line's running median centre (comparing against the
    # previous component alone lets descenders chain two lines together)
    keep.sort(key=lambda b: (b[1][0].start+b[1][0].stop)/2)
    lines=[]; cur=[]; cyc=[]
    for b in keep:
        c=(b[1][0].start+b[1][0].stop)/2
        if cur and abs(c - float(np.median(cyc))) > 0.5*hmed:
            lines.append(cur); cur=[]; cyc=[]
        cur.append(b); cyc.append(c)
    if cur: lines.append(cur)
    out=[]
    for line in lines:
        if len(line) < 6: continue                       # skip headings / short runs
        line.sort(key=lambda b: b[1][1].start)
        cls  = [classify(lab[b[1]]==b[0]) for b in line]
        good = sum(1 for c in cls if c[1] > 0.72)
        if good/len(line) < 0.55: continue                # not a Coptic line
        # baseline and letter height from the confidently classified letters that sit
        # on the baseline (descender letters and merged overlines would bias both)
        flat = [b for b,(n,scv,marg) in zip(line, cls) if scv > 0.72 and n in FLAT]
        if len(flat) < 3: continue
        base = float(np.median([b[1][0].stop for b in flat]))
        lh   = float(np.median([b[2] for b in flat]))
        for b,(name,scv,marg) in zip(line, cls):
            if scv < 0.72 or marg < 0.03: continue
            if not plausible(name, b[2], b[1][0].stop, base, lh): continue
            m = (lab[b[1]]==b[0])
            out.append(dict(letter=name, score=scv, margin=marg, mask=m,
                            h=b[2], w=b[3], x0=b[1][1].start, x1=b[1][1].stop,
                            bottom=b[1][0].stop, base=base, lh=lh, page=path))
    return out

if __name__ == "__main__":
    allg=[]
    for p in sorted(glob.glob(os.path.join(face.PAGES, "**", "*.png"), recursive=True)):
        src = os.path.relpath(os.path.dirname(p), face.PAGES)      # pages/<source>/... -> source name
        src = "" if src == "." else src
        scale = face.CFG.get("source_scale", {}).get(src, 1.0)
        g = page_glyphs(p)
        for x in g:
            x["source"] = src
            x["res"] = x["lh"]*scale          # letter height in real scanned pixels
        allg += g
        print(f"  {os.path.relpath(p, face.PAGES)}: {len(g)}", flush=True)
    print("TOTAL:", len(allg))
    from collections import Counter
    c = Counter(g["letter"] for g in allg)
    print("per letter:", {k:c[k] for k in LETTERS})
    print("per source:", dict(Counter(g["source"] for g in allg)))
    pickle.dump(allg, open(os.path.join(face.WORK, "instances.pkl"),"wb"))
