# Release notes

## 0.2.18 (2026-10-18)
- Registration now shows up reliably on new boards, with a Register link in Settings if you miss it.
- Plan, Timeline, VA Claim and Settings are shorter and easier to use on a phone.

## 0.2.17 (2026-10-18)

- Registration now appears when your plan is ready, with a link in Settings if you need it.
- Today is easier to reach on iPad, and stopping counts now asks you to confirm.

## 0.2.16 (2026-10-17)
- Setup asks for consent once, checks any date in the past before you save it, and shows exactly which date to fix if your leave plan cannot save.
- New boards register with one tap after the plan loads, and links in Muster Out emails open a page with one clear button.

## 0.2.15 (2026-10-16)
- The VA rating math now combines both arms and both legs correctly, and intake keeps your place when you use a keyboard.
- Public files leave out internal provider data, and the security page lists exactly what deleting your records removes.

## 0.2.14 (2026-10-16)
- Setup, updates and weekly checks work inside Claude chat by checking a downloaded copy of the npm package against the same publisher signature and file hashes.
- Leave is one tap from Today on every board, and the leave chart opens as soon as you save your first balance.

## 0.2.13 (2026-10-16)
- Setup and updates check Muster Out's publisher signature before installing, and weekly checks file only signed notices.
- Help lines are plain numbers you can copy, stuck updates finish on their own, and enlisted retirees get the right MMSR-2 desk.

## 0.2.12 (2026-10-15)
- Export brief: turn your plan into a short PowerPoint for your command or a mentor, with a timeline, key milestones and decisions. Private details stay off unless you add them.
- Saving the file needs one update through Claude. Until then, the brief sheet lets you copy the brief text.

## 0.2.11 (2026-10-15)
- A tighter, cleaner board on every screen: compact header, two-line rows, one spacing scale, and an update status you can see with a clear success or retry.
- Setup now asks once to count installs and usage. Counts never include your plan, notes, dates or questions, and you can stop or delete them in Settings.

## 0.2.10 (2026-10-15)
- Date edits save and can be retried after a failed write. VA dates follow the last active-duty day, including a confirmed override, with an earlier confirmation target and a separate 1-year filing boundary.
- VA Class II dental guidance uses the current 180-day application window. Privacy, watch coverage and update help match the shipped routes.
- Required release checks now include date-editor saves, failure and retry, VA boundary fixtures and current policy rules.

## 0.2.9 (2026-10-15)
- Update now works again. Boards on 0.2.6 or earlier showed "could not be verified" for 0.2.7 and 0.2.8 because those releases carried one note instead of two.
- Includes everything in 0.2.7 (your coach) and 0.2.8 (works on Claude Free).
- The pack stays usmc-2026.10.

## 0.2.8 (2026-10-15)
- Works on Claude Free. An owner test on a Free account installed the board in a Project, saved checked items, and kept them after closing and reopening the app twice. Claude Pro at $20 a month gives more room for long coach chats.
- Setup, help and the board no longer say Pro is required.
- The pack stays usmc-2026.10.

## 0.2.7 (2026-10-14)
- Your coach: set up a Muster Out Project in the Claude app, paste the coach block and type Start. The coach reads your board at every chat and offers a Monday check-in.
- Today shows a coach card with your last check-in and its next step. The setup steps replace pasting a Project link.
- What your coach knows lists the facts your coach keeps on your board. Add, edit or delete them, with Undo. The Project chat and Ask both save there, and every save is read back.
- Ask keeps your last 10 questions and answers on your board until you clear them. Save to coach memory turns an answer into a coach fact.
- Coach check-ins show on the board, newest first.
- The pack stays usmc-2026.10.

## 0.2.6 (2026-10-14)
- Phone layout: reference tables on the VA Claim, Benefits and Leave screens show as labeled cards on phones, with no split words or empty columns. Month labels stay with leave balances.
- Dates name the target, the opening and the close, and say whether a window is projected or confirmed. The BDD window stays projected until your service end and its endpoints are confirmed.
- Shared boards are view only: profile and rebuild actions are hidden for viewers.
- Deleting a condition asks to confirm and offers Undo. Each condition shows its next evidence step.
- Instructions and references follow your path and grade. VSO options each end with a next step.
- Leave warns about overlaps as soon as you save, and one continuous block can run longer than 30 days.
- Timeline opens in List on phones. The bottom tabs are solid and long titles get their own row.
- The Veterans Crisis Line (dial 988, then press 1, or text 838255) is on Today and in More.
- The ten ready-made prompts are on the Project screen with Copy buttons.
- The pack stays usmc-2026.10.

## 0.2.5 (2026-10-14)
- Check for updates says Up to date when your board already has the newest release, instead of Could not check.
- Settings shows your path and grade group in words, such as Separating at EAS · E-6 to E-7.
- VA math and Exposures on the VA Claim tab explain what to add when they are empty, instead of opening blank.
- Setup and update instructions lead with the current feed list and explain why the weekly Watch feed files carry no release hash.
- The pack stays usmc-2026.10.

## 0.2.4 (2026-10-14)

