"""Assemble the traced letterforms into OTF + TTF."""
import json
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
import trace as TR
import refine as RF
import score as S

BASE, TARGET = 700, 256
SIGMA    = 4.0    # smoothing of the averaged template before tracing
CONTRAST = 7      # px of x-growth / y-shrink: widens the thick/thin difference
LETTER_H = 620                      # letter height in font units
K = LETTER_H / TARGET
UPEM = 1000
FAMILY, STYLE = "Layton Coptic", "Regular"
VERSION = "1.100"

CP = {   # letter -> (small, capital) codepoints; the type is unicase, one outline serves both
 "alpha":(0x2C81,0x2C80), "beta":(0x2C83,0x2C82), "gamma":(0x2C85,0x2C84), "delta":(0x2C87,0x2C86),
 "epsilon":(0x2C89,0x2C88), "zeta":(0x2C8D,0x2C8C), "eta":(0x2C8F,0x2C8E), "theta":(0x2C91,0x2C90),
 "iota":(0x2C93,0x2C92), "kappa":(0x2C95,0x2C94), "lambda":(0x2C97,0x2C96), "mu":(0x2C99,0x2C98),
 "nu":(0x2C9B,0x2C9A), "ksi":(0x2C9D,0x2C9C), "omicron":(0x2C9F,0x2C9E), "pi":(0x2CA1,0x2CA0),
 "rho":(0x2CA3,0x2CA2), "sigma":(0x2CA5,0x2CA4), "tau":(0x2CA7,0x2CA6), "upsilon":(0x2CA9,0x2CA8),
 "phi":(0x2CAB,0x2CAA), "khi":(0x2CAD,0x2CAC), "psi":(0x2CAF,0x2CAE), "omega":(0x2CB1,0x2CB0),
 "shai":(0x03E3,0x03E2), "fai":(0x03E5,0x03E4), "hori":(0x03E9,0x03E8), "djandja":(0x03EB,0x03EA),
 "kyima":(0x03ED,0x03EC), "ti":(0x03EF,0x03EE),
}
GNAME = {n:"uni%04X"%CP[n][0] for n in CP}

def signed_area(pts):
    a=0.0
    for (x0,y0),(x1,y1) in zip(pts, pts[1:]+pts[:1]): a += x0*y1 - x1*y0
    return a/2.0

def inside(p, poly):
    x,y=p; c=False; n=len(poly)
    for i in range(n):
        x0,y0=poly[i]; x1,y1=poly[(i+1)%n]
        if (y0>y) != (y1>y):
            xi = x0 + (y-y0)*(x1-x0)/(y1-y0)
            if x < xi: c = not c
    return c

MIN_AREA = 150.0     # drop trace specks

def orient(contours, outer_positive_in_font):
    """Nonzero winding. CFF wants outer CCW (positive); TrueType wants outer CW."""
    contours=[c for c in contours if abs(signed_area([seg[-1] for seg in c])) >= MIN_AREA]
    polys=[[seg[-1] for seg in c] for c in contours]
    out=[]
    for i,c in enumerate(contours):
        depth = sum(1 for j,p in enumerate(polys) if j!=i and inside(polys[i][0], p))
        a = signed_area(polys[i])
        # canvas y is flipped on the way into font space, so invert the target sign here
        want_pos = ((depth % 2 == 0) == (not outer_positive_in_font))
        if (a > 0) != want_pos:
            # reverse: rebuild the contour backwards, flipping cubic control order
            pts=[c[0][-1]]+[s[-1] for s in c[1:]]
            rev=[("m", pts[-1])]
            for k in range(len(c)-1, 0, -1):
                seg = c[k]
                rev.append(("l", pts[k-1]) if seg[0]=="l" else ("c", seg[2], seg[1], pts[k-1]))
            first = c[0]
            out.append(rev)
        else:
            out.append(c)
    return out

def draw(contours, pen, ox, outer_positive_in_font):
    def T(p): return (round((p[0]-ox)*K), round((BASE-p[1])*K))
    for c in orient(contours, outer_positive_in_font):
        pen.moveTo(T(c[0][1]))
        for seg in c[1:]:
            if seg[0]=="l": pen.lineTo(T(seg[1]))
            else: pen.curveTo(T(seg[1]), T(seg[2]), T(seg[3]))
        pen.closePath()

def rect(pen, x0,y0,x1,y1):
    pen.moveTo((round(x0),round(y0))); pen.lineTo((round(x1),round(y0)))
    pen.lineTo((round(x1),round(y1))); pen.lineTo((round(x0),round(y1))); pen.closePath()

