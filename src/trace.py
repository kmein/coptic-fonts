"""Threshold averaged templates, trace with potrace, return contours in canvas coords."""
import json, os, re, subprocess
import numpy as np
from PIL import Image

POTRACE = "/nix/store/mnnr6ch3xmn9i594w5lrv4ggg1w14n7n-potrace-1.16/bin/potrace"
UP = 2                      # upsample before thresholding: keeps the superresolution detail

def trace_template(avg, tag, outdir="trace", opttol="0.6", alphamax="1.0"):
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
    subprocess.run([POTRACE,"-s","-o",svg,"-t","6","-a",alphamax,"-O",opttol,"-u","20",pbm], check=True)
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


# ---------------------------------------------------------------- outline polish
import math

def _dist_to_line(p, a, b):
    (px,py),(ax,ay),(bx,by) = p,a,b
    dx,dy = bx-ax, by-ay
    L = math.hypot(dx,dy)
    if L < 1e-9: return math.hypot(px-ax, py-ay)
    return abs(dy*(px-ax) - dx*(py-ay))/L

def polish(contours, flat_tol=1.1, angle_tol=4.0, snap_tol=2.2, min_len=1.5):
    """Curves that are effectively straight become lines; collinear lines merge;
    near-horizontal / near-vertical lines snap true. Shared nodes move together, and
    the control point next to a moved node moves with it so curves stay attached."""
    out=[]
    for c in contours:
        if len(c) < 2: continue
        nodes=[seg[-1] for seg in c]                     # nodes[i] = end of segment i
        kinds=[c[i][0] for i in range(len(c))]
        ctrl ={i:(c[i][1], c[i][2]) for i in range(len(c)) if c[i][0]=="c"}
        # 1. straighten near-flat cubics
        for i in range(1, len(c)):
            if kinds[i]=="c":
                a,b = nodes[i-1], nodes[i]
                c1,c2 = ctrl[i]
                if max(_dist_to_line(c1,a,b), _dist_to_line(c2,a,b)) < flat_tol:
                    kinds[i]="l"; ctrl.pop(i, None)
        # 2. snap near-axis lines (longest first so short segments do not fight)
        segs=[i for i in range(1,len(c)) if kinds[i]=="l"]
        segs.sort(key=lambda i: -math.hypot(nodes[i][0]-nodes[i-1][0], nodes[i][1]-nodes[i-1][1]))
        moved={}
        for i in segs:
            a,b = nodes[i-1], nodes[i]
            dx,dy = b[0]-a[0], b[1]-a[1]
            L=math.hypot(dx,dy)
            if L < min_len: continue
            ang = abs(math.degrees(math.atan2(dy,dx))) % 180
            if min(ang, 180-ang) < snap_tol:                      # horizontal
                y=(a[1]+b[1])/2
                moved[i-1]=(a[0],y); moved[i]=(b[0],y)
            elif abs(ang-90) < snap_tol:                          # vertical
                x=(a[0]+b[0])/2
                moved[i-1]=(x,a[1]); moved[i]=(x,b[1])
        for idx,p in moved.items():
            old=nodes[idx]; d=(p[0]-old[0], p[1]-old[1])
            nodes[idx]=p
            if idx+1 < len(c) and (idx+1) in ctrl:                # control after the node
                c1,c2=ctrl[idx+1]; ctrl[idx+1]=((c1[0]+d[0], c1[1]+d[1]), c2)
            if idx in ctrl:                                       # control before the node
                c1,c2=ctrl[idx]; ctrl[idx]=(c1, (c2[0]+d[0], c2[1]+d[1]))
        # 3. merge consecutive near-collinear lines
        keep=[0]
        for i in range(1, len(c)):
            if (kinds[i]=="l" and keep and kinds[keep[-1]]=="l" and len(keep)>1):
                a,b,d = nodes[keep[-2]], nodes[keep[-1]], nodes[i]
                a1=math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
                a2=math.degrees(math.atan2(d[1]-b[1], d[0]-b[0]))
                turn=abs((a1-a2+180)%360-180)
                if turn < angle_tol:
                    keep[-1]=i
                    continue
            keep.append(i)
        new=[("m", nodes[0])]
        for i in keep[1:]:
            new.append(("l", nodes[i]) if kinds[i]=="l" else ("c", ctrl[i][0], ctrl[i][1], nodes[i]))
        out.append(new)
    return out
