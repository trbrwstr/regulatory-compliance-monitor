from __future__ import annotations

import difflib
import hashlib
import re


def normalize_content(content: str) -> str:
    """Normalize whitespace while preserving deterministic line boundaries."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in content.splitlines()]
    return "\n".join(line for line in lines if line)


def content_hash(content: str) -> str:
    return hashlib.sha256(normalize_content(content).encode("utf-8")).hexdigest()


def deterministic_diff(previous: str, current: str) -> dict:
    previous_lines = normalize_content(previous).splitlines()
    current_lines = normalize_content(current).splitlines()
    changes = list(difflib.unified_diff(previous_lines, current_lines, lineterm=""))
    return {
        "changed": previous_lines != current_lines,
        "previous_hash": content_hash(previous),
        "current_hash": content_hash(current),
        "unified_diff": "\n".join(changes),
        "added_lines": [line[1:] for line in changes if line.startswith("+") and not line.startswith("+++")],
        "removed_lines": [line[1:] for line in changes if line.startswith("-") and not line.startswith("---")],
    }
