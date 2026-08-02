#!/usr/bin/env python3
"""Move a small reviewed batch from _scheduled/ into the live _posts/ folder."""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_DIR = os.path.join(ROOT, "_scheduled")
POSTS_DIR = os.path.join(ROOT, "_posts")
ORDER_PREFIX = re.compile(r"^\d{2}-")


def queued_files() -> list[str]:
    if not os.path.isdir(QUEUE_DIR):
        return []
    return sorted(
        os.path.join(QUEUE_DIR, name)
        for name in os.listdir(QUEUE_DIR)
        if name.endswith(".md") and ORDER_PREFIX.match(name)
    )


def validate_reviewed(text: str, path: str) -> None:
    problems = []
    if text.startswith("<!-- REJECTED:"):
        problems.append("still carries a rejected marker")
    if len(re.findall(r"!\[[^\]]+\]\(([^)]+)\)", text)) != 2:
        problems.append("does not contain exactly two inline images")
    if "## Frequently Asked Questions" not in text:
        problems.append("has no FAQ section")
    if "https://sulsul.app" not in text:
        problems.append("has no SULSUL CTA")
    if problems:
        raise ValueError(f"{os.path.basename(path)}: " + "; ".join(problems))


def publication_copy(text: str, published_at: str) -> str:
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        raise ValueError("missing YAML frontmatter")
    frontmatter, body = parts[1], parts[2]
    for field in ("date", "updated"):
        pattern = rf'(?m)^{field}:\s*["\']?.*?["\']?\s*$'
        replacement = f'{field}: "{published_at}"'
        if re.search(pattern, frontmatter):
            frontmatter = re.sub(pattern, replacement, frontmatter, count=1)
        else:
            frontmatter += f"\n{replacement}"
    return f"---{frontmatter}---{body}"


def release(count: int) -> list[str]:
    os.makedirs(POSTS_DIR, exist_ok=True)
    selected = queued_files()[:count]
    if not selected:
        print("No reviewed posts are waiting.")
        return []

    # Validate the whole batch before moving any file.
    drafts = []
    for source in selected:
        with open(source, encoding="utf-8") as handle:
            text = handle.read()
        validate_reviewed(text, source)
        live_name = ORDER_PREFIX.sub("", os.path.basename(source), count=1)
        destination = os.path.join(POSTS_DIR, live_name)
        if os.path.exists(destination):
            raise FileExistsError(f"Live post already exists: {live_name}")
        drafts.append((source, destination, text))

    published_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    released = []
    for source, destination, text in drafts:
        temp = destination + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            handle.write(publication_copy(text, published_at))
        os.replace(temp, destination)
        os.remove(source)
        released.append(os.path.basename(destination))
        print(f"Released: {os.path.relpath(destination, ROOT)}")
    return released


def main() -> int:
    parser = argparse.ArgumentParser(description="Release reviewed blog posts in order")
    parser.add_argument("--count", type=int, default=2)
    args = parser.parse_args()
    if args.count < 1 or args.count > 3:
        parser.error("--count must be between 1 and 3")

    try:
        released = release(args.count)
    except (OSError, ValueError) as exc:
        print(f"Release stopped: {exc}", file=sys.stderr)
        return 1

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            if released:
                summary.write("### 오늘 공개된 검수 완료 글\n\n")
                summary.writelines(f"- `{name}`\n" for name in released)
            else:
                summary.write("검수 완료 대기 글이 없습니다.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
