#!/usr/bin/env python3
"""Block internal notes and prices from reaching anything a visitor can load.

The blog keeps two kinds of text in one repository: copy written for readers,
and rules written to keep the post generator honest. The rules are phrased as
prohibitions ("no invented $299 anchors"), so when one leaks into a page it
reads as the brand defending itself against an accusation nobody made. This
checker fails the build when that happens.

Run directly, or via `npm run check:copy`.
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Everything a browser or an AI crawler can fetch.
SCAN_DIRS = ["src", "public", "_posts"]
SCAN_EXTS = {".tsx", ".ts", ".jsx", ".js", ".md", ".mdx", ".txt", ".html"}
SKIP_PARTS = {"node_modules", ".next", ".git", "_rejected", "out", "build"}
# Machine-readable briefs may address an AI summariser directly.
AI_BRIEF_FILES = {"public/llms.txt", "public/llms-full.txt"}

RULES = [
    (
        "price",
        r"\$\s?\d[\d,.]*|\b\d{1,3}\.99\b|priceCurrency",
        "A price. Prices live only on sulsul.app so there is one source of truth.",
    ),
    (
        "denial",
        r"\bno fake\b|\bno invented\b|strikethrough|original.{0,12}anchor",
        "Denies wrongdoing nobody alleged. Say what SULSUL is, not what it is not accused of.",
    ),
    (
        "discount",
        r"%\s?off\b|\bearly bird\b|\blimited time\b|\bmoney[- ]back\b"
        r"|\brefund guarantee\b|\bsatisfaction guarantee\b|\bfree trial\b",
        "An offer or guarantee SULSUL does not make.",
    ),
    (
        "competitor",
        r"\bDuolingo\b|\bTTMIK\b|\bSejong\b|\bBabbel\b|\bAnki\b",
        "Names a competitor. Internal positioning, not customer copy.",
    ),
    (
        "instruction",
        r"\(facts only\)|\bhard ban|\bbanned phrase|\bdo not invent\b|\bnever the hero\b"
        r"|\bnever sell\b|\bguardrail|\bsystem prompt\b|\bas an AI\b|\bAI-generated\b",
        "An instruction meant for the writing model, not a sentence for a reader.",
    ),
    (
        "slop",
        r"in today's fast-paced world|\bdelve\b|\bdive into\b|unlock your full potential"
        r"|game-changer|embark on a journey|the ultimate guide to|look no further"
        r"|\bin conclusion\b",
        "Filler phrasing that reads as machine-written.",
    ),
    (
        "overclaim",
        r"fluent in \d+ days?|master korean in|guaranteed to|\bnetflix\b"
        r"|\bgovernment-approved\b",
        "A promise or affiliation SULSUL cannot support.",
    ),
]

# Narrow, deliberate exceptions. Each needs a reason.
ALLOW = [
    (
        "price",
        r"\$30[\u2013\-]50",
        "Comparison to a private tutor's hourly rate, not a SULSUL price.",
    ),
    (
        "instruction",
        r"do not (?:quote|state|imply)",
        "Directed at AI summarisers inside the machine-readable brief.",
    ),
]


def scannable(path):
    rel_parts = set(os.path.relpath(path, ROOT).split(os.sep))
    if rel_parts & SKIP_PARTS:
        return False
    return os.path.splitext(path)[1] in SCAN_EXTS


def files():
    found = []
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in SKIP_PARTS]
            for name in filenames:
                full = os.path.join(dirpath, name)
                if scannable(full):
                    found.append(full)
    return sorted(found)


def allowed(rule_id, line, rel):
    for allow_rule, pattern, _ in ALLOW:
        if allow_rule != rule_id:
            continue
        if allow_rule == "instruction" and rel not in AI_BRIEF_FILES:
            continue
        if re.search(pattern, line, re.I):
            return True
    return False


def check_text(text, rel):
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        for rule_id, pattern, why in RULES:
            hit = re.search(pattern, line, re.I)
            if hit and not allowed(rule_id, line, rel):
                problems.append((n, rule_id, hit.group(0).strip(), why))
    return problems


def main():
    targets = sys.argv[1:] or files()
    failures = []
    for path in targets:
        rel = os.path.relpath(path, ROOT)
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        for n, rule_id, snippet, why in check_text(text, rel):
            failures.append((rel, n, rule_id, snippet, why))

    if not failures:
        print("check_public_copy: %d files scanned, nothing to fix." % len(targets))
        return 0

    print("check_public_copy: text that must not reach a reader\n")
    for rel, n, rule_id, snippet, why in failures:
        print("  %s:%d  [%s]  %r" % (rel, n, rule_id, snippet))
        print("      %s\n" % why)
    print("%d problem(s). Fix the copy, or add a reasoned entry to ALLOW." % len(failures))
    return 1


if __name__ == "__main__":
    sys.exit(main())
