# prosewise guide

prosewise is an agent skill for writing. It makes an AI agent's text read like a careful person wrote it: plain,
specific, in the writer's voice, and with every fact intact. It covers prose, code comments, commit messages and PR
descriptions, in English.

## 1. Skill or plugin?

A skill is a folder with a `SKILL.md` file (instructions with a short description) plus optional reference files
and scripts. The format is an open standard, so the same folder works in Claude Code, Codex, Cursor, Gemini CLI,
GitHub Copilot, OpenCode and about 60 other agents. The agent reads the description, decides when the skill is
relevant, and loads the rest only then.

A plugin is a package. It can hold several skills plus things a skill cannot provide: slash commands, hooks (code
that runs on events, such as before a commit), subagents and MCP servers. Plugins are installed and updated from a
marketplace with a version number. Each agent has its own plugin format.

| you need | use |
|---|---|
| instructions the agent applies when relevant, in any agent | a skill |
| several skills installed and updated together | a plugin |
| something that runs automatically on an event (e.g. check every commit message) | a plugin with a hook (Claude Code, Cline, Kiro) |
| one-command install and updates through a marketplace | a plugin |

prosewise does both. The content lives in three plain skills, so every agent can use it. The plugin manifests wrap
those skills for Claude Code, Codex and Cursor marketplaces, and `npx skills` or `install.sh` covers everything else.
Nothing in the core depends on hooks or other plugin-only features. The Claude Code plugin has one hook, which shows
a one-time notice about conflicting writing skills; in every other agent you run the same check by asking for it.

## 2. Install

| agent | command |
|---|---|
| Claude Code | `/plugin marketplace add caps-slop/prosewise` then `/plugin install prosewise@prosewise` |
| Codex, Cursor, Gemini CLI, Copilot, OpenCode, Cline, Windsurf, ... | `npx skills add caps-slop/prosewise --agent '*'` (or `--agent codex`) |
| no node | `./install.sh` (Claude Code and `~/.agents/skills`), `./install.sh --dir <folder>` for others |
| agents that only read AGENTS.md | copy `AGENTS.md` into the project |

