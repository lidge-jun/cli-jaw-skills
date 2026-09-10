# Visual Story Reference

How to decide what a figure argues, before deciding how to draw it. The rest of this skill owns
format, geometry, theme and security; this file owns the part that makes a well-formed diagram worth
looking at.

A figure that satisfies every budget in `SKILL.md` can still be six nouns in six boxes. The difference
is whether a reader learns something they could act on.

## Before you draw (DIAGRAM-CLAIM-01)

Answer three questions. If you cannot, the diagram is not ready.

1. **Who is reading, and what are they deciding?** "A developer choosing between two caching layers"
   is a reader. "Someone interested in caching" is not.
2. **What is the one claim?** Write it as a sentence a reasonable person could disagree with. "The
   retry path is the only place that writes to the queue twice" is a claim. "System overview" is a
   label.
3. **What does the reader do differently if the claim is true?** If nothing, the figure is decoration.

Write the claim down first. It becomes the caption, the `<title>`, and the sentence next to the fence.

When there is no claim, say so in prose and stop. A one-line answer beats a diagram of the same line.

## Draw only when the shape carries the meaning (DIAGRAM-SCOPE-01)

A picture earns its place when the *relation* is the point: something contains, precedes, causes,
branches from, or is proportionally larger than something else. Reach for prose or a table instead
when the content is a definition, a single fact, a linear list of unrelated items, or values a reader
will want to compare precisely.

The proactive triggers in `SKILL.md` count things. A count is a reason to consider a figure, never a
reason to draw one. Four items with no relation between them are a list.

## Say where the numbers came from (DIAGRAM-EVIDENCE-01)

Every quantity belongs to one of four classes, and the figure or its caption says which:

| Class | Meaning | How it appears |
|---|---|---|
| Observed | Measured or read from a real source | value + unit + source + date |
| User-supplied | The user stated it in this conversation | value + unit, attributed to the user |
| Assumed | You chose it to make the model work | value + unit + the assumption, stated |
| Illustrative | Shape matters, magnitude does not | labelled illustrative, with no fake precision |

Never invent plausible-looking data. A chart of quarterly revenue you made up is not a placeholder, it
is a false claim that renders beautifully. If you need a shape to show a pattern, label it
illustrative and round the numbers so no one mistakes them for measurements.

State units on the axis, not only in the caption. If an axis does not start at zero, say so, because
the reader's eye reads the bar heights as the ratio.

## One takeaway per figure (DIAGRAM-SEQ-01)

A figure carries one idea. When the subject has more, sequence them:

- **Overview first.** The whole system at the level where the claim is visible, and no deeper.
- **Then a named detail.** "The retry path, in detail" — a second figure scoped to one region of the
  first, with prose between them saying why you are zooming in.

The failure mode is shrinking everything into one 680px frame until each label is four characters and
nothing is legible. The node budget in `SKILL.md` is the symptom; this is the rule behind it. Two
honest figures beat one crowded one, and a figure you decided not to draw costs the reader nothing.

## Hand off to prose (DIAGRAM-HANDOFF-01)

The figure shows the structure; the sentence next to it states what to conclude. Neither repeats the
other.

- **Caption or preceding sentence**: the claim, in words. Not "the diagram below shows the
  architecture" — that tells the reader nothing they cannot see.
- **The accessible name**: `<title>` and `<desc>` for SVG, `aria-label` for a canvas or widget, carry
  the same takeaway. A screen-reader user gets the claim, not the word "Diagram".
- **After the figure**: the implication, or the next question. This is where the detail that did not
  fit in a five-word subtitle goes.

Explanatory prose stays outside the figure. Labels inside stay short.

## Compositions to avoid (DIAGRAM-SLOP-01)

These render cleanly and pass every budget, which is exactly why they survive review.

| Pattern | Why it fails | Instead |
|---|---|---|
| A grid of same-sized cards for things that are not a list | Equal boxes assert equal weight and no relation, so the layout says nothing | Show the actual relation: nesting, sequence, or a comparison with an axis |
| Cycling colour through categories like a palette swatch | Colour stops meaning anything, so the reader learns to ignore it | Group by category; see `color-palette.md` |
| Boxes and arrows with no claim | A generic pipeline diagram of any system looks the same | Draw the part where the claim lives, or write the sentence instead |
| Numbered step chips, badges, oversized headings | Decoration competing with content | Sentence-case labels; the forbidden list in `SKILL.md` already bans the ornaments |
| A domain card or decorative illustration nobody asked for | Answers a question the user did not ask | Use `module-domain-cards.md` and `module-art.md` when that surface is requested |
| Restating the surrounding paragraph as a figure | The reader reads the same thing twice | Cut one of them |

## Look at what you produced (DIAGRAM-RENDER-01, DIAGRAM-FRESH-01)

Valid syntax is not a rendered result. Before delivering, check the figure the way a reader receives
it: text inside its box, nothing clipped at the frame, no overlapping labels, no empty series, and for
Korean or other CJK text no tofu boxes and no metric shift from a font fallback. `korean-text.md` owns
the CJK specifics and `SKILL.md` owns the OfficeCLI raster directive.

Then the fresh-reader check, which you run on yourself because you are the only reader available at
authoring time. Cover everything except the figure and its caption. From those two alone, write down
the one sentence a reader would carry away. Compare it with the claim you wrote before drawing. If
what you just wrote is a description of the picture ("a flow from client to queue") rather than a
claim ("retries are the only path that writes twice"), the caption is a label: rewrite it and the
`<title>` before delivering. If the two sentences disagree, the figure is drawing something other
than the point you meant to make.
