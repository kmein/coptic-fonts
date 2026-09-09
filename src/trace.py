"""Threshold averaged templates, trace with potrace, return contours in canvas coords."""
import json, os, re, subprocess
import numpy as np
from PIL import Image

POTRACE = "/nix/store/mnnr6ch3xmn9i594w5lrv4ggg1w14n7n-potrace-1.16/bin/potrace"
UP = 2                      # upsample before thresholding: keeps the superresolution detail

def trace_template(avg, tag, outdir="trace"):
    os.makedirs(outdir, exist_ok=True)
    H,W = avg.shape
    big = np.asarray(Image.fromarray((avg*255).astype(np.uint8))
                     .resize((W*UP, H*UP), Image.BICUBIC)).astype(np.float32)/255.0
    b = big > 0.5
    ys,xs = np.where(b)
    if len(ys)==0: return [], None
    y0,y1,x0,x1 = ys.min()-2, ys.max()+3, xs.min()-2, xs.max()+3
    y0=max(y0,0); x0=max(x0,0)
    crop = b[y0:y1, x0:x1]
    pbm = f"{outdir}/{tag}.pbm"
    Image.fromarray((~crop).astype(np.uint8)*255).convert("1").save(pbm)
    svg = f"{outdir}/{tag}.svg"
    subprocess.run([POTRACE,"-s","-o",svg,"-t","6","-a","1.0","-O","0.2","-u","20",pbm], check=True)
    return parse_svg(svg, x0, y0), (x0,y0,crop.shape)

NUM = re.compile(r"-?\d*\.?\d+(?:e-?\d+)?")
def parse_svg(path, ox, oy):
    s = open(path).read()
    m = re.search(r'transform="translate\(([-\d.]+),([-\d.]+)\) scale\(([-\d.]+),([-\d.]+)\)"', s)
    tx,ty,sx,sy = (float(g) for g in m.groups())
    contours=[]
    for d in re.findall(r'<path[^>]*\sd="([^"]+)"', s):
        toks = re.findall(r"[MmLlCcVvHhZz]|-?\d*\.?\d+", d)
        i=0; cur=(0.0,0.0); start=None; cont=[]; cmd=None
        def pt(x,y):   # path space -> image pixel space -> canvas px (undo UP and crop offset)
            X = tx + sx*x; Y = ty + sy*y
            return ((X+ox)/UP, (Y+oy)/UP)
        while i < len(toks):
            t = toks[i]
            if t.isalpha(): cmd=t; i+=1
            if cmd in "Mm":
                x,y=float(toks[i]),float(toks[i+1]); i+=2
                if cmd=="m": x,y = cur[0]+x, cur[1]+y
                if cont: contours.append(cont)
                cur=(x,y); start=cur; cont=[("m", pt(x,y))]
                cmd = "L" if cmd=="M" else "l"
            elif cmd in "Ll":
                x,y=float(toks[i]),float(toks[i+1]); i+=2
                if cmd=="l": x,y = cur[0]+x, cur[1]+y
                cur=(x,y); cont.append(("l", pt(x,y)))
            elif cmd in "Hh":
                x=float(toks[i]); i+=1
                if cmd=="h": x = cur[0]+x
                cur=(x,cur[1]); cont.append(("l", pt(*cur)))
            elif cmd in "Vv":
                y=float(toks[i]); i+=1
                if cmd=="v": y = cur[1]+y
                cur=(cur[0],y); cont.append(("l", pt(*cur)))
            elif cmd in "Cc":
                v=[float(x) for x in toks[i:i+6]]; i+=6
                if cmd=="c": v=[cur[0]+v[0],cur[1]+v[1],cur[0]+v[2],cur[1]+v[3],cur[0]+v[4],cur[1]+v[5]]
                cont.append(("c", pt(v[0],v[1]), pt(v[2],v[3]), pt(v[4],v[5])))
                cur=(v[4],v[5])
            elif cmd in "Zz":
                if cont: contours.append(cont); cont=[]
                if start: cur=start
            else: i+=1
        if cont: contours.append(cont)
    return contours