Instead of `caps-slop/prosewise` you can give a local path or any git URL you have access to.
`install.sh` copies the three skill folders into `~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex and
the other agents that read it). With `--link` it creates symbolic links to this folder instead of copies, so any
change here, including a `git pull` or an update run, reaches the agents at once with no reinstall.
`./install.sh --uninstall` removes them. At the end of an install the script checks for conflicting writing skills
(section 3); `--no-scan` skips the check.

## 3. Other writing skills

prosewise contains the rules of the writing skills it merged. If one of them is still installed, your agent loads two
rulebooks that disagree (one bans every em dash, the other keeps the author's; one wants Conventional Commits
everywhere, the other copies the repository) and either picks one at random or over-edits. The
`prosewise-conflicts` skill finds them and disables the ones you approve.

It looks in Claude Code (installed plugins, plugins added from claude.ai, `~/.claude/skills` and the project's
`.claude/skills`), in `~/.agents/skills` and the project's `.agents/skills`, and in the Codex, Cursor, Gemini,
Windsurf and OpenCode skill folders. Each finding is one of:

| label | meaning | default |
|---|---|---|
| CONFLICT | a skill or plugin whose rules are merged into prosewise (the list is rebuilt from prosewise's sources at every update) | suggested |
| possible conflict | another skill whose description is about fixing writing, or one prosewise tracks but no longer merges (for example after a licence change) | not selected; you judge |

Skills that run only when called by name (`disable-model-invocation: true`) are marked as such: they do not
compete unless you call them. A Claude Code plugin is disabled as a whole, so the list says which other skills it
provides. A skill that ships with sibling skills (sepia installs sepia-write, sepia-review and others) is matched by all of them. Plugins added from claude.ai cannot be disabled locally; turn them off in claude.ai.

Disabling is reversible. Skill folders move to `~/.config/prosewise/disabled/<agent>/` (a symlinked skill moves as the
link), with a record in `manifest.json`; Claude Code plugins are switched off with `claude plugin disable` and need a
restart. Nothing is deleted or uninstalled.

| when | how |
|---|---|
| `./install.sh` | runs at the end and asks; Enter accepts the suggestions, `n` keeps everything, numbers pick |
| Claude Code plugin | the first session after install or update shows a one-line notice if conflicts exist; it changes nothing |
| any time, any agent | "check for conflicting writing skills", `/prosewise:prosewise-conflicts`, `$prosewise-conflicts` |
| undo | "restore humanizer", "restore everything", "what did prosewise disable?" |
| from a terminal | `python3 skills/prosewise-conflicts/scripts/conflicts.py scan` (also `review`, `disable ID`, `restore --all`, `list-disabled`) |

### Re-enabling what prosewise disabled

Ask your agent, in any session: "what did prosewise disable?", then "restore dedash" or "restore everything". In
Claude Code you can also type `/prosewise:prosewise-conflicts restore everything`.

From a terminal, run the script from wherever the skill is installed (`~/.claude/skills/prosewise-conflicts` or
`~/.agents/skills/prosewise-conflicts` after `install.sh`):

```
python3 ~/.claude/skills/prosewise-conflicts/scripts/conflicts.py list-disabled
python3 ~/.claude/skills/prosewise-conflicts/scripts/conflicts.py restore claude:dedash agents:dedash
python3 ~/.claude/skills/prosewise-conflicts/scripts/conflicts.py restore --all
```

The ids are the ones `list-disabled` prints: `<agent>:<skill>` for a skill folder, `plugin:<name>@<marketplace>`
for a Claude Code plugin. A restored folder goes back exactly where it was; a restored plugin is re-enabled with
`claude plugin enable`. Restart the agent for the change to take effect. If the original place is taken again (for
example you reinstalled the skill meanwhile), the script leaves both untouched and says so.

## 4. Using prosewise

You rarely need to name it: agents load it when you ask them to write, rewrite or review text, or to write a commit
message. To call it explicitly use `/prosewise` (Claude Code) or `$prosewise` (Codex).

| you say | mode | you get |
|---|---|---|
| "Does this README sound AI-generated?" | audit | findings (`rule · quote · why · fix`), no edits |
| "Clean up this paragraph" | rewrite | the new text; a short note only when something needs you (a gap, a claim to confirm) |
| "Tighten docs/intro.md in place" | edit | minimal edits in the file; a short note only when something needs you |
| "Write the commit message" | write | the message only |
| "Clean the comments in utils.py" | rewrite | the code only |
| "Rewrite this in my voice" | rewrite with voice | as rewrite, using your profile |

If a fix needs a fact it does not have, prosewise asks. When it cannot ask, it leaves a visible `[gap: ...]`
instead of inventing something. When you ask it to choose between options your text states, it chooses. A text
that is already clean comes back unchanged and without comment (in audit mode it says the text is clean).
Rule ids are hidden unless you ask for them or set `show_rule_ids: true`.

### Sensitivity
Say "strict" or "relaxed" in the request, or set it in the config.
- `standard` (default): each rule's own thresholds. Most rules act only when a pattern repeats or clusters.
- `strict`: act on single occurrences. Good for text that will be read by people who hunt for AI tells.
- `relaxed`: only clusters and repeats. Good for your own drafts when you want a light touch.
Integrity rules (no invented facts, no changed meaning, code and quotes untouched) ignore sensitivity.

### Dashes
prosewise never writes em dashes (—). When a dash between clauses is the best mark it uses a spaced hyphen
( - ), at most 2 per 1,000 words and 1 per paragraph. It also avoids replacing every removed dash with a colon or
a semicolon, which would be a new habit. One exception: a voice profile built from an author's own writing that shows
em dashes brings them back at the measured rate, only when writing in that author's voice.

### Code comments
prosewise keeps comments that explain why (a constraint, an incident, a workaround) and removes comments that
restate the code, narrate the change history, decorate or shout. It never touches lint or type-checker directives,
licence headers or public API docs, and never changes code behaviour. When unsure, it keeps the comment.

### Commit messages and PR descriptions
It reads the repository's convention first: contributing docs, a commitlint config, recent `git log`. With
Conventional Commits it follows them, including breaking-change markers. Without a detectable convention it writes
a plain imperative subject ("Fix pagination off-by-one"), a blank line, then what changed and why. It avoids
self-praise, emoji and chat formatting, and states nothing the diff does not show. Attribution trailers follow
your tool's settings.

## 5. Your voice

The `prosewise-voice` skill builds a profile from text you wrote yourself.

1. Collect samples in one folder with a subfolder per genre; the subfolder names become the genre names:
   ```
   ~/writing/
     email/   posts/   docs/   notes/
   ```
   Plain text, Markdown or `.eml` files, any depth inside each subfolder. Only your own words: drop forwarded
   threads, signatures, automated mail and anything an AI drafted.
2. Ask your agent, in the normal chat: "Build my voice profile from ~/writing". You can also call the skill by name:

   | agent | command |
   |---|---|
   | Claude Code, plugin install | `/prosewise:prosewise-voice build my profile from ~/writing` |
   | Claude Code, `install.sh` install | `/prosewise-voice build my profile from ~/writing` |
   | Codex | `$prosewise-voice build my profile from ~/writing` |

   The skill asks a few questions (profile name, things you already know about your style), measures each genre
   with a local script, reads samples, and drafts the profile.
3. Review the draft. Correct anything wrong; say what you do not want stored.
4. Use it: "rewrite this in my voice", or set `voice.apply: always` in the config.

Sample sizes: at least 3 pieces and 500 words per genre to start (marked provisional), 20+ items for firm
patterns, 200+ for rare habits. Genres stay separate: your email habits are never averaged with your docs.

Privacy: everything runs on your machine. The corpus stays where you keep it. The profile, stored in
`~/.config/prosewise/profiles/<name>/`, holds statistics, rules and short fragments, not documents. Nothing goes
into a git repository unless you ask. To update the profile, say "update my profile with these files". To fix it,
say "that's not me: I never ...".

What the profile can and cannot do: it can bring back habits the generic rules would remove (em dashes, "that
said", long sentences) at the rate you use them. It cannot permit invented facts, invented personal experience,
filler or flattery.

## 6. Configuration

Optional. `~/.config/prosewise/config.yaml` applies everywhere; `.prosewise.yaml` in a project overrides it; what you
say in a request overrides both.

```yaml
sensitivity: standard
modules: [marketing-social, genres]   # extra rules: posts and launch copy; fiction, postmortems, tickets, articles, journalism
                                      # also: ste-strict (controlled English), academic-econ (economics papers)
