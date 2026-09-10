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
        version="1.300", monospace=False, lighten=0.16,
        description=("Revival of the Coptic type used in Bentley Layton's A Coptic Grammar "
                     "(Harrassowitz 2000) and in the Bibliotheque copte de Nag Hammadi. "
                     "Outlines traced from registered and averaged page scans; metrics "
                     "measured from the printed setting."),
        # reference alphabet: Grammar Table 1, PDF p. 30; one column of 30 rows
        ref_crops=[(300, 602, 780, 3780)],
        # pages the supralinear stroke, hyphen and word space are measured on (all of them)
        bars_glob="grammar/*.png", spacing_glob="grammar/*.png", metrics_source="grammar",
        # pages/<source>/: the Grammar (600 dpi bilevel) and Zostrianos, BCNH 24 (Peeters 2000),
        # a 300 dpi greyscale scan rendered at 600 dpi so its soft edges survive thresholding;
        # source_scale gives real pixels per rendered pixel, so instances are weighted by
        # the resolution they were actually scanned at
        source_scale={"zost": 0.5},
        # expected ink height (h / letter height) and descent below the baseline of each
        # letter, from the v1.2 templates; harvest.py keeps only instances that fit
        geom={"alpha":(1.00,0.00),"beta":(0.99,-0.03),"gamma":(0.97,0.00),"delta":(1.00,0.00),
              "epsilon":(1.00,0.00),"zeta":(1.22,0.11),"eta":(0.98,-0.02),"theta":(1.00,0.00),
              "iota":(1.00,0.00),"kappa":(1.00,0.00),"lambda":(1.00,0.00),"mu":(0.99,-0.01),
              "nu":(0.98,0.00),"ksi":(1.27,0.11),"omicron":(1.00,0.00),"pi":(0.98,0.00),
              "rho":(1.39,0.42),"sigma":(1.00,0.00),"tau":(1.00,0.00),"upsilon":(1.41,0.41),
              "phi":(1.85,0.42),"khi":(1.00,0.00),"psi":(1.89,0.42),"omega":(1.00,0.00),
              "shai":(1.41,0.43),"fai":(1.40,0.40),"hori":(1.42,0.42),"djandja":(1.12,0.12),
              "kyima":(1.40,0.00),"ti":(1.84,0.42)},
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
        # from the v1.0 templates (see layton)
        geom={"alpha":(1.03,0.00),"beta":(0.95,-0.05),"gamma":(0.99,-0.03),"delta":(1.00,0.03),
              "epsilon":(0.98,0.00),"zeta":(1.00,0.00),"eta":(0.98,-0.05),"theta":(1.00,0.00),
              "iota":(1.03,0.00),"kappa":(0.97,-0.03),"lambda":(0.97,-0.03),"mu":(1.00,0.00),
              "nu":(1.02,0.00),"ksi":(1.00,0.00),"omicron":(1.00,0.00),"pi":(1.00,0.00),
              "rho":(1.35,0.38),"sigma":(0.97,-0.03),"tau":(0.95,0.00),"upsilon":(1.30,0.30),
              "phi":(1.84,0.46),"khi":(1.00,0.00),"psi":(1.43,0.11),"omega":(0.94,0.00),
              "shai":(1.20,0.31),"fai":(0.96,-0.01),"hori":(0.98,0.13),"djandja":(1.00,0.00),
              "kyima":(1.05,-0.03),"ti":(1.84,0.43)},
    ),
}
CFG = FACES[FACE]
for d in (DATA, REF, WORK):
    os.makedirs(d, exist_ok=True)
