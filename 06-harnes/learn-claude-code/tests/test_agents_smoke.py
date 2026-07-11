from __future__ import annotations

from pathlib import Path
import py_compile

import pytest


ROOT = Path(__file__).resolve().parents[1]
COURSE_FILES = sorted(ROOT.glob("s??_*/code.py"))
COURSE_IDS = [path.parent.name for path in COURSE_FILES]


@pytest.mark.parametrize("code_path", COURSE_FILES, ids=COURSE_IDS)
def test_course_scripts_compile(code_path: Path) -> None:
    _ = py_compile.compile(str(code_path), doraise=True)


def test_course_scripts_exist() -> None:
    assert len(COURSE_FILES) == 20, f"expected 20 course chapters, found {len(COURSE_FILES)}"
