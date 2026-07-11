"""Misc helpers.

Brownfield smell: this module hand-rolls things a utility library already does
(chunking, dedupe, plucking). It exists to be a "why do we have two ways to do
this?" moment in the workshop. Leave it.
"""
import re
from typing import Any, Iterable


def chunk(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def uniq(items: Iterable) -> list:
    seen = []
    for it in items:
        if it not in seen:
            seen.append(it)
    return seen


def pluck(rows: list[dict], key: str) -> list[Any]:
    out = []
    for r in rows:
        out.append(r.get(key))
    return out


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
