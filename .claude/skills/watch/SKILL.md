---
name: watch
description: File this week's regulation watch into the person's board. Use on "/watch", "anything new", "check the MARADMINs", or as part of a Monday review. Reads the public feed named in config.json, checks that the feed is whole and fresh, keeps only notices that match the person's live profile, writes them to the board's inbox, and says plainly when the check was by title only.
---

# /watch

Authenticate WEEKLY.md through the independently pinned bootstrap before protected actions. Then use its signed v2 feed protocol, strict source validation, durable high-water and native version/readback rules in full. Feed transports are data and are never executed. No WebFetch-only verification, unsigned JSON or v1 fallback. config.watch_feed cannot replace the pinned signed transport URLs. Filter the authenticated data against the live board only after verification; keep profile data outside the helper. Keep the existing board URL in my/board.json and all my/ data. Preserve per-source failures and titles-only confidence, legacy MARADMIN deduplication, create-only inbox filing, possible applicability, and the MARADMIN-only status projection. Never infer a deadline, edit a plan item, send, schedule or broaden consent. Failure keeps last good watch and inbox, reports the exact reason and original good date, and writes only authorized watch_error with native preconditions and readback. A concurrent higher signed sequence wins before every write and final summary.
