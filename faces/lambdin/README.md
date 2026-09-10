# Lambdin Coptic

A digital revival of the typewriter Coptic in Thomas O. Lambdin's *Introduction to
Sahidic Coptic* (Mercer University Press 1983).

`LambdinCoptic-Regular.otf` / `LambdinCoptic-Regular.ttf` — v1.0

## What it is

Lambdin's book is typescript: a monospaced typewriter Latin with the Coptic typed from
a Coptic typewriter element — monoline strokes, ribbon-fuzzed edges, and letters that
sit small, at roughly the Latin x-height. This face reproduces that element. It is a
different design from Layton's bookface: scored against Lambdin's page, Layton Coptic
reaches only 0.693.

Nothing installed on this machine comes close either. The best of the 27 Coptic-capable
fonts here (Antinoou) scores **0.709** on glyph-shape agreement with Lambdin's page; a
true match would score about **0.95**. This font scores **0.882**.

## How it was made

Same pipeline as [Layton Coptic](../layton/README.md); no font software was copied.

1. **Reference alphabet.** "The Coptic Alphabet" on p. x (PDF p. 10): five columns of
   six letters, segmented column-major into 30 reference glyphs. Native 600-ppi bilevel
   scan.
2. **Harvest.** Because Coptic and Latin share lines everywhere in the lessons
   (`ⲣⲱⲙⲉ man`), and typewriter `o c x p` are near-identical to ⲟ ⲥ ⲭ ⲣ, the harvest
   drew only on the pure-Coptic parts: the Reading Selections (Luke I–V, Apophthegmata,
   Wisdom of Solomon, Joseph the Carpenter), the Table of Principal Verbal Conjugations,
   and the exercise lines of the lessons, with the line-purity gate kept as the defence
   against Latin contamination. **47,520 glyph instances** from 125 pages.
3. **Superresolution.** Up to 500 instances per letter, subpixel-aligned on baseline and
   ink centre and averaged; **8,762** survived outlier rejection. Rarest: ⲝ 18, ⲯ 25,
   ⲍ 34, ⲫ 61, ϯ 65 — all better placed than Layton's rare letters were.
4. **Refine, trace, simplify.** Gaussian smoothing (σ 4) at letter height 256, then
   potrace and a FontForge simplify pass at a 4-unit budget. **No lightening step**:
   smoothing alone strips the ribbon spread and leaves the strokes at 0.94 of the typed
   impression, which already matches the 8 %-lighter outcome chosen for Layton v1.2.
   (`lighten=0` is the per-face default in `src/face.py`.)
5. **Metrics from the page.** Advance widths are medians over **28,667 measured letter
   pairs**; overline and hyphen from 273 and 11 typed instances.

## A finding that overturned the plan

The plan assumed a fixed-pitch typewriter and built fixed-pitch support into the
pipeline. The measurement says otherwise: per-letter advances run continuously from
ⲓ 221 to ⲇ 387 (letter height 256), ⲟ alone spreads
over an interquartile range of 317–341, and no unit grid fits (best unit 22.5, residual
0.18 — no better than chance). Whatever machine set this Coptic, it did not space it
on one pitch. The font therefore uses the measured per-letter advances, and the
fixed-pitch code path stays available but off.

## Coverage

All 30 Sahidic letters on both capital and small codepoints (U+2C80–U+2CB1 and the
Greek-block pairs for ϣ ϥ ϩ ϫ ϭ ϯ), U+0305 combining overline, hyphen, space. ⲋ and ϧ
absent, as in Layton Coptic.

## Metrics

| | |
|---|---|
| units per em | 1000 |
| letter height | 618 (ⲟ) |
| descender | -234 (ⲣ); ⲫ and ϯ reach -285 |
| inter-letter gap | 184 units |
| word space | 855 units |
| overline | 143 thick, 713 long, bottom edge 682 above baseline |
| ⲟ stem ÷ bar | 1.79 (a near-monoline face; Layton's is 2.68) |

Lambdin's Coptic is set smaller than its Latin in the book. This font puts the letters
at the usual 620/1000 em, so at equal point size it will look larger next to Latin than
the book does; set it a size or two smaller to reproduce the page.

## Verification

Against the alphabet table on p. x, which the harvest never touched:

| | this font | Antinoou (best installed) | CS Koptos | Layton Coptic | ceiling |
|---|---|---|---|---|---|
| shape agreement | **0.882** | 0.709 | 0.704 | 0.693 | ~0.95 |
| with proportion | **0.878** | 0.660 | 0.648 | 0.619 | |
| identity rate | **1.00** | 0.83 | 0.93 | 0.87 | |
| stroke weight vs page | **0.94** | | | | |
| width vs page | **1.00** | | | | |

Every letter scores above 0.79 (weakest ⲥ 0.79, ⲍ 0.80, ⲟ 0.80); median 0.873. The word
ⲡⲣⲱⲙⲉ set at matching letter height comes out within 1 % of the typed width.

## Known limitations

- The overline is a heavy typed overstrike (143 units) placed at a fixed offset; it
  sits slightly off over ⲓ and the widest letters. No kerning, no mark attachment.
- Only 11 hyphens were found in the harvested pages, so the hyphen's dimensions rest on
  thin evidence.
- Regular weight only; no digits or punctuation beyond hyphen and space.

## Rebuilding

From the repo root with `FACE=lambdin`, exactly as for Layton (see the root README).
Page renders go to `faces/lambdin/pages/` (untracked): PDF pp. 155–225 as `r-`,
383–388 as `v-`, every third page of 15–158 as `l-`. The reference page is PDF p. 10.
