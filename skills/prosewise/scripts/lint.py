#!/usr/bin/env python3
"""prosewise linter: deterministic candidate finder for English prose.

Counts lexical triggers from lint_rules.json, em dashes and clause dashes against the dash budget, bold and emoji
density, and sentence-length spread (information only). Output is a list of CANDIDATES for the skill's gate step,
not verdicts and never proof of AI authorship. Standard library only.

Usage:
  python3 lint.py [--sensitivity strict|standard|relaxed] [--json] [FILE ...]   (stdin when no FILE)
Exit code: 0 no hard findings, 1 hard findings present, 2 usage error.
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

DATA = Path(__file__).with_name("lint_rules.json")

# Rules whose triggers are too common, structural or scope-specific to count blindly in prose. The model handles them.
SKIP_RULES = {
    "STR-047", "STR-048", "LEX-013", "LEX-017", "LEX-023", "STR-024", "STR-031", "STR-044", "STR-004",
    "PUN-001", "PUN-002", "PUN-005", "PUN-008", "PUN-010", "PUN-011", "PUN-014", "PUN-015",
    "FMT-001", "FMT-011", "FMT-013", "FMT-015", "FMT-016", "FMT-019", "FMT-020",
    "SCO-005", "PRC-013", "TON-015", "LEX-016", "LEX-044", "STR-055",
}
SKIP_PREFIXES = ("CMT-", "CMS-")  # comment and commit rules need code or git context
PLACEHOLDER = re.compile(r"(\.\.\.|\(.*\)|\[adj\]|\[x\]|\bx\b|\by\b|\bz\b)")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")


def strip_protected(text):
    """Remove code, inline code, URLs and block quotes: rules never fire inside them (INT-004, PRC-018)."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))
    # quoted spans are mentions, not uses (PRC-018)
    text = re.sub(r'"[^"\n]{1,120}"|“[^”\n]{1,120}”', " ", text)
    return text


def words(text):
    return re.findall(r"[A-Za-z][A-Za-z'’-]*", text)


def sentences(text):
    flat = re.sub(r"\s+", " ", re.sub(r"^\s*([-*+]|\d+\.)\s+", "", text, flags=re.M))
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(])", flat) if len(words(s)) >= 3]


def trigger_regex(trigger):
    esc = re.escape(trigger.lower()).replace(r"\ ", r"\s+")
    left = r"\b" if trigger[:1].isalnum() else ""
    right = r"\b" if trigger[-1:].isalnum() else ""
    return re.compile(left + esc + right)


def lexical_findings(text, rules, sensitivity, modules):
    low = text.lower()
    out = []
    for r in rules:
        if r["id"] in SKIP_RULES or r["id"].startswith(SKIP_PREFIXES):
            continue
        if r.get("module") and r["module"] not in modules:
            continue
        hits = []
        for t in r["wordlist"]:
            if PLACEHOLDER.search(t) and not t.startswith("[") and "<!--" not in t:
                continue
            hits += [(m.start(), m.end(), t) for m in trigger_regex(t).finditer(low)]
        # overlapping triggers ("hope this helps" inside "i hope this helps") count once, longest wins
        kept, taken = [], []
        for start, end, t in sorted(hits, key=lambda h: (h[0], -(h[1] - h[0]))):
            if any(start < e and end > b for b, e in taken):
                continue
            taken.append((start, end))
            kept.append((start, t))
        hits = kept
        if not hits:
            continue
        n = len(hits)
        single = r["strength"] == "hard" or r.get("threshold") == "single"
        need = {"strict": 1, "standard": 1 if single else (3 if r["strength"] == "soft" else 2),
                "relaxed": 1 if r["strength"] == "hard" else 3}[sensitivity]
        if sensitivity == "relaxed" and r["strength"] == "soft":
            continue
        if n < need:
            continue
        sample = sorted({t for _, t in hits})[:6]
        out.append({"rule": r["id"], "pattern": r["pattern"], "strength": r["strength"], "count": n,
                    "triggers": sample})
    return out


