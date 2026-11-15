<p align="center">
  <img src=".claude-plugin/icon.png" width="96" alt="prosewise">
</p>

<h1 align="center">prosewise</h1>

<p align="center">
  <b>The writing skill that rules them all.</b><br>
  21 public anti-slop skills and Wikipedia's field guide to AI writing, merged into one rulebook your agent actually follows.
</p>

<p align="center">
  <img alt="licence: MIT" src="https://img.shields.io/badge/licence-MIT-blue">
  <img alt="rules: 299" src="https://img.shields.io/badge/rules-299-informational">
  <img alt="agents: Claude Code, Codex, Cursor and more" src="https://img.shields.io/badge/agents-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor%20%C2%B7%2060%2B-success">
</p>

<p align="center">
  <a href="#install"><b>Install</b></a> ·
  <a href="docs/GUIDE.md"><b>Guide</b></a> ·
  <a href="#use">Use</a> ·
  <a href="#clear-the-field">Clear the field</a> ·
  <a href="CREDITS.md">Credits</a>
</p>

---

Your agent writes "delve", "seamless" and "it's worth noting". It wraps a one-line fix in three headings and an
emoji. Its commit messages congratulate themselves. You can install one of the many skills that fight this, and
each covers part of the problem with its own lists, its own blind spots and its own over-corrections.

**prosewise** takes the best of them and resolves their disagreements. Every rule from 21 public writing skills
(humanizer, stop-slop, avoid-ai-writing, Cursor's unslop, tropes, writing-clearly-and-concisely, three comment
skills, two commit skills, four voice skills and more) was broken out, compared and merged into 299 rules, each
with a strength, thresholds, exceptions and an example. Where sources conflict, a written policy decides, and
integrity always wins: **prosewise** never invents a fact to make a sentence sound better.

## Why one skill, and only one

Every few weeks a new anti-slop skill appears, and following the trend means installing it next to the last one.
The rulebooks pile up, and three problems pile up with them:

- **Overlap.** Most skills ban the same words and patterns, each with its own list and its own threshold. Your
  agent reads the same advice several times, worded differently.
- **Contradiction.** The skills disagree. One bans every em dash while another tells the agent to keep the
  author's own. One wants Conventional Commits in every repository, another tells it to copy whatever the
  history already does. One cuts every "not X, but Y", another keeps the ones that contrast something real. With
  two rulebooks loaded, your agent either picks one at random or tries to satisfy both and over-edits.
- **Overload.** Each skill adds its own instructions and lists to your agent's context. Context spent on duplicate
  and conflicting rules is no longer available for your actual task.

**prosewise** carries that burden for you. The overlaps are merged into single rules. Each contradiction was
settled once, in writing, with the reason recorded. And your agent loads only the part it needs: the rules for
commit messages when it writes a commit, the comment rules when it touches code. What is left is efficient and
effective: one rulebook, no conflicts, and nothing loaded that the task does not need.

> [!IMPORTANT]
> **prosewise works best on its own, so it is suggested to install it on its own.** If you already use humanizer, stop-slop, avoid-ai-writing, unslop or another writing skill, remove it: their rules are already inside **prosewise**, and two rulebooks loaded side by side bring the conflicts back.

