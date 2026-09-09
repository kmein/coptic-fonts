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
4. **Refine (v1.1).** Templates are Gaussian-smoothed (σ = 4 px at letter height 256)
   and the stroke contrast is widened: the shape is grown along x and shrunk along y by
   7 px, which thickens vertical stems and thins horizontal bars while leaving
   diagonals alone, then the ink box is restored so proportions do not drift
   (`src/refine.py`). Layton's printed type has a thick/thin ratio of about 1.45; the
   font now sits roughly halfway between that and IFAO N Copte.
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

| | v1.1 (this font) | v1.0 (faithful) | CS Koptos (best installed) | ceiling |
|---|---|---|---|---|
| shape agreement | **0.853** | 0.874 | 0.816 | ~0.95 |
| with proportion | **0.844** | 0.867 | 0.806 | |
| identity rate | **1.00** | 1.00 | 0.90 | |
| stroke weight vs page | **1.08** | 1.01 | 0.69 | |
| width vs page | **0.97** | 0.97 | 0.95 | |

Identity rate = fraction of the 30 glyphs that match their own printed counterpart
better than any other letter. v1.0 (git `b56f7ad`) reproduces the page as printed;
v1.1 deliberately departs from it in stroke contrast and smoothness, which is why its
agreement score is a little lower. Both remain well ahead of any installed font.

Stroke contrast, measured as stem width ÷ bar thickness at the mid cross-section
(letter height 256): ⲟ 2.7 → 4.3, ⲡ 2.2 → 4.3, ⲏ 7.2 → 11.9; mean over ⲟ ⲉ ⲡ ⲏ
4.4 → 6.9 (IFAO N Copte: 10.2). The x-growth adds slightly more ink than the y-shrink
removes, so v1.1 prints about 7 % heavier than the page.
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
- The contrast increase is a design choice, not a property of Layton's type. The
  faithful version is tagged in git as v1.0; rebuild with `CONTRAST = 0` in
  `src/build_font.py` to get it back.

## Rebuilding

Needs `poppler-utils`, `potrace`, `fontforge`, and python with `pillow numpy scipy fonttools`:

```
nix shell nixpkgs#poppler-utils nixpkgs#potrace
nix build --impure --expr 'let pkgs = import (builtins.getFlake "nixpkgs") { system = "x86_64-linux"; };
  in pkgs.python3.withPackages (ps: with ps; [ pillow numpy scipy fonttools ])'
```

Render page scans to `pages/`, then run `src/` in order: `segref.py` (reference
alphabet) → `harvest.py` → `average.py` → `spacing.py`, `bars.py`, `overline.py` →
`build_font.py` → `fontforge -lang=py -script src/simplify.py LaytonCoptic-Regular.otf 4`
(needs `nixpkgs#fontforge`; regenerates both OTF and TTF). `score4.py` reproduces the
verification numbers. Smoothing and contrast are the `SIGMA` / `CONTRAST` constants at
the top of `build_font.py`; the simplify error budget is the script's second argument.

`data/` holds the intermediate artefacts, so the font can be rebuilt from
`templates.npz` without re-harvesting.

## Installing

```
cp LaytonCoptic-Regular.ttf ~/.local/share/fonts/ && fc-cache -f
```
