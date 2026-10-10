<!-- Reader: Marines using Muster Out. Effect: understand the next step and the records the project holds. -->
# What Muster Out covers

Pack usmc-2026.10 covers the situations in the first table. For the situations in the second table, the assistant names the office to call first and builds no plan. Covered items name the office that confirms your eligibility, dates and any detail left to that office.

## Covered paths
| Situation | Covered | Notes |
| --- | --- | --- |
| Officer resigning a regular commission | Yes | MCO 1900.16 chapter 5, MARADMIN 175/24 timing |
| Officer retiring (20 or more years) | Yes | MCO 1900.16 chapter 2 retirement procedures, SBP, retired pay, TRICARE retiree enrollment |
| Enlisted retiring with 20 or more years of active service | Yes | FMCR transfer at 20 to 29 years; direct retirement at 30 or more. MCO 1900.16 chapter 7, MARADMIN 175/24, MARADMIN 326/23 and MMSR-2 guidance. The reporting unit submits to MMSR-2 through unit diary; IPAC confirms your record and dates. Shared transition, SBP and benefits items apply. |
| Enlisted or officer separating at EAS | Yes | No retirement or resignation request; confirm separation processing with IPAC. Transition gates, orders, and benefits tasks remain. |
| Reserve affiliation through DAP | Yes | Officer and enlisted windows, NAVMC 763, check in |
| SkillBridge | Yes | Category caps and approval rules from MARADMIN 280/24 and NAVMC 1700.2B. The sources conflict on approval and absence limits; confirm the applicable rule with the SkillBridge coordinator and approving command. |
| VA pre discharge claim through BDD | Yes | Timeline, evidence tasks, condition list. No rating predictions. |
| Leave | Yes | Advance leave limits, sell back cap, transition PTAD where the order allows it |

## Paths referred to an office
| Situation | Who to call first |
| --- | --- |
| Medical separation or disability retirement | PEBLO and Wounded Warrior Regiment |
| Involuntary separation | IPAC and legal assistance |
| Guard or Reserve retirement with nonregular pay | Unit Career Planner and Reserve Affairs |
| Another service | Your service personnel office |

## Setup help

### Can I use Claude Free?
You need Claude Pro or higher to save board data. The Free plan cannot store it. Muster Out adds no charge.

### Why does Claude ask me to publish?
Tap Publish when Claude asks. Publishing creates the board page in your Claude account; keep its visibility private and share its link only with people you choose.

### What if the chat closed during setup?
Paste the setup message into a new Claude chat. Claude looks for your existing board and resumes an unfinished setup.

### What if the Claude app lacks the board tools?
Open [claude.ai in a browser](https://claude.ai) and paste the setup message to give Claude access to the board tools.

### What if my work computer blocks claude.ai?
Use a personal phone or computer to open [claude.ai](https://claude.ai), then paste the setup message.

## Set up your board
If your path is covered, send this one message in any Claude chat: the Claude app on a phone, claude.ai, or the desktop app, including Claude Code and the desktop Code tab. Claude Pro costs $20 a month. You need Pro or higher; the Free plan cannot store board data.

```
Set up Muster Out for me. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/SETUP.md and follow it.
```

Claude checks the release files, asks you to tap Publish for your private board, and interviews you. Setup takes about 5 minutes. If the phone app cannot open the board, use claude.ai in your phone browser. The [welcome page](https://musterout.warfarecommand.com/#setup) has a Copy button for the message.

Claude Code and desktop Code tab users paste the same setup message. Developers who want a folder install can clone [the public release repository](https://github.com/warfarecommand/musterout-release). Folder updates verify each changed file against `release.json` and keep `my/`.

## Keep it current
Your board shows the weekly and update messages under Talk to Claude, each with a Copy button.

Weekly message:

```
Run the Muster Out weekly check. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/WEEKLY.md and follow it.
```

Update message:

```
Update Muster Out. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/UPDATE.md and follow it.
```

- **Weekly check.** During setup, Claude offers a Monday check if the chat supports recurring tasks. Confirm your timezone and time. If scheduling is unavailable or you skip it, send the weekly message any week. The check files possible MARADMIN matches for your path and the lines of effort on your board. It also checks for new versions.
- **Updates.** When a weekly check finds a newer version and records the notice, the board shows the update message with a Copy button. Paste it into any Claude chat; the board keeps its address and your data.

If your path is not covered, call the office listed above.
