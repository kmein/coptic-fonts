#set page(paper: "a4", margin: (x: 2.2cm, y: 2cm))
#set text(size: 10pt)
#set par(justify: false)

#let cop(sz, body) = text(font: "Lambdin Coptic", size: sz)[#body]
#let ALPHA = "ⲁⲃⲅⲇⲉⲍⲏⲑⲓⲕⲗⲙⲛⲝⲟⲡⲣⲥⲧⲩⲫⲭⲯⲱϣϥϩϫϭϯ"

#align(center)[
  #text(size: 22pt)[Lambdin Coptic]
  #v(-6pt)
  #text(size: 9.5pt, style: "italic")[
    a revival of the typewriter Coptic in Thomas O. Lambdin's #smallcaps[Introduction to Sahidic Coptic] \
    traced from averaged 600 dpi page scans · v1.0, smoothed; 6 % lighter than the typed impression
  ]
]

#v(10pt)
#line(length: 100%, stroke: 0.4pt)
#v(6pt)

#align(center)[
  #cop(26pt, "ⲁⲃⲅⲇⲉⲍⲏⲑⲓⲕⲗⲙⲛⲝⲟ") \
  #v(2pt)
  #cop(26pt, "ⲡⲣⲥⲧⲩⲫⲭⲯⲱϣϥϩϫϭϯ")
]

#v(4pt)
#align(center)[
  #text(size: 8pt, fill: luma(90))[
    alpha vida gamma dalda eie zata hate thethe iauda kapa laula mi ni ksi o pi ro
    sima tau ua fi khi psi oou shai fai hori gangia shima dei
  ]
]

#v(8pt)
#line(length: 100%, stroke: 0.4pt)
#v(8pt)

== Sizes

#grid(columns: (auto, 1fr), gutter: 10pt, align: (right + horizon, left + horizon),
  text(size: 7pt, fill: luma(90))[8], cop(8pt, ALPHA),
  text(size: 7pt, fill: luma(90))[9], cop(9pt, ALPHA),
  text(size: 7pt, fill: luma(90))[10], cop(10pt, ALPHA),
  text(size: 7pt, fill: luma(90))[12], cop(12pt, ALPHA),
  text(size: 7pt, fill: luma(90))[14], cop(14pt, ALPHA),
  text(size: 7pt, fill: luma(90))[18], cop(18pt, ALPHA),
)

#v(10pt)

== Superlineation and morph division

The supralinear stroke is #raw("U+0305") (combining overline); the morph-dividing
hyphen is the ordinary #raw("U+002D").

#v(4pt)
#cop(14pt, "ⲁϥ-ϣⲁϫⲉ ⲛ̅ⲙⲙⲁ-ⲩ ϫⲉ-ⲙ̅ⲡⲣ̅-ⲣ̅-ϩⲟⲧⲉ")

#v(4pt)
#cop(14pt, "ⲁⲩⲱ ⲛ̅ⲧⲉⲣⲉ-ⲡⲥⲁⲃⲃⲁⲧⲟⲛ ⲟⲩⲉⲓⲛⲉ ⲙⲁⲣⲓⲁ ⲧⲙⲁⲅⲇⲁⲗⲏⲛⲏ")

#v(4pt)
#cop(11pt, "ⲡⲣⲱⲙⲉ ⲡⲟⲛⲏⲣⲟⲥ ⲙⲁⲣⲓⲁ ⲟⲩⲛ̅ⲧⲉ- ⲛⲁⲛⲟⲩ-ϥ ⲉⲧⲃⲉ-ⲡⲉⲓ-ϩⲱⲃ ϣⲟⲙⲛ̅ⲧ")

#v(10pt)
#line(length: 100%, stroke: 0.4pt)
#v(6pt)

== Fidelity

The same word, typed and revived. Above: #cop(9pt, "ⲡⲣⲱⲙⲉ") as it appears in the
book (600 dpi scan). Below: the same word set in this font at matching letter height.

#v(6pt)
#box(image("data/scan_word.png", width: 6.2cm))

#v(2pt)
#cop(46.7pt, "ⲡⲣⲱⲙⲉ")

#v(6pt)

Measured against the alphabet table on p. x of the book — held out from the harvest,
which used the reading selections, the verbal-conjugation table and lesson exercises:

#v(4pt)
#table(columns: 4, stroke: none, align: (left, right, right, right),
  inset: (x: 8pt, y: 3pt),
  table.hline(stroke: 0.4pt),
  [], [*this font*], [*best installed*], [*ceiling*],
  table.hline(stroke: 0.4pt),
  [glyph-shape agreement], [0.882], [0.709], [\~0.95],
  [with proportion], [0.878], [0.660], [],
  [identity rate], [1.00], [0.83], [],
  [stroke weight vs page], [0.94], [—], [],
  [set width vs page], [1.00], [—], [],
  table.hline(stroke: 0.4pt),
)

#v(3pt)
#text(size: 8.5pt)[
  Best installed = Antinoou, the closest of the 27 Coptic-capable fonts on this
  machine to Lambdin's page (CS Koptos 0.704; Layton Coptic 0.693 — a different design).
  Ceiling = what a true match scores against a scan of this quality. Identity rate =
  share of the 30 glyphs closer to their own typed counterpart than to any other letter.
  Smoothing alone strips the ribbon spread, leaving 6 % less ink than the impression.
]

#v(10pt)
#line(length: 100%, stroke: 0.4pt)
#v(6pt)

#text(size: 8.5pt)[
  *Built from* 47,520 harvested glyph instances across 125 pages; 8,762 survived
  outlier rejection into the averaged templates. Advance widths are medians over
  28,667 measured letter pairs — they vary by letter, so this is not fixed pitch. #h(1fr) 1000 upem · letter height 620 · descender −265
]
