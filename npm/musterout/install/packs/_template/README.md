# Pack template

A pack is everything the board needs for one service. Copy this folder to `packs/<service>/` and fill it.

- `regs/` the governing texts as plain text, one file per document, with the public URL in the first line.
- `citations.json` every `ref` and `para` the seed uses, mapped to the file and the line range where the quote appears. The build checks each quote against the text.
- `glossary.md` the acronyms a member of that service uses, one line each.
- `faq-<path>.md` one file per path with the ten questions people ask first and the cited answers.
- `REVIEW.md` who reviewed the pack, when, and what they checked. A pack is not shipped without it.
