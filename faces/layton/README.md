# Layton Coptic

A digital revival of the Coptic type used in Bentley Layton's *A Coptic Grammar*
(Harrassowitz 2000) and *Coptic Gnostic Chrestomathy* (Peeters 2004), and in the
Bibliothèque copte de Nag Hammadi (e.g. *Zostrien*, BCNH 24, Peeters 2000).

`LaytonCoptic-Regular.otf` / `LaytonCoptic-Regular.ttf`

## Why it exists

Nothing already installed on this machine is that face. The closest of the 27
Coptic-capable fonts available here is CS Koptos Manuscript Unicode, which scores
**0.816** on glyph-shape agreement with the printed page. A true match would score
about **0.95** (measured by scoring a font against a simulated scan of itself).
This font scores **0.877**.

## How it was made

No font software was copied. The outlines were traced from the printed pages —
the letterforms in books, not any font file.

1. **Reference alphabet.** The alphabet table on p. 13 of the *Grammar*, segmented
   into 30 individual letters. Its page image is a native 600-ppi bilevel scan, so
   there is no interpolation loss.
2. **Harvest.** Every page of the *Grammar* from p. 60 to the end (481 pages, 600 dpi
   bilevel) and the three spreads of Coptic text in the *Zostrien* excerpt (300 dpi
   greyscale, rendered at 600 dpi and thresholded by Otsu's method so its light ink is
   not eroded) were segmented into connected components. Lines are grouped by their
   running median centre, the baseline and letter height of each line come from the
   confidently classified baseline-sitting letters, and every component is classified
   against the reference alphabet and then checked against the expected height and
   descent of the letter it was read as, which throws out merged overlines, broken
   glyphs and look-alikes such as the editorial line-division bar read as ⲓ.
   **83,569 glyph instances** collected (81,947 *Grammar*, 1,622 *Zostrien*).
3. **Superresolution.** A printed letter is ~40 px tall at 600 dpi in the *Grammar*
   and ~22 px in *Zostrien*. For each letter, up to 500 instances per source were
   rendered into a common canvas at their line's letter height, registered to the
   running average by cross-correlation (to a quarter of a scanned pixel), weighted
   by the square of their scanned letter height, and averaged; outliers were rejected
   against the registered average. **14,159 instances** survived into the final
   templates (12,552 + 1,607). Registration is what makes the difference to v1.2,
   which aligned instances only by ink centre and line baseline: the averages are
   sharper, the outlier test keeps 98 % of instances instead of 72 %, and
   the rare letters now rest on 33–160 instances instead of 10–22.
4. **Refine.** Templates are Gaussian-smoothed (σ = 4 px at letter height 256) to take
   out press noise, then lightened by 16 % of each stroke's own width via the distance
   transform (`src/refine.py`, `lighten`). Because the cut is proportional rather than
   a fixed erosion, thick and thin strokes lose the same fraction and the page's
   contrast is kept — this is the same design at a lighter weight, about 7 % less ink
   than the printed impression, which is roughly the ink gain a press adds. A
   contrast-widening option (`CONTRAST`) exists but ships at 0; v1.1 used it and is
   tagged for reference.
5. **Trace and simplify.** Templates upsampled 2×, thresholded, traced with potrace,
   then simplified in FontForge within a 4-unit error budget (`src/simplify.py`) —
   near-straight runs become true lines, wobble becomes single curves, and extrema get
   on-curve points. 2,390 outline points in all.
6. **Metrics from the page, not invented.** Advance widths are the median of
   **45,744 measured adjacent letter pairs** in the *Grammar*. Supralinear stroke and
   hyphen dimensions and heights were measured from 15,253 and 13,420 instances
   respectively, over every harvested page. The *Zostrien* setting agrees: its
   inter-letter gap is 59.5 units against the *Grammar*'s 57.8, and its per-letter
   advances are 0.98 of the *Grammar*'s at the median, so the spacing is the face's
   own and not tracking added by one typesetter.

### Sources that are not this face

The Brill *Nag Hammadi Studies* editions (the *Treatise on the Resurrection* in NHS 22
and the *Exegesis on the Soul* in NHS 21, both reprinted in *The Coptic Gnostic Library*)
look like the same type but are a heavier cut: thicker ⲛ diagonal, wider ϣ, ⲡ without
the flared serifs. Templates averaged from them score 0.86 and 0.82 against the
*Grammar*'s table where the *Zostrien* templates score 0.87, and mixing them in pulls
the shapes away from the page. They were harvested (7,938 instances) and excluded.

## Coverage

- All 30 letters of the Sahidic alphabet. The type is unicase, so each outline is
  mapped to **both** the Coptic capital and small codepoints (U+2C80–U+2CB1) and,
  for the six Demotic-derived letters ϣ ϥ ϩ ϫ ϭ ϯ, the Greek-block pairs
  (U+03E2–U+03EF).
