# Privacy

Anthropic hosts your board inside your own Claude account. The maintainers of this project have no account on it, and this build sends them nothing from it. Two optional submissions can reach the project's database: the setup count and the lesson result. Each one goes only if you say yes.

## Where your data is
| Place | What is there | Who controls it |
| --- | --- | --- |
| Your board's database on claude.ai | Your profile, items, dates, notes, leave, conditions, contacts, notices | You, and anyone you share the page with. Anthropic hosts it under its consumer terms. |
| The Ask box | When you press Ask, the page sends your board (items, notes, dates, condition list, regulation excerpts) to Claude on your account for that one answer | Your account |
| Your Claude conversations and Claude Code transcripts | Whatever you and the assistant said, including anything you pasted | You, through your Claude account settings, under Anthropic's retention rules |
| This folder on your laptop | `my/board.json` holds the board pointer. `my/receipt.json` holds your count choice and its random install id. `my/pending.json` adds the setup stage to the pointer. During an update, `my/update.json` keeps installation progress and record counts with public release details. These files hold no personal facts. | You |
| Your browser | Tab and filter preferences. The plan itself only if you used the board as a local file before publishing. | You |

The board page itself is a generic template. A copy of the page carries none of your data.

Anthropic's privacy and training settings change, so this page does not restate them. Read them in your Claude account settings before you put medical detail on the board.

## Release checks and updates
Once per Claude session, the assistant makes a GET of `https://musterout.warfarecommand.com/release.json`, a public static file. It sends no identifiers, board data, or installed version. The host receives the normal internet address and request headers. The board page makes no release request. If you confirm an update, Claude downloads the public zip from the same site, checks its SHA-256, keeps your `my/` folder, and replaces the page at your existing board address. An unfinished update keeps a marker so the next run can resume.

## What this project collects
Apart from the welcome page's counter, the project receives nothing unless you say yes to one of these two.
- **The count.** At setup, Claude asks once. On yes it sends exactly five fields: `service`, `path` (resign, retire, eas), `grade` (the grade group), `version` (the product version), and `id`, a random install id so a repeated setup is not counted twice. The install id is kept in `my/receipt.json` in your folder and does not link to your name or account. Your choice is saved in that file before anything is sent, so a retry or a reset reuses the same id and you are not asked again. The endpoint also records the time it received the count and a salted hash of the internet address it came from, used for rate limiting. It keeps no name, date, unit, or board data. Say skip and nothing is sent.
- **The lesson result.** The lesson works without sending anything. If you choose to send, the project receives exactly these fields: a random study token, an optional nickname, your quiz score and your eight answers, your one sentence reflection, your yes or no on going deeper, the number of sections you completed, and the lesson version. The reflection goes as you typed it, with the spaces at the start and end removed, up to 600 characters; the server keeps the first 600 characters and drops the rest. With each result, the server stores the time it arrived and a salted hash of your internet address, used for rate limiting. Nothing in the lesson asks for your name, email, or a date, and the page asks you to keep names, dates, and medical details out of the reflection.

Both submissions land in one database, which the maintainer reads only in aggregate. The welcome page carries Cloudflare Web Analytics, a cookieless page counter that records no personal data. The lesson carries no analytics script at all.

## How to delete
- **The board.** Delete the page from claude.ai and delete this folder.
- **Copies the project cannot reach.** Your own Claude chats and transcripts, device backups, anything you copied or exported, and any text message you sent stay where they are until you delete them yourself.
- **A lesson result or the count.** Send a delete request. Run the line you need in Terminal on a Mac, or in Git Bash on Windows. You can also ask Claude in this folder to send it; it shows you the command first. A reply of `{"ok":true}` means nothing remains under that key in the project's database. The study token is the only key to a lesson result, and the install id is the only key to the count.

For a lesson result, put your study token in place of `YOUR-STUDY-TOKEN`:

```
curl -X POST "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/ingest" -H "content-type: application/json" -d '{"kind": "delete", "token": "YOUR-STUDY-TOKEN"}'
```

For the count, put the `installId` from `my/receipt.json` in place of `YOUR-INSTALL-ID`:

```
curl -X POST "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/ingest" -H "content-type: application/json" -d '{"kind": "delete", "id": "YOUR-INSTALL-ID"}'
```

The address is `ingest_url` in `config.json`. If either request fails, [email security@warfarecommand.com](mailto:security@warfarecommand.com) with the token or the id, and the maintainer deletes the row by hand.

## What never belongs here
Keep these out of the board, this folder, and your chats: other people's personal information, anything classified or controlled unclassified, a password, a CAC PIN, or a Social Security number. Do not paste them. The assistant is instructed not to ask for them; if it does, stop and report it.
