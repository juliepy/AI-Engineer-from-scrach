#!/usr/bin/env python3
"""Apply Uzbek Latin orthography fixes to translated markdown files.

Rules:
  - o' -> oʻ, O' -> Oʻ, g' -> gʻ, G' -> Gʻ  (modifier letter turned comma U+02BB)
  - All other word-internal `'` -> ʼ            (modifier letter apostrophe U+02BC)
  - "..." -> “...”                              (curly double quotes, paired)
  - shablon -> andoza (case-preserving)

Code fences (```), inline code (`...`), and URLs are skipped.
"""

import re
import sys
from pathlib import Path

OKINA = "ʻ"      # ʻ — for oʻ / gʻ
HAMZA = "ʼ"      # ʼ — for maʼruza / sunʼiy / eʼlon
LDQUO = "“"      # “
RDQUO = "”"      # ”


def fix_apostrophes(text: str) -> str:
    text = text.replace("o'", "o" + OKINA)
    text = text.replace("O'", "O" + OKINA)
    text = text.replace("g'", "g" + OKINA)
    text = text.replace("G'", "G" + OKINA)
    text = re.sub(r"(?<=[A-Za-zʻ])'(?=[A-Za-z])", HAMZA, text)
    return text


def fix_double_quotes(text: str) -> str:
    """Replace pairs of straight " with “ ” alternately, line-aware."""
    out = []
    open_q = True
    for ch in text:
        if ch == '"':
            out.append(LDQUO if open_q else RDQUO)
            open_q = not open_q
        else:
            out.append(ch)
            if ch == "\n":
                open_q = True
    return "".join(out)


def fix_shablon(text: str) -> str:
    text = re.sub(r"\bShablon", "Andoza", text)
    text = re.sub(r"\bshablon", "andoza", text)
    return text


def fix_common_typos(text: str) -> str:
    # qaer* → qayer*
    text = re.sub(r"\bqaer(da|ga|dan)?\b", lambda m: "qayer" + (m.group(1) or ""), text)
    text = re.sub(r"\bQaer(da|ga|dan)?\b", lambda m: "Qayer" + (m.group(1) or ""), text)
    # senariy → ssenariy (Russian-borrowed, double s in Uzbek Latin)
    text = re.sub(r"\bsenariy", "ssenariy", text)
    text = re.sub(r"\bSenariy", "Ssenariy", text)
    # English loanwords ending in 'g' + suffix: ʻ → ʼ
    # `bug'`, `tag'`, `log'`, `flag'`, `slug'`, `debug'`, `blog'` should use suffix ʼ,
    # not the Uzbek `gʻ` letter combination.
    for stem in ("bug", "tag", "log", "flag", "slug", "debug", "blog", "ping", "config"):
        text = re.sub(stem + "ʻ", stem + "ʼ", text)
        text = re.sub(stem.capitalize() + "ʻ", stem.capitalize() + "ʼ", text)
    return text


CODE_FENCE_RE = re.compile(r"^(\s*)```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
URL_RE = re.compile(r"https?://\S+")
LINK_PATH_RE = re.compile(r"\]\([^)]+\)")


def protect(text: str):
    placeholders = []

    def stash(m):
        placeholders.append(m.group(0))
        return f"\x00PH{len(placeholders) - 1}\x00"

    text = INLINE_CODE_RE.sub(stash, text)
    text = URL_RE.sub(stash, text)
    text = LINK_PATH_RE.sub(stash, text)
    return text, placeholders


def restore(text: str, placeholders):
    # Iterate in reverse so a nested placeholder (e.g. LINK_PATH containing a
    # URL placeholder) is restored before its inner PH0 reference would be
    # consumed by a parallel restoration elsewhere in the line.
    for i in range(len(placeholders) - 1, -1, -1):
        text = text.replace(f"\x00PH{i}\x00", placeholders[i])
    return text


def transform(content: str) -> str:
    out_lines = []
    in_fence = False
    for line in content.splitlines(keepends=True):
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        protected, phs = protect(line)
        protected = fix_apostrophes(protected)
        protected = fix_double_quotes(protected)
        protected = fix_shablon(protected)
        protected = fix_common_typos(protected)
        out_lines.append(restore(protected, phs))
    return "".join(out_lines)


def main():
    if len(sys.argv) < 2:
        print("usage: uz-orthography-fix.py <file> [<file> ...]", file=sys.stderr)
        sys.exit(2)
    for arg in sys.argv[1:]:
        p = Path(arg)
        original = p.read_text(encoding="utf-8")
        fixed = transform(original)
        if fixed != original:
            p.write_text(fixed, encoding="utf-8")
            print(f"fixed: {p}")
        else:
            print(f"unchanged: {p}")


if __name__ == "__main__":
    main()
