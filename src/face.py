"""Which face the pipeline works on. FACE=<name> in the environment; default layton."""
import os
FACE = os.environ.get("FACE", "layton")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR   = os.path.join(ROOT, "faces", FACE)
DATA  = os.path.join(DIR, "data")
REF   = os.path.join(DATA, "ref")
PAGES = os.path.join(DIR, "pages")     # 600 dpi renders, untracked
WORK  = os.path.join(DIR, "work")      # instances.pkl, trace output, untracked

FACES = {
    "layton": dict(
        family="Layton Coptic", ps="LaytonCoptic", out="LaytonCoptic-Regular",
        version="1.200", monospace=False, lighten=0.16,
        description=("Revival of the Coptic type used in Bentley Layton's A Coptic Grammar "
                     "(Harrassowitz 2000) and Coptic Gnostic Chrestomathy (Peeters 2004). "
                     "Outlines traced from averaged 600 dpi page scans; metrics measured from "
                     "the printed setting."),
        # reference alphabet: Grammar Table 1, PDF p. 30; one column of 30 rows
        ref_crops=[(300, 602, 780, 3780)],
        # pages used for bar / overline / spacing measurements
        bars_glob="p-4*.png", spacing_glob="p-46*.png",
    ),
    "lambdin": dict(
        family="Lambdin Coptic", ps="LambdinCoptic", out="LambdinCoptic-Regular",
        version="1.000", monospace=False,   # measured: advances vary continuously by letter, no fixed pitch
        lighten=0.0,                          # smoothing alone strips the ribbon fuzz: weight 0.94 vs page
        description=("Revival of the typewriter Coptic in Thomas O. Lambdin's Introduction to "
                     "Sahidic Coptic (Mercer 1983). Fixed pitch. Outlines traced from averaged "
                     "600 dpi page scans; metrics measured from the typed setting."),
        # reference alphabet: PDF p. 10, five columns of six rows, column-major
        ref_crops=[(600,740,1200,1910),(1130,1260,1200,1910),(1700,1830,1200,1910),
                   (2250,2380,1200,1910),(2800,2940,1200,1910)],
        bars_glob="r-*.png", spacing_glob="r-*.png",
    ),
}
CFG = FACES[FACE]
for d in (DATA, REF, WORK):
    os.makedirs(d, exist_ok=True)
