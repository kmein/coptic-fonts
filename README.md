# coptic-font

Digital revivals of Coptic types from printed books, traced from averaged 600 dpi page
scans rather than from any font file. One pipeline in `src/`, one directory per face.

| face | source | status |
|---|---|---|
| [`faces/layton/`](faces/layton/README.md) — **Layton Coptic** | Bentley Layton, *A Coptic Grammar* (Harrassowitz 2000) | v1.2 |
| [`faces/lambdin/`](faces/lambdin/README.md) — **Lambdin Coptic** | Thomas Lambdin, *Introduction to Sahidic Coptic* (Mercer 1983) | v1.0 |

Each face directory holds the font files, a specimen (`specimen.typ` / `.pdf`), a README
with provenance, metrics and verification, and `data/` with the reference alphabet and
the averaged templates the font rebuilds from. Page scans go in `faces/<face>/pages/`
and are not tracked.

## Pipeline

`FACE=<face>` selects the face; `src/face.py` carries its constants. Run from the repo
root, in order: `segref.py` (reference alphabet from the book's own table) →
`harvest.py` (segment and classify every glyph on the scanned pages) → `average.py`
(subpixel-align and average each letter's instances) → `spacing.py`, `bars.py`,
`overline.py` (metrics measured from the printed setting) → `build_font.py` (refine,
trace, assemble OTF + TTF) → `fontforge -lang=py -script src/simplify.py <otf> 4`.
`score4.py` scores a font against the reference alphabet.

## Tooling

`poppler-utils`, `potrace`, `fontforge`, `typst`, and python with
`pillow numpy scipy fonttools`:

```
nix build --impure --expr 'let pkgs = import (builtins.getFlake "nixpkgs") { system = "x86_64-linux"; };
  in pkgs.python3.withPackages (ps: with ps; [ pillow numpy scipy fonttools ])'
```
