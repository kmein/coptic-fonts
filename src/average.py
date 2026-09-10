"""Register and average all instances of each letter -> superresolved templates.

Every instance is rendered into a common canvas at its line's letter height (so the
canvas pixel is a fraction of a source pixel), then registered to the running average
by cross-correlation and averaged again. Instances are weighted by the square of their
letter height in scanned pixels: a letter scanned at 40 px carries more edge information
than one at 22 px, and the registration is more precise. Outliers (merged or broken
glyphs) are rejected against the registered average.
"""
import pickle, json, os
import face
import numpy as np
from PIL import Image
from scipy.signal import correlate
import score as S

TARGET = 256          # normalised letter height (a typical letter's ink height)
CW, CH = 700, 900     # canvas
BASE   = 700          # baseline y within canvas
MAXN   = 500          # per letter and source
WIN    = 16           # registration search radius, canvas px
ITERS  = 3
# cache window of the canvas that any letter can touch (rows, cols)
CY0, CY1, CX0, CX1 = 280, 840, 60, 640

def place(inst, dx=0.0, dy=0.0):
    """render one instance into the canvas at its true scale/baseline, subpixel-accurate"""
    m = inst["mask"]
    scale = TARGET / inst["lh"]
    src = Image.fromarray((m*255).astype(np.uint8))
    ys,xs = np.where(m)
    cx = (xs.min()+xs.max()+1)/2.0                 # ink centre (source px)
    by = m.shape[0] - (inst["bottom"] - inst["base"])   # baseline y in source coords
    ox = CW/2.0 + dx; oy = BASE + dy
    a = 1.0/scale; c = cx - ox/scale
    e = 1.0/scale; f = by - oy/scale
    out = src.transform((CW,CH), Image.AFFINE, (a,0,c, 0,e,f), resample=Image.BICUBIC, fillcolor=0)
    return np.asarray(out).astype(np.float32)/255.0

def register(img, cur, box):
    """integer canvas shift (dy,dx) that best overlays img on cur, searched within WIN"""
    y0,y1,x0,x1 = box
    c = correlate(cur[y0:y1, x0:x1], img[y0:y1, x0:x1], mode="same", method="fft")
    cy, cx = (y1-y0)//2, (x1-x0)//2
    w = c[cy-WIN:cy+WIN+1, cx-WIN:cx+WIN+1]
    dy, dx = np.unravel_index(int(np.argmax(w)), w.shape)
    return dy-WIN, dx-WIN

def shifted(img, dy, dx):
    out = np.zeros_like(img)
    H,W = img.shape
    ys = slice(max(dy,0), H+min(dy,0)); xs = slice(max(dx,0), W+min(dx,0))
    yd = slice(max(-dy,0), H+min(-dy,0)); xd = slice(max(-dx,0), W+min(-dx,0))
    out[ys, xs] = img[yd, xd]
    return out

def average(insts, iters=ITERS):
    imgs = [place(g)[CY0:CY1, CX0:CX1] for g in insts]
    wts  = np.array([g.get("res", g["lh"])**2 for g in insts], np.float64)
    wts /= wts.mean()
    cur = None; keep = np.ones(len(imgs), bool); shifts = [(0,0)]*len(imgs)
    for it in range(iters):
        if cur is not None:
            t = cur > 0.5
            ys,xs = np.where(t)
            box = (max(ys.min()-2*WIN,0), min(ys.max()+2*WIN+1, cur.shape[0]),
                   max(xs.min()-2*WIN,0), min(xs.max()+2*WIN+1, cur.shape[1]))
            for i,img in enumerate(imgs):
                dy,dx = register(img, cur, box)
                shifts[i] = (dy,dx)
                b = shifted(img, dy, dx) > 0.5
                inter = np.count_nonzero(b&t); union = np.count_nonzero(b|t)
                keep[i] = bool(union) and inter/union >= 0.75      # outlier: merged/broken glyph
        acc = np.zeros(imgs[0].shape, np.float64); n = 0.0
        for i,img in enumerate(imgs):
            if not keep[i]: continue
            acc += wts[i]*shifted(img, *shifts[i]); n += wts[i]
        if n == 0: return None, 0, None
        cur = (acc/n).astype(np.float32)
    full = np.zeros((CH,CW), np.float32); full[CY0:CY1, CX0:CX1] = cur
    return full, int(keep.sum()), keep

if __name__ == "__main__":
    insts = pickle.load(open(os.path.join(face.WORK, "instances.pkl"),"rb"))
    by = {}
    for g in insts: by.setdefault(g["letter"], []).append(g)
    rng = np.random.default_rng(0)
    tpl, meta = {}, {}
    for name in S.LETTERS:
        L = by.get(name, [])
        if not L: print(f"  {name}: NO INSTANCES"); continue
        # cap per source, best-classified first
        bysrc = {}
        for g in L: bysrc.setdefault(g.get("source",""), []).append(g)
        sel = []
        for src, G in bysrc.items():
            G.sort(key=lambda g: -g["score"])
            sel += G[:MAXN]
        avg, n, keep = average(sel)
        if avg is None: continue
        tpl[name] = avg
        b = avg > 0.5
        ys,xs = np.where(b)
        srcs = {}
        for g,k in zip(sel, keep):
            s = g.get("source",""); srcs.setdefault(s, [0,0]); srcs[s][1] += 1; srcs[s][0] += int(k)
        meta[name] = dict(n=n, pool=len(L), sources={s:dict(n=v[0], pool=len(bysrc[s])) for s,v in srcs.items()},
                          top=int(ys.min()), bottom=int(ys.max())+1,
                          left=int(xs.min()), right=int(xs.max())+1,
                          height=int(ys.max()-ys.min()+1), width=int(xs.max()-xs.min()+1),
                          desc=int(ys.max()+1-BASE))
        print(f"  {name:9s} n={n:4d}/{len(sel):4d} of {len(L):5d}  h={meta[name]['height']:3d} w={meta[name]['width']:3d} "
              f"desc={meta[name]['desc']:+4d}  " + " ".join(f"{s}:{v[0]}/{v[1]}" for s,v in srcs.items()), flush=True)
    np.savez_compressed(os.path.join(face.DATA, "templates.npz"), **tpl)
    json.dump(meta, open(os.path.join(face.DATA, "template_meta.json"),"w"), indent=1)
