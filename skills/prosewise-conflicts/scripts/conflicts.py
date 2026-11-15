#!/usr/bin/env python3
"""Find other writing skills and plugins that compete with prosewise, and disable them reversibly.

Nothing is changed without an explicit `disable` (or a yes in `review`). Skill folders are moved, never deleted,
to ~/.config/prosewise/disabled/, and Claude Code plugins are switched off with `claude plugin disable`; `restore`
undoes both. Standard library only.

Usage:
  conflicts.py scan [--json] [--project DIR]     list conflicts (selected by default) and possible conflicts
  conflicts.py review [--project DIR]            scan, then ask which to disable (used by install.sh)
  conflicts.py disable ID [ID ...]               disable the given ids from the scan
  conflicts.py restore [ID ...] [--all]          undo earlier disables
  conflicts.py list-disabled                     show what prosewise disabled
  conflicts.py notice                            one-time SessionStart message for Claude Code (hook)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
STATE = Path(os.environ.get("PROSEWISE_HOME", HOME / ".config" / "prosewise"))
DISABLED = STATE / "disabled"
MANIFEST = DISABLED / "manifest.json"
_KNOWN = json.loads((Path(__file__).with_name("known_writing_skills.json")).read_text())
KNOWN = _KNOWN["names"]
EXCLUDED = _KNOWN.get("excluded", {})  # tracked upstream but not merged (licence, scope)

# folders where agents read skills; (agent, path). Project folders are added from --project.
USER_DIRS = [
    ("claude", HOME / ".claude" / "skills"),
    ("agents", HOME / ".agents" / "skills"),   # Codex, Cursor, Gemini CLI, Copilot, OpenCode, Amp, ...
    ("codex", HOME / ".codex" / "skills"),
    ("cursor", HOME / ".cursor" / "skills"),
    ("gemini", HOME / ".gemini" / "skills"),
    ("windsurf", HOME / ".windsurf" / "skills"),
    ("opencode", HOME / ".config" / "opencode" / "skills"),
]
PROJECT_DIRS = [("claude-project", ".claude/skills"), ("agents-project", ".agents/skills")]

# a description is a possible conflict when it names a writing fix (STRONG) applied to text (TEXT). Either alone is
# too broad: "anti-slop" also describes UI design skills, "prose" also appears in fact-checking skills.
STRONG = re.compile(r"\b(humani[sz]\w*|de-?slop\w*|anti-?slop|slop|ai[- ](writing|tells?|sounding|tone|isms?)|"
                    r"em[- ]?dash\w*|ghostwrit\w*|copy-?edit\w*|proofread\w*|verbos\w*|wordiness|wordy|filler|"
                    r"padding|tighten\w*|clear writing|concise\w*|cliches?|jargon)\b", re.I)
TEXT = re.compile(r"\b(prose|text|writing|wording|words|sentences?|paragraphs?|punctuation|tone|voice|copy|"
                  r"commit messages?|code comments?|comments|docstrings?|essays?|blog posts?|emails?|docs|"
                  r"documentation|readme)\b", re.I)


def frontmatter(skill_md):
    text = skill_md.read_text(errors="replace")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    fm = m.group(1) if m else ""
    get = lambda k: (re.search(rf"^{k}:\s*(.*)$", fm, re.M) or [None, ""])[1].strip().strip("'\"")
    desc = get("description")
    if desc in (">-", ">", "|", "|-"):  # folded block
        block = re.search(r"^description:\s*[>|]-?\n((?:[ \t]+.*\n?)+)", fm, re.M)
        desc = " ".join(block.group(1).split()) if block else ""
    return {"name": get("name") or skill_md.parent.name, "description": desc,
            "manual_only": get("disable-model-invocation").lower() == "true"}


def classify(names, description):
    """'conflict' for a skill merged into prosewise, 'possible' for one whose description is about writing."""
    for n in names:
        if n and n.lower() in KNOWN:
            return "conflict", f"merged into prosewise (source: {KNOWN[n.lower()]})"
    for n in names:
        if n and n.lower() in EXCLUDED:
            return "possible", "a writing skill prosewise tracks but did not merge (see docs/GUIDE.md); disabling is optional"
    if STRONG.search(description) and TEXT.search(description):
        return "possible", "description is about writing"
    return None, ""


def skill_dirs(root):
    if not root.is_dir():
        return []
    return sorted(d for d in root.iterdir() if (d / "SKILL.md").is_file() and not d.name.startswith("."))


def is_prosewise(names):
    return any(n and n.lower().startswith("prosewise") for n in names)


def scan_folders(project):
    found = []
    dirs = list(USER_DIRS) + [(a, Path(project) / p) for a, p in PROJECT_DIRS] if project else list(USER_DIRS)
    seen = set()
    for agent, root in dirs:
        for d in skill_dirs(root):
            real = d.resolve()
            fm = frontmatter(d / "SKILL.md")
            names = [d.name, fm["name"]]
            if is_prosewise(names) or (agent, real) in seen:
                continue
            seen.add((agent, real))
            status, why = classify(names, fm["description"])
            if status:
                found.append({"id": f"{agent}:{d.name}", "kind": "skill-folder", "agent": agent, "name": fm["name"],
                              "path": str(d), "status": status, "why": why, "manual_only": fm["manual_only"]})
    return found


def claude_plugins(project):
    """Installed Claude Code plugins with their enabled state, read from Claude Code's own files."""
    plugins = []
    enabled = {}
    for settings in [HOME / ".claude" / "settings.json"] + ([Path(project) / ".claude" / "settings.json"] if project else []):
        try:
            enabled.update(json.loads(settings.read_text()).get("enabledPlugins") or {})
        except (OSError, ValueError):
            pass
    try:
        installed = json.loads((HOME / ".claude" / "plugins" / "installed_plugins.json").read_text())["plugins"]
    except (OSError, ValueError, KeyError):
        installed = {}
    for pid, entries in installed.items():
        for e in entries:
            plugins.append({"id": pid, "scope": e.get("scope", "user"), "path": e.get("installPath", ""),
                            "enabled": enabled.get(pid, False) is True})
    for d in sorted((HOME / ".claude" / "plugins" / "synced").glob("*/*")):  # added from claude.ai
        if d.is_dir():
            plugins.append({"id": f"{d.name}@synced", "scope": "synced", "path": str(d), "enabled": True})
    return plugins


