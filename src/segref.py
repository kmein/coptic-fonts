import numpy as np, os, sys
import face
from PIL import Image
from scipy import ndimage

LETTERS = ["alpha","beta","gamma","delta","epsilon","zeta","eta","theta","iota","kappa",
           "lambda","mu","nu","ksi","omicron","pi","rho","sigma","tau","upsilon",
           "phi","khi","psi","omega","shai","fai","hori","djandja","kyima","ti"]

img = Image.open(sys.argv[1]).convert("L")
crops = face.CFG["ref_crops"]
out=[]; idx=0
for (x0,x1,y0,y1) in crops:
    a = np.asarray(img.crop((x0,y0,x1,y1)), dtype=np.uint8)
    ink = a < 128
    proj = ink.sum(axis=1)
    rows=[]; inrow=False
    for i,v in enumerate(proj):
        if v>0 and not inrow: start=i; inrow=True
        elif v==0 and inrow:
            if i-start > 20: rows.append((start,i))
            inrow=False
    if inrow: rows.append((start,len(proj)))
    print(f"crop x{x0}-{x1}: {len(rows)} rows")
    for (ra,rb) in rows:
        band = ink[ra:rb]
        cp = band.sum(axis=0)
        cols=[]; inc=False
        for j,v in enumerate(cp):
            if v>0 and not inc: cs=j; inc=True
            elif v==0 and inc:
                if j-cs>3: cols.append((cs,j))
                inc=False
        if inc: cols.append((cs,len(cp)))
        merged=[]
        for c in cols:
            if merged and c[0]-merged[-1][1] < 12: merged[-1]=(merged[-1][0], c[1])
            else: merged.append((c[0],c[1]))
        ca,cb = merged[0]
        g = band[:, ca:cb]
        ys = np.where(g.any(axis=1))[0]
        g = g[ys[0]:ys[-1]+1]
        name = LETTERS[idx] if idx < len(LETTERS) else "extra%d"%idx
        Image.fromarray((~g*255).astype(np.uint8)).save(os.path.join(face.REF, f"{idx:02d}_{name}.png"))
        out.append((idx,name,rb-ra,g.shape,len(merged)))
        idx += 1
for o in out: print(o)
print("letters written:", idx, "->", face.REF)
