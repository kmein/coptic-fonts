#set page(paper: "a4", margin: (x: 2.2cm, y: 2cm))
#set text(size: 10pt)
#set par(justify: false)

#let cop(sz, body) = text(font: "Layton Coptic", size: sz)[#body]
#let ALPHA = "ⲁⲃⲅⲇⲉⲍⲏⲑⲓⲕⲗⲙⲛⲝⲟⲡⲣⲥⲧⲩⲫⲭⲯⲱϣϥϩϫϭϯ"

#align(center)[
  #text(size: 22pt)[Layton Coptic]
  #v(-6pt)
  #text(size: 9.5pt, style: "italic")[
    a revival of the Coptic type of Bentley Layton's #smallcaps[A Coptic Grammar] \
    traced from registered and averaged page scans · v1.3, smoothed and cut 8 % lighter than the page
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

The supralinear stroke is #raw("U+0305") (combining overline); Layton's morph-dividing
hyphen is the ordinary #raw("U+002D"), and his prepersonal-state sign ⸗ is
#raw("U+2E17") (double oblique hyphen): ⲥⲱⲧⲡ-, ⲥⲟⲧⲡ⸗.

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

The same word, printed and revived. Above: #cop(9pt, "ⲡⲟⲛⲏⲣⲟⲥ") as it appears in the
book (600 dpi scan). Below: the same word set in this font at matching letter height.

#v(6pt)
#box(image("data/scan_word.png", width: 6.2cm))

#v(2pt)
#cop(27.9pt, "ⲡⲟⲛⲏⲣⲟⲥ")

#v(6pt)

Measured against the alphabet table on p. 13 of the #emph[Grammar] — held out from the
harvest, which used only pp. 60–540:

#v(4pt)
#table(columns: 4, stroke: none, align: (left, right, right, right),
  inset: (x: 8pt, y: 3pt),
  table.hline(stroke: 0.4pt),
  [], [*this font*], [*best installed*], [*ceiling*],
  table.hline(stroke: 0.4pt),
  [glyph-shape agreement], [0.877], [0.816], [\~0.95],
  [with proportion], [0.868], [0.806], [],
  [identity rate], [1.00], [0.90], [],
  [stroke weight vs page], [0.93], [0.69], [],
  [set width vs page], [0.98], [0.95], [],
  table.hline(stroke: 0.4pt),
)

#v(3pt)
#text(size: 8.5pt)[
  Best installed = CS Koptos Manuscript Unicode, the closest of the 27 Coptic-capable
  fonts on this machine. Ceiling = what a true match scores against a scan of this
  quality. Identity rate = share of the 30 glyphs closer to their own printed
  counterpart than to any other letter. Weight 0.93 = 7 % less ink than the printed
  impression, with the page's own thick/thin ratio kept; v1.2 scored 0.859 and v1.0
  (as printed) 0.874, both tagged in git.
]

#v(10pt)
#line(length: 100%, stroke: 0.4pt)
#v(6pt)

#text(size: 8.5pt)[
  *Built from* 83,569 glyph instances harvested from 481 pages of the #emph[Grammar]
  and three spreads of #emph[Zostrien] (BCNH 24); 14,159 were registered and averaged
  into the templates. Advance widths are medians over 45,744 measured letter pairs. #h(1fr) 1000 upem · letter height 620 · descender −265
]
