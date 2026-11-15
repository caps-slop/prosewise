# prosewise for ChatGPT

Cleaned zips for ChatGPT's Skills upload. ChatGPT takes one skill per upload, so there is one zip per skill:

| zip | what it is | needed? |
|---|---|---|
| `prosewise.zip` | the writing skill: rules, references, linter | yes |
| `prosewise-voice.zip` | builds a personal voice profile from your own texts | optional |

`prosewise-conflicts` is not included: it moves skill folders on your own machine, which ChatGPT cannot do.

## Install

1. In ChatGPT open **Skills**, then **Create**, then **Upload from your computer**, and choose `prosewise.zip`. Repeat for
   `prosewise-voice.zip` if you want it.
2. Wait for the scan to finish. Start a **new** chat or task afterwards; skills are not added to a chat that is already open.
3. Ask for it by name, for example: "Use prosewise to rewrite this text so it reads plainly, without changing its facts."

Skills are offered to Business, Enterprise, Healthcare and Edu workspaces, and an admin must allow skill uploads.

## If it works in Work mode but not in regular Chat

Other users report the same: installed skills are available in Work mode and not in regular Chat. OpenAI does not
document it, so this is not confirmed for your account. prosewise loads its reference files on demand (`SKILL.md`
points to `references/*.md`), which needs the skill's files to be readable in the session. Use Work mode, or paste the
short rules from `../AGENTS.md` into your custom or project instructions.

## What was cleaned

Built from `plugin/skills/` by `pipeline/build_chatgpt.py`. Each zip has one top folder and exactly one `SKILL.md`;
`agents/` (Codex and Cursor interface files), `__pycache__` and dotfiles are left out; files are mode 0644, because zips
with 0600 files reportedly install but never become available; the entries are sorted with fixed timestamps, so an
unchanged source gives a byte-identical zip. The build also checks the limits OpenAI documents for skills (name 64,
description 1024 characters, 500 files, 25 MB per file, 50 MB per zip).

`prosewise-voice` keeps its profile under `~/.config/prosewise`, which a ChatGPT session may not keep between tasks.
Download the profile files it writes and keep them in a Project. Without the `prosewise` skill beside it, the voice
statistics skip the count of prosewise trigger words and say so; everything else works.

## Rebuild

```
python3 -I pipeline/build_chatgpt.py          # after changing anything under plugin/skills/
python3 -I pipeline/build_chatgpt.py --check  # fails if the zips are stale; publish_plugin.sh runs it
```