You do not have to hunt for them yourself: **prosewise** finds them for you (see
[Clear the field](#clear-the-field)).

## Install

### Claude Code
```
/plugin marketplace add caps-slop/prosewise
/plugin install prosewise@prosewise
```

### Codex, Cursor, Gemini CLI, Copilot and about 60 other agents
```
npx skills add caps-slop/prosewise --agent '*'
```

### Without node

Clone the repository and run `./install.sh` (Claude Code and `~/.agents/skills`), or
`./install.sh --dir <skills folder>` for any other agent. For agents that only read `AGENTS.md`, copy
[AGENTS.md](AGENTS.md) into your project.

### Clear the field

Right after installing, **prosewise** looks for other writing skills and plugins on your machine: in Claude Code,
in `~/.agents/skills` (Codex and the agents that share it), and in the Cursor, Gemini, Windsurf and OpenCode
folders. It shows you what it found, in two groups:

- **Conflicts**: skills whose rules are already merged into **prosewise**, such as humanizer, stop-slop or unslop.
  These are suggested for disabling.
- **Possible conflicts**: other skills whose description is about writing. These are listed for you to judge and
  left unselected.

Nothing is disabled without your yes, and everything can be undone. Skill folders are moved to
`~/.config/prosewise/disabled/`, never deleted, and Claude Code plugins are switched off with
`claude plugin disable`. To restore one, ask your agent to "restore humanizer", or "restore everything" (details in
the [guide](docs/GUIDE.md#re-enabling-what-prosewise-disabled)).

When it runs:

| installed with | the check |
|---|---|
| `./install.sh` | runs at the end and asks you which to disable (`--no-scan` skips it) |
| Claude Code plugin | at the first session, a one-line notice tells you if conflicts exist; it never changes anything |
| any agent, any time | ask "check for conflicting writing skills", or call `/prosewise:prosewise-conflicts` (Claude Code) or `$prosewise-conflicts` (Codex) |

## What it does

### Prose

It cuts the filler, hype and chatbot wrapping and keeps every fact, number and hedge.

```
in   The new tool is a revolutionary game-changer. It exports CSV files.
out  The new tool exports CSV files.
```

### Code comments

It removes comments that narrate the code or shout, and keeps the ones that explain why, along with lint and type-checker directives.

```python
# in
def parse(raw):  # noqa: C901
    # 🚀 This robust, cutting-edge parser seamlessly handles all edge cases!
    # IMPORTANT: Do not remove!!!
    data = json.loads(raw)  # type: ignore[arg-type]
    return data

# out
def parse(raw):  # noqa: C901
    data = json.loads(raw)  # type: ignore[arg-type]
    return data
```

### Commit messages and PR descriptions

It follows your repository's convention, and says what changed and why.

```
in   ## 🎉 Overview
     In this PR, I have embarked on a comprehensive journey to refactor the billing module! 💪
     ## ✨ Key Changes
     - **Refactoring:** Refactored the billing module.
     - **Performance:** Invoice generation now takes 1.2 s instead of 4.8 s on the March dataset.
     - **Testing:** Added 14 unit tests.
     ## 🙏 Conclusion
     Let me know if you have any questions! Happy to help!

out  Refactor the billing module. Invoice generation now takes 1.2 s instead of 4.8 s on the March
     dataset. Added 14 unit tests.
```

### Knowing when to stop

Text that is already good comes back untouched. "Robust" in "the retry queue is robust
against worker crashes because every job is leased with a deadline" is the engineering word, not hype, and
**prosewise** leaves it alone.

### Your voice

The companion skill `prosewise-voice` reads your own emails, posts and documents, on your
machine, and builds a profile of how you write: sentence length, punctuation, openers, the words you use and the
ones you never use. Ask for a draft "in my voice" and the profile takes priority over the generic rules, except the rules on facts.

All examples above are real outputs from the evaluation set.

## How it compares

107 test cases, five systems, three blind judges who never saw which output came from which skill:

| | **prosewise** | no skill | humanizer | stop-slop | avoid-ai-writing |
|---|---|---|---|---|---|
| quality, 1 to 5 | **4.49** | 4.24 | 4.14 | 4.02 | 3.89 |
| outputs that changed the meaning | **0** | 12 | 2 | 7 | **0** |
| good text damaged by over-editing | **1** | 4 | 8 | 21 | **1** |

**prosewise** ranks first overall and on the texts that need editing. Along with avoid-ai-writing, it is the only
system whose outputs never changed the meaning. On texts that should be left alone, it ties with the plain model.
Many cases come from the authors of the merged skills, which favours their rules, so read these numbers as a sanity
check rather than a leaderboard.

## Use

Most of the time you do not need to name it: your agent loads it when you ask for writing, rewriting, a review or a
commit message. To call it directly use `/prosewise` (Claude Code) or `$prosewise` (Codex).

- "Does this README sound AI-generated?" gives a list of findings and makes no edits
- "Rewrite this email, strict" gives the cleaned text
- "Write the commit message for the staged changes" gives the message and nothing else
- "Build my voice profile from ~/writing" (one subfolder per genre: `email/`, `posts/`, `docs/`)
- "Rewrite this in my voice"
- "Check for conflicting writing skills" lists the competing skills and disables the ones you approve

Three sensitivity levels (`relaxed`, `standard`, `strict`), per-project settings in `.prosewise.yaml`, and a small
standard-library Python linter that can gate CI on generated docs. Everything is in the
**[full guide](docs/GUIDE.md)**.

## Always current

Models change their habits with every release, and the lists that track them go stale. **prosewise** is built to
stay current. An update routine watches for new writing skills worth adding.
Each change is analysed rule by rule, merged under the same written policy, and evaluated again before it ships.
New tells reach you as a plugin update, and you never have to evaluate or reconcile another skill yourself.

## Credits and licence

**prosewise** stands on the work of the authors listed in [CREDITS.md](CREDITS.md). Their rules are restated in our
own words, with credit, and each upstream source keeps its own licence. **prosewise** itself is MIT.
