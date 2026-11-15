#!/usr/bin/env python3
"""Measure a writer's habits from a local corpus, one genre at a time.

Reads .txt, .md and .eml files under each genre folder, never sends anything anywhere, and prints JSON with
summary statistics only (no document text beyond short opener/closer fragments). The prosewise-voice skill turns
this into a profile. Standard library only.

Usage:
  python3 voice_stats.py --genre email PATH [PATH ...] [--out stats-email.json]
  python3 voice_stats.py --root ~/writing [--out-dir PROFILE/stats]   # one genre per subfolder
"""
import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

LINT = Path(__file__).resolve().parents[2] / "prosewise" / "scripts"
EXTS = {".txt", ".md", ".eml", ".markdown"}
STOP = set("""a an the and or but if of to in on at for with by from as is are was were be been being it its this that
these those i you he she we they me him her us them my your our their not no so do does did have has had will would can
could should may might must just than then there here what which who whom when where why how all any some more most""".split())
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]")


def clean(text, path):
    if path.suffix == ".eml":
        text = text.split("\n\n", 1)[-1]                      # drop headers
    text = re.split(r"\n-- ?\n|\nOn .{5,80} wrote:\n|\n-----Original Message-----", text)[0]  # signature, quoted reply
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    return text.strip()


def words(t):
    return re.findall(r"[A-Za-z][A-Za-z'’]*", t)


def sentences(t):
    flat = re.sub(r"\s+", " ", t)
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(])", flat) if words(s)]


def q(values, p):
    if not values:
        return None
    v = sorted(values)
    return v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]


def per_k(count, n):
    return round(1000 * count / max(n, 1), 2)


def first_line(t):
    return next((l.strip() for l in t.splitlines() if l.strip()), "")


def last_line(t):
    return next((l.strip() for l in reversed(t.splitlines()) if l.strip()), "")


def fragment(line, n=4):
    return " ".join(words(line)[:n]).lower()


def formatting(docs, n):
    """Markdown habits: heading depth and length, bold density and target, one-line paragraphs, separators."""
    heads = [l for d in docs for l in d.splitlines() if re.match(r"^#{1,6}\s", l)]
    bolds = [b for d in docs for b in re.findall(r"\*\*([^*\n]+)\*\*", d)]
    paras = [p for d in docs for p in re.split(r"\n\s*\n", d) if p.strip()]
    return {
        "heading_depth_max": max((len(h) - len(h.lstrip("#")) for h in heads), default=0),
        "heading_words_median": q([len(words(h)) for h in heads], .5),
        "bold_per_1000": per_k(len(bolds), n),
        "bold_on_sentences_share": round(sum(len(words(b)) >= 6 for b in bolds) / max(len(bolds), 1), 2),
        "one_line_paragraph_share": round(sum(len(p.strip().splitlines()) == 1 and len(words(p)) <= 25
                                              for p in paras) / max(len(paras), 1), 2),
        "separators": sum(len(re.findall(r"^\s*(---|\*\*\*|___)\s*$", d, re.M)) for d in docs),
    }


