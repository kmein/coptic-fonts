import os, json, glob, hashlib, sys
import face
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont

LETTERS = ["alpha","beta","gamma","delta","epsilon","zeta","eta","theta","iota","kappa",
           "lambda","mu","nu","ksi","omicron","pi","rho","sigma","tau","upsilon",
           "phi","khi","psi","omega","shai","fai","hori","djandja","kyima","ti"]
LC = [0x2C81,0x2C83,0x2C85,0x2C87,0x2C89,0x2C8D,0x2C8F,0x2C91,0x2C93,0x2C95,
      0x2C97,0x2C99,0x2C9B,0x2C9D,0x2C9F,0x2CA1,0x2CA3,0x2CA5,0x2CA7,0x2CA9,
      0x2CAB,0x2CAD,0x2CAF,0x2CB1,0x03E3,0x03E5,0x03E9,0x03EB,0x03ED,0x03EF]
UC = [c-1 for c in LC[:24]] + [0x03E2,0x03E4,0x03E8,0x03EA,0x03EC,0x03EE]
H = 96          # normalised glyph height in px
SLACK = 10      # translation search radius

def trim(mask):
    ys,xs = np.where(mask)
    if len(ys)==0: return None
    return mask[ys.min():ys.max()+1, xs.min():xs.max()+1]

def norm(mask, h=H):
    m = trim(mask)
    if m is None or m.shape[0] < 3: return None
    w = max(1, int(round(m.shape[1]*h/m.shape[0])))
    im = Image.fromarray((m*255).astype(np.uint8)).resize((w,h), Image.LANCZOS)
    return np.asarray(im) > 127

def iou(a, b, slack=SLACK):
    hh = max(a.shape[0], b.shape[0]) + 2*slack
    ww = max(a.shape[1], b.shape[1]) + 2*slack
    A = np.zeros((hh,ww), bool); B = np.zeros((hh,ww), bool)
    ay,ax = (hh-a.shape[0])//2, (ww-a.shape[1])//2
    by,bx = (hh-b.shape[0])//2, (ww-b.shape[1])//2
    A[ay:ay+a.shape[0], ax:ax+a.shape[1]] = a
    best = 0.0
    for dy in range(-slack, slack+1):
        for dx in range(-slack, slack+1):
            B[:] = False
            B[by+dy:by+dy+b.shape[0], bx+dx:bx+dx+b.shape[1]] = b
            inter = np.count_nonzero(A & B); union = np.count_nonzero(A | B)
            if union: best = max(best, inter/union)
    return best

def shape_stats(m):
    """stroke width + contrast from the distance transform, at normalised height"""
    d = ndimage.distance_transform_edt(m)
    v = d[m]
    if v.size == 0: return (0,0,0)
    # ridge = local maxima of EDT approximate half stroke width
    ridge = v[v >= np.percentile(v, 70)]
    return (2*float(np.mean(ridge)), float(np.percentile(v,95)/max(np.percentile(v,50),1e-6)),
            float(np.count_nonzero(m))/m.size)

def render(fontpath, cps, px=300):
    """returns {letter: mask} for the codepoints that exist and render non-empty"""
    try:
        t = TTFont(fontpath, lazy=True, fontNumber=0); cm = t.getBestCmap() or {}; t.close()
    except Exception: return {}, {}
    try: f = ImageFont.truetype(fontpath, px)
    except Exception: return {}, {}
    out, raw = {}, {}
    for name, cp in zip(LETTERS, cps):
        if cp not in cm: continue
        img = Image.new("L", (px*3, px*3), 255)
        ImageDraw.Draw(img).text((px, px), chr(cp), font=f, fill=0)
        m = np.asarray(img) < 128
        if not m.any(): continue
        tm = trim(m)
        if tm is None or tm.shape[0] < 4: continue
        raw[name] = tm.shape          # (h,w) at fixed em size -> proportion info
        n = norm(m)
        if n is not None: out[name] = n
    return out, raw

# ---- reference ----
ref, ref_raw = {}, {}
for p in sorted(glob.glob(os.path.join(face.REF, "*.png"))):
    idx, name = os.path.basename(p)[:-4].split("_",1)
    m = np.asarray(Image.open(p).convert("L")) < 128
    tm = trim(m); ref_raw[name] = tm.shape
    ref[name] = norm(m)
ref_stats = {k: shape_stats(v) for k,v in ref.items()}

def compare(fontpath, label):
    lo,_lr = render(fontpath, LC); up,_ur = render(fontpath, UC)
    if not lo and not up: return None
    per, used, raws = {}, {}, {}
    for name in LETTERS:
        if name not in ref: continue
        best, bestcase, bestmask = 0.0, None, None
        for case, d, rr in (("lc",lo,_lr), ("uc",up,_ur)):
            if name in d:
                s = iou(ref[name], d[name])
                if s > best: best, bestcase, bestmask = s, case, d[name]; raws[name]=rr[name]
        if bestcase:
            per[name] = best; used[name] = bestcase
            if name not in raws: raws[name] = None
            per.setdefault(name, best)
    if not per: return None
    # shape descriptors on the matched masks
    sw, ct, dens = [], [], []
    for name in per:
        d = lo if used[name]=="lc" else up
        s = shape_stats(d[name]); r = ref_stats[name]
        if r[0]>0: sw.append(s[0]/r[0])
        ct.append(s[1]); dens.append(s[2]/r[2] if r[2]>0 else np.nan)
    # proportion: relative ink heights across letters vs reference
    common = [n for n in LETTERS if n in per and raws.get(n)]
    hv = np.array([raws[n][0] for n in common], float)
    rv = np.array([ref_raw[n][0] for n in common], float)
    wv = np.array([raws[n][1] for n in common], float)
    rwv= np.array([ref_raw[n][1] for n in common], float)
    hcorr = float(np.corrcoef(hv/hv.mean(), rv/rv.mean())[0,1]) if len(common)>3 else np.nan
    wcorr = float(np.corrcoef(wv/wv.mean(), rwv/rwv.mean())[0,1]) if len(common)>3 else np.nan
    return dict(label=label, file=fontpath, n=len(per), mean_iou=float(np.mean(list(per.values()))),
                per=per, case={k:v for k,v in used.items()},
                weight_ratio=float(np.nanmean(sw)), contrast=float(np.nanmean(ct)),
                density_ratio=float(np.nanmean(dens)), h_corr=hcorr, w_corr=wcorr)

if __name__ == "__main__":
    cands = json.load(open(sys.argv[1]))
    res=[]
    for c in cands:
        r = compare(c["file"], c["label"])
        if r: res.append(r); print(f"{r['mean_iou']:.3f}  {r['label']}", flush=True)
        else: print(f"  --   {c['label']} (no glyphs)", flush=True)
    res.sort(key=lambda x:-x["mean_iou"])
    json.dump(res, open("scores.json","w"), indent=1)
