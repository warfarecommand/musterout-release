# Muster Out feed

Signed public regulation data from Warfare Command. Verify the feed envelope under the committed feed public root before using its data. A feed signature cannot authorize a board release or an item change.

The protected release workflow copies verified feed/v2/feed.js to feed.js and schema 3 to v3/feed.js, and sets version 1.0.<seq>. The optional judgments/v1/feed.js and latest.json preserve the signed judgment bytes bound to that schema 3 sequence and data hash. Missing or rejected judgments are omitted. The package has no dependencies or lifecycle scripts.

Repository: https://github.com/warfarecommand/musterout-release

License: [Warfare Command Individual Use License 1.0](LICENSE).