- **U+0305** combining overline (superlineation), **U+002D** hyphen, **U+2E17** double
  oblique hyphen ⸗ (Layton's prepersonal-state sign, as in ⲥⲟⲧⲡ⸗; traced like a letter from
  454 registered instances), **U+0020** space.
- Deliberately absent: ⲋ *sou* (U+2C8A/8B, the numeral six) and ϧ *khei* (U+03E6/E7,
  Bohairic) — neither belongs to the Sahidic alphabet Layton's table sets out.

Font bounding box is (−750, −271) to (1145, 915); the negative xMin is the
zero-width overline, which is drawn to the left of the origin so it lands over the
preceding letter.

## Metrics

| | |
|---|---|
| units per em | 1000 |
| letter height | 620 |
| descender | −271 (ⲣ ⲩ ⲫ ⲯ ϣ ϥ ϩ ϯ) |
| inter-letter gap | 140 units — this face is noticeably letterspaced, in both books |
| word space | 620 |
| overline | 117 thick, 670 long, bottom edge 789 above baseline |

The overline sits lower than in v1.2 (883): that figure came from eight chrestomathy
pages, where the bars are set higher than in the running text; measured over every
page, the bottom edge is 1.27 letter heights above the baseline.

## Verification

Scored against the alphabet table, which is **held out**: it is on page 30 of the
PDF, while the harvest drew only on pages 60–540, and *Zostrien* is another book.

| | v1.3 (this font) | v1.2 | v1.0 (as printed) | CS Koptos (best installed) | ceiling |
|---|---|---|---|---|---|
| shape agreement | **0.877** | 0.859 | 0.874 | 0.816 | ~0.95 |
| with proportion | **0.868** | 0.850 | 0.867 | 0.806 | |
| identity rate | **1.00** | 1.00 | 1.00 | 0.90 | |
| stroke weight vs page | **0.93** | 0.91 | 1.01 | 0.69 | |
| width vs page | **0.98** | 0.97 | 0.97 | 0.95 | |

Identity rate = fraction of the 30 glyphs that match their own printed counterpart
better than any other letter. v1.0 (tag `v1.0`) reproduces the page as printed, ink
gain included; v1.3 is cut 7 % lighter and still agrees with the page better than the
as-printed build did, which is the registration paying off. ⲟ's thick/thin ratio is
unchanged from v1.2 (1.30 against 1.33 by the same measurement).

## Known limitations

- **Rarest letters.** ⲯ rests on 33 instances, ⲝ on 60, ⲍ on 61, ⲫ on 93 — against
  500+ for the common letters. They are much better supported than in v1.2 (10–22)
  but still the least refined outlines.
- No kerning and no GPOS mark attachment: U+0305 is a zero-width glyph at a fixed
  offset tuned for a typical advance, so it sits slightly off over the narrowest (ⲓ)
  and widest (ⲱ, ϣ) letters.
- Regular weight only. No italic, no bold, no digits, and no punctuation beyond
  hyphen and space.
- Lightening is proportional, but the local-width estimate is a windowed maximum,
  so a thin bar that joins a thick stem loses slightly more than its share. Set
  `LIGHTEN=0` for the printed weight.

## Rebuilding

Needs `poppler-utils`, `potrace`, `fontforge`, and python with `pillow numpy scipy fonttools`
(`nix develop` at the repo root provides all of them).

Render page scans into `faces/layton/pages/<source>/` (untracked): `grammar/p-NNN.png`
from the *Grammar* PDF at 600 dpi (`pdftoppm -r 600 -mono -png -f 60 -l 540`) and
`zost/z-*.png` from the *Zostrien* PDF at 600 dpi, split into left and right pages.
The subdirectory name is recorded as each instance's source; `source_scale` in
`src/face.py` says how many real scanned pixels a rendered pixel is (0.5 for the
300 dpi *Zostrien*), so the averaging can weight by true resolution. Then from the repo
root with `FACE=layton` run `src/` in order: `segref.py` (reference alphabet) →
`harvest.py` → `average.py` → `spacing.py`, `bars.py`, `overline.py` → `build_font.py` →
`fontforge -lang=py -script src/simplify.py faces/layton/LaytonCoptic-Regular.otf 4`
(regenerates both OTF and TTF). `score4.py` reproduces the verification numbers.
`build_font.py` reads `SIGMA` (smoothing, 4), `LIGHTEN` (0.16) and `CONTRAST` (0) from
the environment; the simplify error budget is that script's second argument. Per-face
constants (names, reference-table geometry, expected letter geometry, metric page globs,
source scales) live in `src/face.py`.

`data/` (here, `faces/layton/data/`) holds the intermediate artefacts, so the font can be rebuilt from
`templates.npz` without re-harvesting.

## Installing

```
cp LaytonCoptic-Regular.ttf ~/.local/share/fonts/ && fc-cache -f
```
