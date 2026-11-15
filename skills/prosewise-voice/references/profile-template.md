# Profile template

Two kinds of file. `voice.md` holds what is true in every genre. `<genre>.md` holds one genre's numbers and
patterns. Every rule carries `strength: hard | soft` and `evidence: stated | n/N | inferred`. Inferred items are never hard.

## voice.md

```markdown
---
profile: <name>
version: 1
built: <YYYY-MM-DD>
owner_confirmed: true
genres: [email, doc, post]
---

## Provenance
Sources: <folders or exports>, <date range>. Items and words per genre: email 214 / 31,800; doc 9 / 12,400.
Excluded: quoted replies, signatures, automated mail, 3 sensitive threads. Not sampled: <sources>.

## Stated rules (the writer's own words, verbatim)
- "I never use exclamation marks at work."  strength: hard, evidence: stated
- "Cheers, not Best regards."  strength: hard, evidence: stated

## Cross-genre invariants
- Spelling: British (-ise).  evidence: 0 '-ize' forms in 41,000 words
- Never: "I hope this finds you well".  evidence: 0/223 items
- Does use: "to be fair" (0.6 per 1,000 words). Keep it.

## Lifted prosewise style rules
- PUN-002 dash budget: spaced hyphens at 1.1 per 1,000 words in email (within budget, no change).
- LEX-021 "that said": allowed, 0.4 per 1,000 words in docs.

## Known gaps
- Tested drafts came out longer than the median email (182 vs 96 words).
```

## <genre>.md

```markdown
---
genre: email
items: 214
words: 31800
tier: strong
---

## Measured defaults
| field | value |
|---|---|
| length (words) p25 / median / p75 / p90 | 41 / 96 / 170 / 260 |
| sentence words median / sd | 14 / 7.9 |
| paragraph words median | 38 |
| contractions per 1,000 words | 21 |
| per 1,000 words: em dash, spaced hyphen, semicolon, colon, parenthesis, !, ? | 0 / 1.1 / 0.2 / 2.4 / 3.0 / 0 / 4.1 |
| share with bullets / emoji / links | 0.12 / 0 / 0.31 |

## Patterns
- Opens with the request in the first sentence (31/50). "Could you send ..."  strength: soft
- Greeting: "Hi <first name>," (88%); none in replies within a thread.
- Closes: "Cheers," + first name (93%).
- Declines: thanks, gives the reason in one clause, offers one alternative.

## Lexicon
- Favours: "sorted", "shout if", "happy to".
- Never (n=214): "delve", "circle back", "reach out".

## By situation
| situation | length | opener | closer | notes |
|---|---|---|---|---|
| quick reply | < 40 words | none | "Cheers" | no greeting |
| request to a stranger | ~120 words | context in one line | thanks + name | |

## Formatting
| field | value |
|---|---|
| heading depth / median heading words | 2 / 4 |
| bold per 1,000 words; on words or whole sentences | 1.2; words |
| share of one-line paragraphs | 0.08 |
| section separators | none |

## Sources and uncertainty
- Cites primary data and links it inline; uses one concrete example per claim.
- Hedges with "probably" and "I think", once per claim, never stacked.

## Imperfections to keep
- Lowercase "ok". Occasional one-line paragraphs.
```

## Long-form genres only: structure templates

```markdown
## Structure templates
### <content type, e.g. technical post>
- When used: explaining a fix after an incident.
- Opening: the symptom in one sentence (12-20 words), no scene-setting.
- First turn: the wrong first hypothesis, by the end of paragraph two.
- Body: chronological, one section per hypothesis, each ending with the evidence that ruled it out.
- Transitions: a question in a short paragraph, about once per section.
- Close: what changed in the code and how to detect it next time; no moral.
- Reader expectation: an engineer who will act on it. Allowed variations: skip the wrong hypothesis when there was none.
```
