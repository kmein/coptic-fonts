# Layton Coptic

A digital revival of the Coptic type used in Bentley Layton's *A Coptic Grammar*
(Harrassowitz 2000) and *Coptic Gnostic Chrestomathy* (Peeters 2004).

`LaytonCoptic-Regular.otf` / `LaytonCoptic-Regular.ttf`

## Why it exists

Nothing already installed on this machine is that face. The closest of the 27
Coptic-capable fonts available here is CS Koptos Manuscript Unicode, which scores
**0.816** on glyph-shape agreement with the printed page. A true match would score
about **0.95** (measured by scoring a font against a simulated scan of itself).
This font scores **0.874**.

## How it was made

No font software was copied. The outlines were traced from the printed pages —
the letterforms in a book, not any font file.

1. **Reference alphabet.** The alphabet table on p. 13 of the *Grammar*, segmented
   into 30 individual letters. Its page image is a native 600-ppi bilevel scan, so
   there is no interpolation loss.
2. **Harvest.** 112 pages (chrestomathy, glossary, Coptic index, and a sample of
   body pages) segmented into connected components; lines detected, baselines
   estimated, and each component classified against the reference alphabet.
   **20,202 glyph instances** collected.
3. **Superresolution.** A single printed letter is only ~40 px tall at 600 dpi. For
   each letter, up to 500 instances were aligned subpixel-accurately — scaled by
   each line's own letter height, registered on the baseline and ink centre — and
   averaged, with outliers (merged or broken glyphs) rejected against a first-pass
   average. **7,012 instances** survived into the final templates. The average
   recovers far more detail than any single instance carries.
4. **Refine.** Templates are Gaussian-smoothed (σ = 4 px at letter height 256) to take
   out press noise, then lightened by 16 % of each stroke's own width via the distance
   transform (`src/refine.py`, `lighten`). Because the cut is proportional rather than
   a fixed erosion, thick and thin strokes lose the same fraction and the page's
   contrast is kept — this is the same design at a lighter weight, about 8 % less ink
   than the printed impression, which is roughly the ink gain a press adds. A
   contrast-widening option (`CONTRAST`) exists but ships at 0; v1.1 used it and is
   tagged for reference.
5. **Trace and simplify.** Templates upsampled 2×, thresholded, traced with potrace,
   then simplified in FontForge within a 4-unit error budget (`src/simplify.py`) —
   near-straight runs become true lines, wobble becomes single curves, and extrema get
   on-curve points. 8,378 outline points became 2,238.
6. **Metrics from the page, not invented.** Advance widths are the median of
   **10,975 measured adjacent letter pairs**. Supralinear stroke and hyphen
   dimensions and heights were measured from 834 and 716 instances respectively.

## Coverage

- All 30 letters of the Sahidic alphabet. The type is unicase, so each outline is
  mapped to **both** the Coptic capital and small codepoints (U+2C80–U+2CB1) and,
  for the six Demotic-derived letters ϣ ϥ ϩ ϫ ϭ ϯ, the Greek-block pairs
  (U+03E2–U+03EF).
- **U+0305** combining overline (superlineation), **U+002D** hyphen, **U+0020** space.
- Deliberately absent: ⲋ *sou* (U+2C8A/8B, the numeral six) and ϧ *khei* (U+03E6/E7,
  Bohairic) — neither belongs to the Sahidic alphabet Layton's table sets out.

Font bounding box is (−811, −265) to (1133, 977); the negative xMin is the
zero-width overline, which is drawn to the left of the origin so it lands over the
preceding letter.

## Metrics

| | |
|---|---|
| units per em | 1000 |
| letter height | 620 |
| descender | −265 (ⲣ ⲩ ⲫ ⲯ ϣ ϥ ϩ ϯ) |
| inter-letter gap | 140 units — this face is noticeably letterspaced |
| word space | 620 |
| overline | 94 thick, 790 long, bottom edge 883 above baseline |

## Verification

Scored against the alphabet table, which is **held out**: it is on page 30 of the
PDF, while the harvest drew only on pages 60–540.

| | v1.2 (this font) | v1.0 (as printed) | CS Koptos (best installed) | ceiling |
|---|---|---|---|---|
| shape agreement | **0.859** | 0.874 | 0.816 | ~0.95 |
| with proportion | **0.850** | 0.867 | 0.806 | |
| identity rate | **1.00** | 1.00 | 0.90 | |
| stroke weight vs page | **0.92** | 1.01 | 0.69 | |
| width vs page | **0.97** | 0.97 | 0.95 | |
| ⲟ stem ÷ bar | **2.86** | 2.68 | 1.9 | |

Identity rate = fraction of the 30 glyphs that match their own printed counterpart
better than any other letter. v1.0 (tag `v1.0`) reproduces the page as printed, ink
gain included; v1.2 is that design smoothed and cut 8 % lighter, and the small drop in
agreement is the lighter weight being compared against the heavier printed ink. Both
remain well ahead of any installed font. Smoothing on its own costs nothing: the
smoothed-but-unlightened build scores 0.875.
Set at matched letter height, the word ⲡⲟⲛⲏⲣⲟⲥ measures 0.968× the printed setting
(CS Koptos: 0.91×).

## Known limitations

- **Thin evidence for rare letters.** ⲍ and ⲝ rest on 10 instances each, ⲯ 12, ⲫ 18,
  ϯ 22 — against 400+ for the common letters. Those five outlines are correspondingly
  less refined; they are the first thing to improve by harvesting more pages.
- No kerning and no GPOS mark attachment: U+0305 is a zero-width glyph at a fixed
  offset tuned for a typical advance, so it sits slightly off over the narrowest (ⲓ)
  and widest (ⲱ, ϣ) letters.
- Regular weight only. No italic, no bold, no digits, and no punctuation beyond
  hyphen and space.
- Lightening is proportional, but the local-width estimate is a windowed maximum,
  so a thin bar that joins a thick stem loses slightly more than its share: ⲟ's
  contrast drifts from 2.68 to 2.86. Set `LIGHTEN=0` for the printed weight.

## Rebuilding

Needs `poppler-utils`, `potrace`, `fontforge`, and python with `pillow numpy scipy fonttools`:

```
nix shell nixpkgs#poppler-utils nixpkgs#potrace
nix build --impure --expr 'let pkgs = import (builtins.getFlake "nixpkgs") { system = "x86_64-linux"; };
  in pkgs.python3.withPackages (ps: with ps; [ pillow numpy scipy fonttools ])'
```

Render page scans to `faces/layton/pages/` (untracked), then from the repo root with
`FACE=layton` run `src/` in order: `segref.py` (reference alphabet) → `harvest.py` →
`average.py` → `spacing.py`, `bars.py`, `overline.py` → `build_font.py` →
`fontforge -lang=py -script src/simplify.py faces/layton/LaytonCoptic-Regular.otf 4`
(needs `nixpkgs#fontforge`; regenerates both OTF and TTF). `score4.py` reproduces the
verification numbers. `build_font.py` reads `SIGMA` (smoothing, 4), `LIGHTEN` (0.16)
and `CONTRAST` (0) from the environment; the simplify error budget is that script's
second argument. Per-face constants (names, reference-table geometry, harvest page
globs, fixed pitch) live in `src/face.py`.

`data/` (here, `faces/layton/data/`) holds the intermediate artefacts, so the font can be rebuilt from
`templates.npz` without re-harvesting.

## Installing

```
cp LaytonCoptic-Regular.ttf ~/.local/share/fonts/ && fc-cache -f
```
