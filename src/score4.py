import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
import score as S

def disk(r):
    y,x = np.ogrid[-r:r+1, -r:r+1]
    return x*x+y*y <= r*r+0.1

def morph(m, k):
    if k == 0: return m
    return (ndimage.binary_dilation if k>0 else ndimage.binary_erosion)(m, disk(abs(k)))

def stroke(m):
    """mean stroke width: 2x the mean EDT over the glyph's ridge"""
    d = ndimage.distance_transform_edt(m); v = d[m]
    return 2*float(np.mean(v[v >= np.percentile(v,70)])) if v.size else 0.0

def box(m, h=S.H):
    """normalise BOTH axes -> pure shape, aspect removed"""
    im = Image.fromarray((m*255).astype(np.uint8)).resize((h,h), Image.LANCZOS)
    return np.asarray(im) > 127

REF = S.ref
ref_stroke = {k: stroke(v) for k,v in REF.items()}
ref_box    = {k: box(v)    for k,v in REF.items()}

def analyse(path, label):
    lo,lr = S.render(path, S.LC); up,ur = S.render(path, S.UC)
    if not lo and not up: return None
    # case choice per letter: whichever renders (prefer lowercase, the running-text form)
    g, raw = {}, {}
    for n in S.LETTERS:
        if n in lo: g[n]=lo[n]; raw[n]=lr[n]
        elif n in up: g[n]=up[n]; raw[n]=ur[n]
    common = [n for n in g if n in REF]
    if not common: return None
    # weight match: pick k so mean stroke width matches the reference's
    ratios = {}
    for k in range(0,7):
        r = np.mean([stroke(morph(g[n],k))/ref_stroke[n] for n in common if ref_stroke[n]>0])
        ratios[k] = r
    k = min(ratios, key=lambda k: abs(ratios[k]-1.0))
    per_free, per_box = {}, {}
    for n in common:
        mk = morph(g[n], k)
        per_free[n] = S.iou(REF[n], mk)
        per_box[n]  = S.iou(ref_box[n], box(mk), slack=6)
    # identity rate: does each font glyph match its OWN reference letter best?
    hits = 0
    for n in common:
        mk = morph(g[n], k)
        sc = {r: S.iou(ref_box[r], box(mk), slack=6) for r in ref_box}
        if max(sc, key=sc.get) == n: hits += 1
    ar  = np.array([raw[n][1]/raw[n][0] for n in common])
    rar = np.array([S.ref_raw[n][1]/S.ref_raw[n][0] for n in common])
    hv  = np.array([raw[n][0] for n in common], float); rv = np.array([S.ref_raw[n][0] for n in common], float)
    return dict(label=label, file=path, k=k, weight_ratio_before=float(ratios[0]),
                iou_free=float(np.mean(list(per_free.values()))),
                iou_box=float(np.mean(list(per_box.values()))),
                per_free=per_free, per_box=per_box, n=len(common),
                identity=hits/len(common),
                width_ratio=float(np.mean(ar/rar)),
                aspect_dev=float(np.mean(np.abs(ar-rar)/rar)),
                h_corr=float(np.corrcoef(hv/hv.mean(), rv/rv.mean())[0,1]))

if __name__ == "__main__":
    cands = json.load(open("cands.json"))
    out=[]
    for c in cands:
        r = analyse(c["file"], c["label"])
        if r:
            out.append(r)
            print(f"{r['iou_box']:.3f} shape | {r['iou_free']:.3f} +prop | id {r['identity']:.2f} "
                  f"| k={r['k']} wt0={r['weight_ratio_before']:.2f} wd={r['width_ratio']:.2f}  {r['label']}", flush=True)
    out.sort(key=lambda r:-r["iou_box"])
    json.dump(out, open("scores4.json","w"), indent=1)