- The header is compact on phones, and the plan starts near the top of the screen. The EAS date sits on one line next to the title.
- Timeline is its own tab and opens on the timeline, with a List view one tap away. Lanes show only what falls in the visible dates, with earlier and later counts.
- Marking an item done asks you to confirm and gives you 8 seconds to undo. Plan has a Done filter, and done items can be reopened.
- After setup, the board shows that it is building, then a short note on what to add next.
- Plain labels: Join the Reserves (Direct Affiliation Program) and VA claim timeline.
- Phones and tablets use the bottom tabs. Wide screens use tabs under the header instead of a side rail.
- The pack stays usmc-2026.10.

## 0.2.3 (2026-10-13)

- Setup and update instructions state the two accepted release feed lists on their own lines, so a setup chat no longer stops on the 0.2.2 manifest.
- The board, pack and dates are unchanged from 0.2.2. The pack stays usmc-2026.10.

## 0.2.2 (2026-10-12)

- Enlisted FMCR transfers on the last day of the month count leave through the transfer date, per MCO 1900.16 Appendix E. Retired List retirement still stops the day before.
- The update check reads both public CDNs, verifies each signature, and takes the newest release, so a stale CDN copy no longer hides an update.
- The pack stays usmc-2026.10.

## 0.2.1 (2026-10-12)

- Deadlines compute from your entered EAS, resignation, retirement or FMCR date, including a planned date. Late transition gates appear as late.
- Dates counted from a planned date say From planned date. Tap your date on Today to edit it; saving moves the deadlines.
- Ask knows today's date, starts with late items, writes dates as 12 OCT 2026, and shows bold text and short lists.
- Item steps name other items by their titles.
- Updating a board preserves dates you set and lists edited pack items for review. Actual approvals, orders and appointments stay undated until you record them.
- The pack stays usmc-2026.10. This release updates the date rules and citation index without changing the source texts.

## 0.2.0 (2026-10-12)

- The board uses Today, Plan, Dates, Claim and More, with short action rows and steps and sources behind each item.
- Setup ends at Open your board. Answer there, keep an undated plan if you have no date, and add optional details later.
- Ask about your plan answers from this board. The Project guide and ten starter workflows help review records and decisions as drafts to verify.
- A verified pasted update adds the artifact capability at the same address. Update now is available when the signed update channel passes its release gates; pasted recovery remains available.
- Save failures keep your draft and show recovery steps. Copy diagnostic and report review work even when board data or Claude is unavailable.
- Privacy and operations explain CDN reads, uploads, connectors, separate report and usage consent, and deletion receipts. Sending reports and counts remains behind the learning release gate.

## 0.1.6 (2026-10-09)

- Confirmation and welcome emails list your email choices in plain English.
- The email template sources ship with the backend code, so the public release shows exactly what subscribers receive.

## 0.1.5 (2026-10-09)

- Leave projections now count from the date of your leave balance, count overlapping leave once, apply the 30 September carryover limit, and stop at your last active day.
- Transition deadlines follow MCO 1700.31A (2 Mar 2026): initial counseling and pre-separation counseling 365 days before EAS, TRS 180, Capstone 120, and Commander's Verification 90.
- Updating your board now corrects items the pack changed and adds new items. Your dates, notes, and status stay as they are; anything you edited goes to review.
- New items cover the final household goods move and the VA intent to file. The benefits table now states VA dental Class IV and CHAMPVA eligibility correctly.
- A board that is not set up yet shows only the next step. Leave you asked to cancel stays charged until MOL shows it canceled.
- Everyone uses the same setup message in any Claude chat, including Claude Code. The zip download is retired; developers can clone the public release repository.
- Feed sync rejects unsafe links, oversized text, and incomplete feeds before replacing the last good feed. The weekly check reports a failed feed instead of an empty week.

## 0.1.4 (2026-10-09)

- Enlisted retirement covers FMCR transfer at 20 to 29 years of active service and direct retirement at 30 or more. New items cover eligibility, grade limits, obligations, CO counseling and Appendix J, waivers, HQMC receipt, PCS cancellation, status changes and the 45-day modification deadline.
- Enlisted requests go through the reporting unit diary to MMSR-2. The copied MMSR-2 guidance confirms the 6-to-18-month window for retirement and FMCR. Coverage now lists covered paths and the offices for paths outside the pack.
- Register your board anonymously from the setup link or the board banner, then sign up for correction alerts.
- The setup message button counts setup attempts without sending board data. Registration counts each random install id once.
- Warfare Command forms accept tool suggestions and updates signups. Suggestions go to the feedback inbox.
- The lesson link now opens AI 101 at Warfare Command.

## 0.1.3 (2026-10-09)

- The board has weekly and update messages with links and Copy buttons under Talk to Claude.
- Setup reads your answers back in plain words and accepts dates as you write them. It explains late items and where to start.
- Weekly reports use mil dates and say when a notice is only a possible match.
- The What if table shows items on your board and uses the same DAP deadline as the critical path.

## 0.1.2 (2026-10-09)

- Set up from any Claude chat: paste one message and Claude installs your board, checks every file, and interviews you. No download and no Claude Code needed.
- A weekly check in Claude files new MARADMINs onto your board and tells you when a new version is ready.
- The board's update banner tells you what to say to Claude.

## 0.1.1 (2026-10-09)

- Corrected transition, SkillBridge, Reserve affiliation, benefits, and VA claim guidance after three independent reviews.
- PTAD blocks no longer reduce your leave balance.
- Claude checks for new releases and can update your copy while keeping your board and data.

## 0.1.0 (2026-10-08)

- First pilot.