voice:
  profile: ~/.config/prosewise/profiles/me
  apply: on-request              # or always
disable: [FMT-006]               # rule ids to skip (integrity rules cannot be disabled)
extra_triggers: [leverage synergies]
commits:
  convention: auto               # auto | conventional | plain | free text
comments:
  when_unsure: keep
```

Rule ids appear in audit findings, so `disable: [ID]` is the quickest way to silence a rule you disagree with.

## 7. The linter

`skills/prosewise/scripts/lint.py` is a small Python script, standard library only, that counts what can be
counted: trigger words and phrases, em dashes, the dash budget, bold and emoji density, arrow chains, and
sentence-length spread (information only). Agents run it when they can; you can too:

```
python3 skills/prosewise/scripts/lint.py --sensitivity standard README.md
cat draft.txt | python3 skills/prosewise/scripts/lint.py --json
```

It skips code, inline code, URLs, block quotes and quoted phrases. Its findings are candidates, not verdicts, and
never proof that a machine wrote something. Exit code 1 means a hard finding is present, so it can gate a CI job
on generated docs.

## 8. How the rules were made

Twenty-one public skills (humanizer, stop-slop, avoid-ai-writing, Cursor's unslop and technical-writing, tropes,
anti-slop-writing, writing-clearly-and-concisely, three comment skills, two commit skills, four voice skills, sepia,
plain-writing, ste80-humanizer and econ-write) and Wikipedia's *Signs of AI writing* were each broken into atomic rules (1,264 in total). Those
were merged into 299 canonical rules under a written policy: integrity first, no fix that creates a new tell,
thresholds instead of bans where sources disagree, evidence weighted by independent origin, the specific beating the
general, and the local convention beating house style. Eighteen questions were decided by the owner
(`analysis/decisions.yaml`). Every canonical rule lists the sources it came from; see `CREDITS.md`.

The rule files in `skills/prosewise/references/` are generated from that catalogue, so do not edit them by hand.
To change a rule, change the catalogue or add a decision, then rebuild (see the repository README).

## 9. Limits

- English only for now.
- The patterns describe current models' habits. Lists age, so the catalogue is refreshed from upstream regularly.
- Humans write many of these patterns too. prosewise improves text. It does not detect authorship, and its
  findings should never be used to accuse anyone.
