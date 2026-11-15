---
name: prosewise-conflicts
description: >-
  Find other writing skills and plugins installed next to prosewise (humanizer, stop-slop, avoid-ai-writing, unslop
  and the like) and, with the user's agreement, disable them reversibly so two rulebooks do not conflict. Use when
  the user asks to check for conflicting writing skills, after installing prosewise, when the prosewise start-up
  notice mentions conflicts, or to restore a skill prosewise disabled.
license: MIT
metadata:
  version: "0.5.2"
---

# prosewise-conflicts

prosewise already contains the rules of the writing skills it merged. With one of them loaded next to it, the agent
gets two rulebooks that disagree. This skill finds them and turns them off only when the user says so.

Everything goes through `scripts/conflicts.py` (Python 3, standard library). Run it from this skill's folder.

## Procedure

1. Scan: `python3 scripts/conflicts.py scan --project <current project root>`. Show the user the list as printed.
   - **CONFLICT** (`[x]`, suggested): a skill or plugin whose rules are merged into prosewise.
   - **possible conflict** (`[ ]`): another skill whose description is about writing, or one prosewise tracks but
     does not merge. Leave it unselected; say what it does in one line so the user can judge. Mention when it runs only when called by name, since such a
     skill does not compete unless the user calls it.
   - Plugins added from claude.ai (`@synced`) cannot be disabled locally; tell the user to turn them off in claude.ai.
   - A plugin that also provides non-writing skills is disabled as a whole; say which other skills go with it.
2. Ask which to disable. Default answer: the suggested ones. Never disable anything the user did not approve in
   this conversation, and never pick possible conflicts on your own.
3. Disable: `python3 scripts/conflicts.py disable <id> [<id> ...]` with the approved ids. Skill folders move to
   `~/.config/prosewise/disabled/`; Claude Code plugins are switched off with `claude plugin disable`.
4. Report what changed in a line or two, that Claude Code needs a restart to drop a disabled plugin, and how to undo:
   "restore <name>" or "restore everything".

## Other commands

| user says | run |
|---|---|
| what did prosewise disable? | `python3 scripts/conflicts.py list-disabled` |
| restore humanizer / restore everything | `python3 scripts/conflicts.py restore <id>` or `restore --all` |

Never delete a skill or plugin, never edit another skill's files, and never uninstall: disabling must stay
reversible.