# ---------- gather geometry ----------
tpl = np.load("templates.npz")
meta = json.load(open("template_meta.json"))
sp = json.load(open("spacing.json")); bars = json.load(open("bars.json"))
GAP = sp["gap"]
shapes, widths, LSB = {}, {}, {}
for name in S.LETTERS:
    if name not in tpl: continue
    contours,_ = TR.trace_template(RF.refine(tpl[name], sigma=SIGMA, contrast=CONTRAST), name, opttol="0.3", alphamax="1.2")
    contours = TR.polish(contours, flat_tol=0.6, angle_tol=1.2, snap_tol=1.2, min_len=25)
    xs = [p[0] for c in contours for seg in c for p in seg[1:]]
    ink_l, ink_r = min(xs), max(xs); w = ink_r - ink_l
    a = sp["adv"].get(name)
    adv = a["advance"] if (a and a["n"] >= 20) else w + GAP
    adv = max(adv, w + 0.45*GAP)
    lsb = (adv - w)/2.0
    shapes[name] = (contours, ink_l - lsb)
    widths[name] = adv; LSB[name] = lsb
    print(f"  {name:9s} ink {w:6.1f} adv {adv:6.1f} lsb {lsb:5.1f}", flush=True)
typ_adv = float(np.median(list(widths.values())))

# ---------- build ----------
order = [".notdef","space","hyphen","uni0305"] + [GNAME[n] for n in S.LETTERS if n in shapes]
cmap = {0x20:"space", 0x2D:"hyphen", 0x0305:"uni0305"}
for n in shapes:
    cmap[CP[n][0]] = GNAME[n]; cmap[CP[n][1]] = GNAME[n]
ov, hy = bars["overline"], bars["hyphen"]
adv_units = {".notdef": round(0.5*LETTER_H), "space": round(TARGET*K),
             "hyphen": round((hy["ln"]+GAP)*K), "uni0305": 0}
for n in shapes: adv_units[GNAME[n]] = round(widths[n]*K)
xmin = {".notdef":60, "space":0, "hyphen":round(GAP/2*K),
        "uni0305":round((-typ_adv/2-ov["ln"]/2)*K)}
for n in shapes: xmin[GNAME[n]] = round(LSB[n]*K)

CFF_MODE=[True]
def build(pens_factory, finish):
    glyphs={}
    for gname in order:
        pen = pens_factory(gname)
        if gname == ".notdef":
            rect(pen, 60, 0, adv_units[".notdef"]-60, LETTER_H)
            rect(pen, 110, 50, adv_units[".notdef"]-110, LETTER_H-50)
        elif gname == "space": pass
        elif gname == "hyphen":
            x0 = GAP/2*K; rect(pen, x0, (hy["y"]-hy["th"]/2)*K, x0+hy["ln"]*K, (hy["y"]+hy["th"]/2)*K)
        elif gname == "uni0305":
            cx = -typ_adv/2*K
            rect(pen, cx-ov["ln"]/2*K, ov["y"]*K, cx+ov["ln"]/2*K, (ov["y"]+ov["th"])*K)
        else:
            name = [n for n in shapes if GNAME[n]==gname][0]
            contours, ox = shapes[name]; draw(contours, pen, ox, CFF_MODE[0])
        glyphs[gname] = finish(pen, gname)
    return glyphs

names = dict(familyName=FAMILY, styleName=STYLE, uniqueFontIdentifier=f"{FAMILY} {VERSION}",
             fullName=f"{FAMILY} {STYLE}", version=VERSION, psName=f"LaytonCoptic-{STYLE}",
             designer="Digitised from printed specimens",
             description=("Revival of the Coptic type used in Bentley Layton's A Coptic Grammar "
                          "(Harrassowitz 2000) and Coptic Gnostic Chrestomathy (Peeters 2004). "
                          "Outlines traced from averaged 600 dpi page scans; metrics measured from "
                          "the printed setting."))
def setup(fb, glyphs, is_ttf):
    fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
    if is_ttf: fb.setupGlyf(glyphs)
    else: fb.setupCFF(names["psName"], {"FullName":names["fullName"]}, glyphs, {})
    metrics = {g:(adv_units[g], 0) for g in order}
    if is_ttf:
        metrics = {g:(adv_units[g], glyphs[g].xMin if hasattr(glyphs[g],'xMin') else 0) for g in order}
    fb.setupHorizontalMetrics({g:(adv_units[g], xmin[g]) for g in order})
    fb.setupHorizontalHeader(ascent=1000, descent=-270, lineGap=0)
    fb.setupNameTable(names)
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-270, sTypoLineGap=200,
                usWinAscent=1000, usWinDescent=270, sCapHeight=LETTER_H, sxHeight=LETTER_H,
                achVendID="LYTN", fsType=0)
    fb.setupPost(isFixedPitch=0)

# OTF (CFF, cubic)
cs={}
fb = FontBuilder(UPEM, isTTF=False)
def cff_pen(g):
    return T2CharStringPen(adv_units[g], None)
glyphs = build(cff_pen, lambda pen,g: pen.getCharString())
setup(fb, glyphs, False)
fb.save("LaytonCoptic-Regular.otf")
print("wrote LaytonCoptic-Regular.otf")

# TTF (quadratic)
fb2 = FontBuilder(UPEM, isTTF=True)
def tt_pen(g):
    tp = TTGlyphPen(None)
    cq = Cu2QuPen(tp, max_err=0.6); cq._tt = tp
    return cq
def tt_finish(pen, g):
    return pen._tt.glyph()
CFF_MODE[0]=False
glyphs2 = build(tt_pen, tt_finish)
setup(fb2, glyphs2, True)
fb2.save("LaytonCoptic-Regular.ttf")
print("wrote LaytonCoptic-Regular.ttf")