def measure(files):
    docs = []
    for f in files:
        try:
            docs.append(clean(f.read_text(encoding="utf-8", errors="replace"), f))
        except OSError:
            continue
    docs = [d for d in docs if words(d)]
    allt = "\n\n".join(docs)
    n = len(words(allt))
    lens = [len(words(d)) for d in docs]
    sents = [len(words(s)) for d in docs for s in sentences(d)]
    paras = [len(words(p)) for d in docs for p in re.split(r"\n\s*\n", d) if words(p)]
    vocab = collections.Counter(w.lower() for w in words(allt)
                                if w.lower() not in STOP and len(w) > 2 and not w.lower().endswith("ly"))
    docfreq = collections.Counter(w for d in docs for w in {x.lower() for x in words(d)})
    marks = {
        "em_dash": allt.count("—"),
        "en_dash_between_words": len(re.findall(r"[A-Za-z] – [A-Za-z]", allt)),
        "spaced_hyphen": len(re.findall(r"[A-Za-z,] - [A-Za-z]", allt)),
        "semicolon": allt.count(";"),
        "colon": len(re.findall(r":\s", allt)),
        "parenthesis": allt.count("("),
        "exclamation": allt.count("!"),
        "question": allt.count("?"),
        "ellipsis": allt.count("...") + allt.count("…"),
    }
    stats = {
        "items": len(docs),
        "words": n,
        "tier": "too-thin" if len(docs) < 3 or n < 500 else ("thin" if len(docs) < 20 else ("ok" if len(docs) < 200 else "strong")),
        "length_words": {"p25": q(lens, .25), "median": q(lens, .5), "p75": q(lens, .75), "p90": q(lens, .9)},
        "sentence_words": {"median": q(sents, .5), "mean": round(statistics.mean(sents), 1) if sents else None,
                           "sd": round(statistics.pstdev(sents), 1) if len(sents) > 1 else None},
        "paragraph_words_median": q(paras, .5),
        "contractions_per_1000": per_k(len(re.findall(r"[A-Za-z]['’](s|t|re|ve|ll|d|m)\b", allt)), n),
        "marks_per_1000": {k: per_k(v, n) for k, v in marks.items()},
        "share_with_bullets": round(sum(bool(re.search(r"^\s*([-*+]|\d+\.)\s", d, re.M)) for d in docs) / max(len(docs), 1), 2),
        "share_with_emoji": round(sum(bool(EMOJI.search(d)) for d in docs) / max(len(docs), 1), 2),
        "share_with_links": round(sum("http" in d for d in docs) / max(len(docs), 1), 2),
        "openers": collections.Counter(fragment(first_line(d), 2) for d in docs).most_common(8),
        "closers": collections.Counter(fragment(last_line(d), 3) for d in docs).most_common(8),
        # a voice marker is spread across many items; a word concentrated in a few items is topic vocabulary
        "top_words": [{"word": w, "count": c, "items": docfreq[w],
                       "kind": "topic" if docfreq[w] < max(3, 0.2 * len(docs)) else "voice-candidate"}
                      for w, c in vocab.most_common(40)],
        "short_sentence_share": round(sum(l <= 8 for l in sents) / max(len(sents), 1), 2),
        "long_sentence_share": round(sum(l >= 30 for l in sents) / max(len(sents), 1), 2),
        "formatting": formatting(docs, n),
    }
    try:  # which prosewise tells this writer actually uses, and how often: evidence for lifting a style ban
        sys.path.insert(0, str(LINT))
        import lint
        res = lint.lint(allt, "strict")
        stats["prosewise_triggers"] = [
            {"rule": f["rule"], "pattern": f["pattern"], "count": f["count"], "per_1000": per_k(f["count"], n),
             "triggers": f.get("triggers", [])} for f in res["findings"]]
    except Exception as e:  # the linter is optional; stats stay useful without it
        stats["prosewise_triggers_error"] = str(e)[:200]
    return stats


def collect(paths):
    files = []
    for p in map(Path, paths):
        files += [f for f in p.rglob("*") if f.suffix.lower() in EXTS] if p.is_dir() else [p]
    return sorted(set(files))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--genre")
    ap.add_argument("--out")
    ap.add_argument("--root", help="folder whose subfolders are genres (email/, posts/, docs/ ...)")
    ap.add_argument("--out-dir", help="with --root: write <genre>.json here")
    a = ap.parse_args()
    if a.root:
        genres = sorted(d for d in Path(a.root).expanduser().iterdir() if d.is_dir() and not d.name.startswith("."))
        if not genres:
            ap.error(f"{a.root} has no subfolders; pass the files with --genre instead")
        result = {}
        for d in genres:
            result[d.name] = {"genre": d.name, **measure(collect([d]))}
            if a.out_dir:
                Path(a.out_dir).expanduser().mkdir(parents=True, exist_ok=True)
                (Path(a.out_dir).expanduser() / f"{d.name}.json").write_text(
                    json.dumps(result[d.name], indent=2, ensure_ascii=False) + "\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    if not a.genre or not a.paths:
        ap.error("pass --root FOLDER, or --genre NAME with one or more paths")
    stats = {"genre": a.genre, **measure(collect(a.paths))}
    out = json.dumps(stats, indent=2, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
