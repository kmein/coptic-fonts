"""Subpixel-align and average all instances of each letter -> superresolved templates."""
import pickle, json
import numpy as np
from PIL import Image
import score as S

TARGET = 256          # normalised letter height (a typical letter's ink height)
CW, CH = 700, 900     # canvas
BASE   = 700          # baseline y within canvas
MAXN   = 500

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

def average(insts, iters=2):
    cur = None
    used = insts
    for it in range(iters):
        acc = np.zeros((CH,CW), np.float64); n=0
        keep=[]
        for inst in used:
            img = place(inst, *inst.get("shift",(0.0,0.0)))
            if cur is not None:
                b = img > 0.5; t = cur > 0.5
                inter = np.count_nonzero(b&t); union = np.count_nonzero(b|t)
                if union and inter/union < 0.75: continue      # outlier: merged/broken glyph
            acc += img; n += 1; keep.append(inst)
        if n == 0: return None, 0
        cur = (acc/n).astype(np.float32)
        used = keep
    return cur, len(used)

if __name__ == "__main__":
    insts = pickle.load(open("instances.pkl","rb"))
    by = {}
    for g in insts: by.setdefault(g["letter"], []).append(g)
    rng = np.random.default_rng(0)
    tpl, meta = {}, {}
    for name in S.LETTERS:
        L = by.get(name, [])
        if not L: print(f"  {name}: NO INSTANCES"); continue
        L.sort(key=lambda g: -g["score"])
        if len(L) > MAXN:
            L = [L[i] for i in rng.choice(len(L), MAXN, replace=False)]
        avg, n = average(L)
        if avg is None: continue
        tpl[name] = avg
        b = avg > 0.5
        ys,xs = np.where(b)
        meta[name] = dict(n=n, pool=len(by[name]),
                          top=int(ys.min()), bottom=int(ys.max())+1,
                          left=int(xs.min()), right=int(xs.max())+1,
                          height=int(ys.max()-ys.min()+1), width=int(xs.max()-xs.min()+1),
                          desc=int(ys.max()+1-BASE))
        print(f"  {name:9s} n={n:4d}/{len(by[name]):5d}  h={meta[name]['height']:3d} w={meta[name]['width']:3d} "
              f"desc={meta[name]['desc']:+4d}", flush=True)
    np.savez_compressed("templates.npz", **tpl)
    json.dump(meta, open("template_meta.json","w"), indent=1)
