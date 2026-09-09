import numpy as np, os, sys
from PIL import Image
from scipy import ndimage

LETTERS = ["alpha","beta","gamma","delta","epsilon","zeta","eta","theta","iota","kappa",
           "lambda","mu","nu","ksi","omicron","pi","rho","sigma","tau","upsilon",
           "phi","khi","psi","omega","shai","fai","hori","djandja","kyima","ti"]

img = Image.open(sys.argv[1]).convert("L")
x0,y0,x1,y1 = 300,780,602,3780
a = np.asarray(img.crop((x0,y0,x1,y1)), dtype=np.uint8)
# Otsu
hist = np.bincount(a.ravel(), minlength=256).astype(float)
tot = hist.sum(); w = np.cumsum(hist); m = np.cumsum(hist*np.arange(256))
mt = m[-1]
with np.errstate(invalid="ignore", divide="ignore"):
    var = (mt*w/tot - m)**2 / (w*(tot-w))
thr = 128
ink = a < thr
print("otsu thr", thr, "ink frac", ink.mean().round(4))

# rows by horizontal projection
proj = ink.sum(axis=1)
rows=[]; inrow=False
for i,v in enumerate(proj):
    if v>0 and not inrow: start=i; inrow=True
    elif v==0 and inrow:
        if i-start > 20: rows.append((start,i))
        inrow=False
if inrow: rows.append((start,len(proj)))
print("rows found:", len(rows))

os.makedirs("ref", exist_ok=True)
out=[]
for idx,(ra,rb) in enumerate(rows):
    band = ink[ra:rb]
    cp = band.sum(axis=0)
    cols=[]; inc=False
    for j,v in enumerate(cp):
        if v>0 and not inc: cs=j; inc=True
        elif v==0 and inc:
            if j-cs>3: cols.append((cs,j))
            inc=False
    if inc: cols.append((cs,len(cp)))
    # merge clusters separated by < 12 px (600dpi: intra-glyph gaps)
    merged=[]
    for c in cols:
        if merged and c[0]-merged[-1][1] < 12: merged[-1]=(merged[-1][0], c[1])
        else: merged.append(list(c) if False else (c[0],c[1]))
    ca,cb = merged[0]
    g = band[:, ca:cb]
    ys = np.where(g.any(axis=1))[0]
    g = g[ys[0]:ys[-1]+1]
    name = LETTERS[idx] if idx < len(LETTERS) else "extra%d"%idx
    Image.fromarray((~g*255).astype(np.uint8)).save(f"ref/{idx:02d}_{name}.png")
    out.append((idx,name,rb-ra,g.shape,len(merged)))
for o in out: print(o)