def dash_findings(text, n_words, sensitivity):
    out = []
    em = text.count("—")
    if em:
        out.append({"rule": "PUN-001", "pattern": "em dash", "strength": "hard", "count": em,
                    "note": "no em dashes; use a period, comma, colon, or a spaced hyphen ( - ) within the dash budget"})
    clause = re.findall(r"(?<=[A-Za-z,)])[ \t]+(?:-|–|--)[ \t]+(?=[A-Za-z(])", text) + re.findall(r"[A-Za-z]--[A-Za-z]", text)
    doubles = len(re.findall(r"(?<=\w)\s*--\s*(?=\w)", text))
    per_k = 1000 * len(clause) / max(n_words, 1)
    worst_para = max((len(re.findall(r"(?<=[A-Za-z,)])[ \t]+(?:-|–|--)[ \t]+(?=[A-Za-z(])", p))
                      for p in re.split(r"\n\s*\n", text)), default=0)
    limit = {"strict": len(clause) > 0,
             "standard": per_k > 2 or worst_para > 1,
             "relaxed": len(clause) >= 5 or per_k > 4}[sensitivity]
    if limit or doubles:
        out.append({"rule": "PUN-002", "pattern": "clause dashes over budget", "strength": "default",
                    "count": len(clause), "per_1000_words": round(per_k, 1), "max_per_paragraph": worst_para,
                    "note": "budget: 2 per 1,000 words, 1 per paragraph, no double hyphens"})
    return out


def format_findings(text, n_words, sensitivity):
    out = []
    bold = re.findall(r"\*\*[^*\n]+\*\*", text)
    label_items = re.findall(r"^\s*(?:[-*+]|\d+\.)\s+\*\*[^*]+\*\*\s*:", text, flags=re.M)
    allowed = {"strict": 0, "standard": max(1, n_words // 300), "relaxed": max(3, n_words // 100)}[sensitivity]
    if len(bold) > allowed:
        out.append({"rule": "FMT-001", "pattern": "bold overuse", "strength": "default", "count": len(bold)})
    if len(label_items) >= (2 if sensitivity != "relaxed" else 4):
        out.append({"rule": "FMT-002", "pattern": "bold label + colon list", "strength": "default",
                    "count": len(label_items)})
    deco = [l for l in text.splitlines() if re.match(r"^\s*(#+|[-*+]|\d+\.)\s", l) and EMOJI.search(l)]
    if deco:
        out.append({"rule": "FMT-012", "pattern": "decorative emoji", "strength": "hard", "count": len(deco)})
    arrows = len(re.findall(r"\S\s*(?:->|→|=>)\s*\S+\s*(?:->|→|=>)\s*\S+\s*(?:->|→|=>)", text))
    if arrows:
        out.append({"rule": "FMT-013", "pattern": "arrow chains", "strength": "default", "count": arrows})
    return out


def info(text):
    lens = [len(words(s)) for s in sentences(text)]
    if len(lens) < 4:
        return {"sentences": len(lens)}
    return {"sentences": len(lens), "mean_words": round(statistics.mean(lens), 1),
            "sd_words": round(statistics.pstdev(lens), 1),
            "note": "information only (D-06): never act on the spread alone"}


def lint(text, sensitivity="standard", modules=()):
    rules = json.loads(DATA.read_text())["rules"]
    clean = strip_protected(text)
    n = len(words(clean))
    findings = dash_findings(clean, n, sensitivity) + format_findings(clean, n, sensitivity) \
        + lexical_findings(clean, rules, sensitivity, set(modules))
    order = {"hard": 0, "default": 1, "soft": 2}
    findings.sort(key=lambda f: (order[f["strength"]], -f["count"]))
    return {"words": n, "sensitivity": sensitivity, "findings": findings, "info": info(clean),
            "disclaimer": "candidates for review, not verdicts; signals of writing quality, not proof of AI authorship"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--sensitivity", choices=["strict", "standard", "relaxed"], default="standard")
    ap.add_argument("--module", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    texts = [(f, Path(f).read_text(encoding="utf-8")) for f in a.files] or [("<stdin>", sys.stdin.read())]
    hard = False
    results = []
    for name, text in texts:
        res = lint(text, a.sensitivity, a.module)
        res["file"] = name
        hard |= any(f["strength"] == "hard" for f in res["findings"])
        results.append(res)
    if a.json:
        json.dump(results if len(results) > 1 else results[0], sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        for res in results:
            print(f"# {res['file']}: {res['words']} words, sensitivity {res['sensitivity']}, "
                  f"{len(res['findings'])} candidate(s)")
            for f in res["findings"]:
                extra = f" [{', '.join(f['triggers'])}]" if f.get("triggers") else ""
                note = f" ({f['note']})" if f.get("note") else ""
                print(f"- {f['rule']} {f['strength']} x{f['count']}: {f['pattern']}{extra}{note}")
            i = res["info"]
            if "sd_words" in i:
                print(f"- info: {i['sentences']} sentences, mean {i['mean_words']} words, sd {i['sd_words']} (information only)")
            print(f"  {res['disclaimer']}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
