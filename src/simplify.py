"""FontForge pass: turn the traced outlines into clean curves and straight lines.

Run:  fontforge -lang=py -script src/simplify.py LaytonCoptic-Regular.otf 4
Reads the OTF written by build_font.py, simplifies each glyph within an error budget
(font units), and regenerates both OTF and TTF in place. A glyph whose simplified
outline throws a point outside its plausible box is retried one unit lower, since
FontForge occasionally produces a wild control point at larger budgets.
"""
import fontforge, sys
src = sys.argv[1]; target = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
SKIP = (".notdef", "space", "hyphen", "uni0305")
BOX  = (-900, 1400, -320, 1050)

def clean(g, minpts=3, minsize=18):
    keep = fontforge.layer()
    for c in g.foreground:
        pts = [(p.x, p.y) for p in c]
        if len(pts) < minpts: continue
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if max(xs)-min(xs) < minsize and max(ys)-min(ys) < minsize: continue
        keep += c
    g.foreground = keep

def sane(g):
    for c in g.foreground:
        xs = [p.x for p in c]; ys = [p.y for p in c]
        if min(xs) < BOX[0] or max(xs) > BOX[1] or min(ys) < BOX[2] or max(ys) > BOX[3]:
            return False
    return True

def simplify(g, err):
    g.simplify(err, ("smoothcurves", "mergelines", "choosehv", "setstarttoextremum"), 0.2, 0, 0.5)
    g.addExtrema("all")
    g.round()
    g.simplify(0.4, ("mergelines", "choosehv"), 0.2, 0, 0.5)
    clean(g)

f = fontforge.open(src)
used = {}
for g in f.glyphs():
    if g.glyphname in SKIP: continue
    clean(g)
    original = g.foreground
    err = target
    while err >= 1.0:
        g.foreground = original
        simplify(g, err)
        if sane(g): break
        err -= 1.0
    else:
        g.foreground = original
        err = 0.0
    used[g.glyphname] = err
f.generate(src)
f.generate(src[:-4] + ".ttf")
pts = sum(len(c) for g in f.glyphs() for c in g.foreground)
low = {k: v for k, v in used.items() if v != target}
print(f"simplified at {target:g}: {pts} points total; fell back on {low if low else 'nothing'}")
