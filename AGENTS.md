# prosewise: writing rules for agents without skill support

Agents that load Agent Skills should use `skills/prosewise/SKILL.md` instead. This file is a compact fallback for
agents that only read AGENTS.md (or a rules file). The full rule catalogue is in `skills/prosewise/references/`.

When you write or edit any English prose, code comment, commit message or PR description:

## Never
- Invent facts, numbers, names, quotes, sources, experiences or opinions. Ask, or leave a visible `[gap: ...]`.
- Change meaning, certainty, code, commands, paths, URLs, identifiers, numbers or quotations while editing prose.
- Leave chatbot wrapping in deliverables: greetings, praise of the question, "I hope this helps", offers of more help,
  knowledge-cutoff notes, leaked tool tokens or placeholders.
- Use em dashes (—). If a dash between clauses is the best mark, use a spaced hyphen ( - ), at most 2 per 1,000
  words and 1 per paragraph. Do not swap removed dashes for a new habit of colons, semicolons or parentheses.
- Decorate headings, bullets, comments or commits with emoji.
- Cite a source you have not checked, or write "experts say" without naming them.

## Avoid (act on clusters, not single words)
- AI-favoured vocabulary where a plain word works: delve, tapestry, pivotal, testament, underscore, landscape,
  realm, seamless, robust, leverage, foster, elevate. Say "is" instead of "serves as".
- Inflated significance, hype, brochure adjectives, corporate boilerplate. State the concrete effect.
- Signposting ("it's worth noting", "importantly"), hollow intensifiers, stacked hedges.
- Throat-clearing openers, teaser hooks ("The result?"), canned closers, "the future looks bright" endings.
- "Not X, but Y" framings unless the contrast is real. Padding or trimming lists to three items.
- Runs of clipped fragments, repeated sentence openers, trailing "-ing" clauses about significance.
- Bold sprinkled through prose, bold-label-colon lists, bullets for reasoning, document headers in short replies.

## Prefer
- Lead with the point or decision. One name per thing. Concrete nouns and numbers. Active voice when the actor
  matters. Sentence length that follows the content.
- Fix the vague claim behind a removed phrase; do not swap in a synonym. If a rule makes a sentence worse, skip it.

## Code comments
Say why, not what. Delete comments that restate code, narrate the change or decorate. Keep directives, licence
headers, public API docs and anything you are unsure about. Match the file's comment style. Never change behaviour.

## Commit messages
Follow the repository's convention (contributing docs, commitlint config, recent `git log`). With none, write a plain
imperative subject (about 50 characters, never over 72), a blank line, then what changed and why. Mark breaking
changes. No self-praise ("enhances", "robust"), no emoji, no chat formatting. Every statement must match the diff.
