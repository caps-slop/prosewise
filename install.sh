#!/usr/bin/env sh
# Install the prosewise skills into one or more agents' skill folders, without node.
#
#   ./install.sh                 install for Claude Code and every agent that reads ~/.agents/skills (Codex, Cursor,
#                                Gemini CLI, Copilot, OpenCode, Cline, Amp, Warp, Zed and others)
#   ./install.sh --agent claude  only Claude Code (~/.claude/skills)
#   ./install.sh --agent agents  only ~/.agents/skills
#   ./install.sh --dir PATH      any other skills folder (e.g. ~/.gemini/skills, ~/.windsurf/skills)
#   ./install.sh --link          symlink instead of copying, so a git pull updates the installed skills
#   ./install.sh --uninstall     remove the prosewise skills from the chosen folders
#   ./install.sh --no-scan       skip the check for other writing skills at the end
#
# After installing, the script looks for other writing skills and plugins that conflict with prosewise and asks
# which to disable (reversibly). Nothing is disabled without a yes. Run it again any time with
#   python3 skills/prosewise-conflicts/scripts/conflicts.py review
#
# Alternatives: `/plugin marketplace add caps-slop/prosewise` in Claude Code, or
# `npx skills add caps-slop/prosewise` for ~70 agents.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
targets=""
mode=copy
action=install
scan=yes

while [ $# -gt 0 ]; do
  case "$1" in
    --agent)
      case "$2" in
        claude) targets="$targets $HOME/.claude/skills" ;;
        agents|codex) targets="$targets $HOME/.agents/skills" ;;
        *) echo "unknown agent: $2 (use --dir for other folders)" >&2; exit 2 ;;
      esac
      shift 2 ;;
    --dir) targets="$targets $2"; shift 2 ;;
    --link) mode=link; shift ;;
    --uninstall) action=uninstall; shift ;;
    --no-scan) scan=no; shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[ -n "$targets" ] || targets="$HOME/.claude/skills $HOME/.agents/skills"

for dir in $targets; do
  for skill in prosewise prosewise-voice prosewise-conflicts; do
    dest="$dir/$skill"
    if [ "$action" = uninstall ]; then
      rm -rf "$dest" && echo "removed $dest"
      continue
    fi
    mkdir -p "$dir"
    rm -rf "$dest"
    if [ "$mode" = link ]; then
      ln -s "$here/skills/$skill" "$dest"
    else
      cp -R "$here/skills/$skill" "$dest"
    fi
    echo "installed $skill -> $dest ($mode)"
  done
done

if [ "$action" = install ] && [ "$scan" = yes ]; then
  if command -v python3 >/dev/null 2>&1; then
    echo
    python3 "$here/skills/prosewise-conflicts/scripts/conflicts.py" review --project "$PWD" || true
  else
    echo "python3 not found: skipped the check for conflicting writing skills" >&2
  fi
fi
