#!/usr/bin/env python3
"""Fix two issues left by uz-orthography-fix.py:

  1. HTML attribute quotes (class="…", href="…") were curly-converted
     and must be restored to straight quotes.
  2. Inside fenced code blocks the apostrophe substitutions did not run,
     so Uzbek prose-in-fences keeps wrong glyphs (qo'llab → qoʻllab,
     to'plami → toʻplami, etc.). Apply apostrophe fixes inside fences
     while leaving straight " untouched (mermaid uses them as syntax).
"""

import re
import sys
from pathlib import Path

OKINA = "ʻ"
HAMZA = "ʼ"
LDQUO = "“"
RDQUO = "”"

CODE_FENCE_RE = re.compile(r"^(\s*)```")
HTML_TAG_RE = re.compile(r"<[^<>\n]+>")


def fix_apostrophes(text: str) -> str:
    text = text.replace("o'", "o" + OKINA)
    text = text.replace("O'", "O" + OKINA)
    text = text.replace("g'", "g" + OKINA)
    text = text.replace("G'", "G" + OKINA)
    text = re.sub(r"(?<=[A-Za-zʻ])'(?=[A-Za-z])", HAMZA, text)
    return text


def restore_html_attr_quotes(line: str) -> str:
    def fix(m):
        return m.group(0).replace(LDQUO, '"').replace(RDQUO, '"')
    return HTML_TAG_RE.sub(fix, line)


def transform(content: str) -> str:
    out = []
    in_fence = False
    for line in content.splitlines(keepends=True):
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(fix_apostrophes(line))
        else:
            out.append(restore_html_attr_quotes(line))
    return "".join(out)


def main():
    if len(sys.argv) < 2:
        print("usage: uz-orthography-cleanup.py <file> [<file> ...]", file=sys.stderr)
        sys.exit(2)
    for arg in sys.argv[1:]:
        p = Path(arg)
        original = p.read_text(encoding="utf-8")
        fixed = transform(original)
        if fixed != original:
            p.write_text(fixed, encoding="utf-8")
            print(f"cleaned: {p}")
        else:
            print(f"unchanged: {p}")


if __name__ == "__main__":
    main()
