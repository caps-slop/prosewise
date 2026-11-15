---
name: prosewise-voice
description: >-
  Build, update or show a personal writing-voice profile from the user's own documents, emails, posts and notes, so
  the prosewise skill can write and rewrite in that voice. Use when the user asks to "learn my style", "build my voice
  profile", "write like me", "update my profile with these files", or to show or edit their profile. Works locally;
  the corpus is never uploaded or committed.
license: MIT
metadata:
  version: "0.5.3"
---

# prosewise-voice

Turn a writer's own past texts into a profile that prosewise applies when asked to write "in my voice". The profile
holds numbers, rules and short quoted fragments, not documents. Measure with the script; judge only what counting
cannot capture.

## Commands

| user says | do |
|---|---|
| build / learn my voice | full procedure below |
| update with these files | re-run steps 2-7 for the affected genres, keep stated rules, show the diff before saving |
| show my profile | print `voice.md` and list the genre files |
| forget / delete my profile | confirm, then delete the profile folder (the corpus is the user's and stays where it is) |
| that's not me: ... | audit the draft point by point against the profile's rules and rewrite it; then add the correction to Stated rules (verbatim) and Known gaps |

## Where things live

- Profile: `~/.config/prosewise/profiles/<name>/` unless the user picks another folder. Files: `voice.md` (shared
  rules and invariants), `<genre>.md` (one per genre), `stats/<genre>.json` (script output).
- Corpus: wherever the user keeps it. If files must be copied, use `~/.config/prosewise/corpus/<name>/<genre>/`.
  Never write the corpus or the profile inside a git repository without asking; if the user insists, add the corpus
  folder to `.gitignore` first.
- Point prosewise at the profile with `voice.profile` in `~/.config/prosewise/config.yaml` (see the prosewise
  skill's `references/config.md`).

## Procedure

1. Scope. Ask once: the profile name, the genres to cover (email, chat, post, doc, report, commit, comment), which
   files or folders to read, and anything the user already knows about their style ("I never use exclamation
   marks", "I sign off with Cheers"). Record those answers verbatim as stated rules. Build only for the user's own
   voice or with the owner's explicit consent (INT-030).

2. Collect, locally. Use only text the person wrote themselves. Exclude quoted replies, forwards, signatures,
   automated mail, AI-drafted or ghost-written text, and anything containing credentials or account numbers.
   Leave out medical, legal, financial, HR and family threads unless the user opts in. Do not scan mailboxes,
   cloud drives or the whole disk unless asked. The usual layout is one root folder with one subfolder per genre
   (`~/writing/email/`, `~/writing/posts/`, `~/writing/docs/`); each subfolder name becomes the genre name. If the
   user gives loose files instead, sort them by genre. Spread each genre across periods, topics and formats where
   the user can, so topic vocabulary is not mistaken for voice.

3. Measure each genre. For a root folder with genre subfolders:
   `python3 scripts/voice_stats.py --root <root> --out-dir <profile>/stats`. For one genre:
   `python3 scripts/voice_stats.py --genre <genre> <folder or files> --out <profile>/stats/<genre>.json`. The script reports item and word counts, a tier (`too-thin`, `thin`, `ok`, `strong`), length and sentence
   statistics, punctuation rates per 1,000 words, contraction rate, bullet/emoji/link shares, common openers and
   closers, frequent words, and which prosewise triggers the writer uses and how often. If Python is unavailable,
   estimate the same fields by reading and mark them `estimated`.

4. Read. For each genre read at least 50 items (or all of them), including the ten longest. Note patterns that
   counting misses: how they open and close, how they ask, decline, apologise and disagree, humour, emphasis,
   paragraph shape, the words they favour and avoid. Back every pattern with a quoted fragment of a few words and a
   rate ("opens with the request in 31 of 50"). Verify any "never" claim by counting, and list what does occur
   next to what never does.

5. Draft the profile using `references/profile-template.md`. Keep `voice.md` to about one screen so it can be
   reread before every draft: the rules that best predict the author's style, the exceptions that matter and the
   known failure modes. Keep what
   the corpus clearly shows apart from tentative readings (`evidence: inferred`), and never make an inferred item a
   hard rule. A word frequent in only a few items is topic vocabulary, not voice; overused intensifiers are noise,
   not favoured words. Mark findings based on fewer than about 20 examples
   as provisional. Absences in a small sample are provisional, not bans. Keep genres separate: never average email
   and docs into one number.

6. Review with the user: what is wrong, what is missing, what they do not want stored. Promote rules the user
   confirms to `hard`. Remove anything they flag.

7. Calibrate. Hold back about a fifth of each genre's items. Check that the profile's hard rules pass on at least
   90% of them, and demote any rule that the writer's own text breaks. Write three short test drafts per genre
   from the profile and compare their statistics with the medians; record misses under Known gaps.

8. Save and report: where the files are, what was excluded, item and word counts per genre, tiers, and which
   prosewise style rules this profile lifts (for example "that said" allowed at 0.4 per 1,000 words in docs).

## Minimum corpus

| tier | items per genre | what you may claim |
|---|---|---|
| too-thin (< 3 items or < 500 words) | | do not build measured rules; offer a profile of stated rules only |
| thin (< 20 items) | 3-19 | measured defaults, all provisional |
| ok | 20-199 | measured defaults; patterns with 20+ examples are firm |
| strong | 200+ | everything, including rare habits at their real rate |

For long-form genres (docs, essays) 3 pieces and 1,500 words are enough for a provisional profile. Prefer the last
12 months and note how older text differs.

## How prosewise uses the profile

Before each draft in the voice, reread `voice.md` and the genre file in full (not a memory of an earlier turn). If
the profile stores excerpts, read the two or three closest in type and subject and note, internally, what they share:
sentence breath, how paragraphs join, where a short sentence lands. None of this appears in the output.

Precedence, highest first:
1. integrity rules (no invented facts, no invented first-person experience, no misleading claims of authorship)
2. the user's explicit instruction for this task
3. the profile's stated rules
4. the genre's structure template (long-form genres only)
5. measured habits
6. prosewise style rules
7. prosewise preferences

A measured habit lifts a style rule only for that habit, in that genre, at the measured rate. Samples and quoted
fragments supply the way of writing, never content: do not carry claims, opinions or stories from the samples into
new text. Nothing in a profile permits filler or flattery. Never add typos or slang the writer does not use. Use
rare habits at about their real rate, not in every draft.