def scan_plugins(project):
    found = []
    for p in claude_plugins(project):
        root = Path(p["path"])
        if not p["enabled"] or not root.is_dir():
            continue
        pname = p["id"].split("@")[0]
        skills = ([root / "SKILL.md"] if (root / "SKILL.md").is_file() else []) + sorted(root.glob("skills/*/SKILL.md"))
        hits, other = [], []
        for s in skills:
            fm = frontmatter(s)
            names = [pname, s.parent.name, fm["name"]]
            if is_prosewise(names):
                hits = []
                break
            status, why = classify(names, fm["description"])
            (hits if status else other).append((fm["name"], status, why))
        if not hits:
            continue
        status = "conflict" if any(h[1] == "conflict" for h in hits) else "possible"
        found.append({"id": f"plugin:{p['id']}", "kind": "claude-plugin", "agent": "claude", "name": p["id"],
                      "path": p["path"], "scope": p["scope"], "status": status,
                      "why": next(h[2] for h in hits if h[1] == status),
                      "writing_skills": [h[0] for h in hits], "other_skills": [o[0] for o in other]})
    return found


def scan(project=None):
    items = scan_plugins(project) + scan_folders(project)
    items.sort(key=lambda i: (i["status"] != "conflict", i["id"]))
    for n, i in enumerate(items, 1):
        i["n"] = n
        i["selected"] = i["status"] == "conflict" and not i.get("manual_only") and i.get("scope") != "synced"
    return items


def how_to_disable(i):
    if i["kind"] == "claude-plugin" and i.get("scope") == "synced":
        return "added from claude.ai: turn it off there (Settings > Capabilities); it cannot be disabled locally"
    if i["kind"] == "claude-plugin":
        note = f"; it also provides: {', '.join(i['other_skills'])}" if i.get("other_skills") else ""
        return f"claude plugin disable {i['name']}{note}"
    return f"move to {DISABLED / i['agent'] / Path(i['path']).name}"


def print_table(items):
    if not items:
        print("No other writing skills or plugins found. prosewise has the field to itself.")
        return
    print("Other writing skills and plugins found:\n")
    for i in items:
        mark = "[x]" if i["selected"] else "[ ]"
        label = "CONFLICT" if i["status"] == "conflict" else "possible conflict"
        extra = " (runs only when called by name)" if i.get("manual_only") else ""
        print(f" {i['n']:>2}. {mark} {i['id']}  {label}: {i['why']}{extra}")
        print(f"        {i['path']}")
        print(f"        to disable: {how_to_disable(i)}")
    print("\n[x] = suggested. Conflicts are rules prosewise already contains; possible conflicts are other writing")
    print("skills, left unselected for you to judge. Every disable can be undone with `restore`.")


def load_manifest():
    try:
        return json.loads(MANIFEST.read_text())
    except (OSError, ValueError):
        return []


def save_manifest(m):
    DISABLED.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=1) + "\n")


