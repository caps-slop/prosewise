# Configuration

prosewise works with no configuration. Settings are read in this order, later ones winning:

1. built-in defaults
2. `~/.config/prosewise/config.yaml` (user, applies everywhere)
3. `.prosewise.yaml` at the project root (project, can be committed)
4. what the user says in the request ("audit only", "strict", "in my voice")

Unknown keys are ignored. Integrity rules cannot be disabled.

```yaml
# .prosewise.yaml or ~/.config/prosewise/config.yaml
sensitivity: standard        # strict | standard | relaxed
show_rule_ids: false         # true adds rule ids to audit findings and reports
modules: []                  # e.g. [marketing-social, genres, ste-strict, academic-econ]
voice:
  profile: ~/.config/prosewise/profiles/me   # folder written by prosewise-voice; omit for no voice
  apply: on-request          # on-request (only when asked "in my voice") | always
disable: []                  # rule ids to skip, e.g. [FMT-006, PUN-009]; hard integrity rules are never skipped
extra_triggers:              # project-specific words to treat as lexical tells
  - leverage synergies
commits:
  convention: auto           # auto (detect) | conventional | plain | <free text describing the house rule>
  subject_max: 72
comments:
  when_unsure: keep          # keep | delete
```

## Notes
- `voice.apply: always` makes every write and rewrite use the profile. Keep the default `on-request` if the
  profile is tuned to one genre (say, email) and you also write docs or commits.
- `commits.convention: auto` follows CMS-001: contributing docs and commitlint config first, then recent history,
  then a plain imperative subject. Set it explicitly to stop detection.
- To keep a team's rules alongside prosewise, put them in the project file: a project rule always beats the generic
  catalogue (local convention beats house style), never the integrity rules.