def disable(ids, project=None):
    items = {i["id"]: i for i in scan(project)}
    manifest, rc = load_manifest(), 0
    for iid in ids:
        i = items.get(iid)
        if not i:
            print(f"{iid}: not found in the current scan", file=sys.stderr)
            rc = 1
            continue
        when = time.strftime("%Y-%m-%d %H:%M")
        if i["kind"] == "claude-plugin":
            if i.get("scope") == "synced":
                print(f"{iid}: {how_to_disable(i)}")
                continue
            r = subprocess.run(["claude", "plugin", "disable", i["name"], "--scope", i.get("scope", "user")],
                               capture_output=True, text=True)
            if r.returncode:
                print(f"{iid}: claude plugin disable failed: {(r.stderr or r.stdout).strip()[:300]}", file=sys.stderr)
                rc = 1
                continue
            manifest.append({"id": iid, "kind": "claude-plugin", "plugin": i["name"], "scope": i.get("scope", "user"),
                             "date": when})
            print(f"{iid}: disabled (restart Claude Code to apply)")
        else:
            src = Path(i["path"])
            dest = DISABLED / i["agent"] / src.name
            if dest.exists() or dest.is_symlink():
                dest = dest.with_name(f"{src.name}.{time.strftime('%Y%m%d%H%M%S')}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))  # a symlinked skill moves as the link itself
            manifest.append({"id": iid, "kind": "skill-folder", "from": str(src), "to": str(dest), "date": when})
            print(f"{iid}: moved to {dest}")
        save_manifest(manifest)
    return rc


def restore(ids, everything):
    manifest, keep, rc = load_manifest(), [], 0
    for e in manifest:
        if not everything and e["id"] not in ids:
            keep.append(e)
            continue
        if e["kind"] == "claude-plugin":
            r = subprocess.run(["claude", "plugin", "enable", e["plugin"], "--scope", e["scope"]],
                               capture_output=True, text=True)
            ok = r.returncode == 0
        else:
            ok = not Path(e["from"]).exists() and Path(e["to"]).exists()
            if ok:
                Path(e["from"]).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(e["to"], e["from"])
        print(f"{e['id']}: {'restored' if ok else 'could not restore, left as is'}")
        if not ok:
            keep.append(e)
            rc = 1
    save_manifest(keep)
    return rc


def review(project):
    items = scan(project)
    print_table(items)
    actionable = [i for i in items if not (i["kind"] == "claude-plugin" and i.get("scope") == "synced")]
    if not actionable:
        return 0
    if not sys.stdin.isatty():
        print("\nNot an interactive terminal: nothing changed. Run `conflicts.py review` later.")
        return 0
    pre = [i["n"] for i in actionable if i["selected"]]
    ask = f"\nDisable the suggested ones {pre}? Enter = yes, n = none, or type numbers (e.g. 1 3): " if pre else \
          "\nType the numbers to disable (e.g. 1 3), or Enter for none: "
    answer = input(ask).strip().lower()
    if answer in ("n", "no", "none") or (not answer and not pre):
        print("Nothing changed.")
        return 0
    chosen = pre if not answer or answer in ("y", "yes") else [int(x) for x in re.findall(r"\d+", answer)]
    ids = [i["id"] for i in actionable if i["n"] in chosen]
    return disable(ids, project) if ids else 0


def notice():
    """SessionStart hook: tell the user once per prosewise version about conflicts. Never changes anything."""
    try:
        version = json.loads((Path(__file__).resolve().parents[3] / ".claude-plugin" / "plugin.json").read_text())["version"]
    except (OSError, ValueError, KeyError):
        version = os.environ.get("PROSEWISE_VERSION", "")
    marker = STATE / "conflicts-notice-shown"
    try:
        if marker.read_text().strip() == version:
            return 0
    except OSError:
        pass
    try:
        items = [i for i in scan(os.getcwd()) if i["status"] == "conflict"]
    except Exception:  # a hook must never break session start
        return 0
    STATE.mkdir(parents=True, exist_ok=True)
    marker.write_text(version + "\n")
    if items:
        names = ", ".join(i["name"] for i in items[:5]) + (" ..." if len(items) > 5 else "")
        msg = (f"prosewise: {len(items)} other writing skill(s) or plugin(s) are active ({names}). Their rules are "
               "already inside prosewise, and two rulebooks conflict. Run /prosewise:prosewise-conflicts to review "
               "them; nothing is disabled without your agreement.")
        print(json.dumps({"systemMessage": msg}))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["scan", "review", "disable", "restore", "list-disabled", "notice"])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--project", default=None, help="also scan this project's skill folders")
    ap.add_argument("--all", action="store_true", help="restore everything")
    a = ap.parse_args()
    if a.command == "scan":
        items = scan(a.project)
        if a.json:
            print(json.dumps(items, indent=1))
        else:
            print_table(items)
        return 0
    if a.command == "review":
        return review(a.project)
    if a.command == "disable":
        if not a.ids:
            ap.error("give the ids to disable (see scan)")
        return disable(a.ids, a.project)
    if a.command == "restore":
        if not a.ids and not a.all:
            ap.error("give ids or --all")
        return restore(a.ids, a.all)
    if a.command == "list-disabled":
        m = load_manifest()
        print(json.dumps(m, indent=1) if a.json else "\n".join(f"{e['id']}  ({e['date']})" for e in m) or "Nothing disabled.")
        return 0
    return notice()


if __name__ == "__main__":
    sys.exit(main())
