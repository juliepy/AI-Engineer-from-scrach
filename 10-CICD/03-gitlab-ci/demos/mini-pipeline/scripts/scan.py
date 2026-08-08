"""Simulate static analysis / quality gate (SonarQube stand-in).

No Sonar server required. Scans app/ for a few teaching rules and writes
artifacts/scan-report.json — same role as a 'scan' stage in the textbook pipeline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
OUT = ROOT / "artifacts"
REPORT = OUT / "scan-report.json"

# Teaching rules (not a real Sonar engine)
RULES = [
    ("no-eval", re.compile(r"\beval\s*\("), "error", "Avoid eval()"),
    ("no-exec", re.compile(r"\bexec\s*\("), "error", "Avoid exec()"),
    ("bare-except", re.compile(r"except\s*:"), "warning", "Avoid bare except"),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    findings: list[dict] = []

    for path in sorted(APP.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule_id, pattern, severity, message in RULES:
                if pattern.search(line):
                    findings.append(
                        {
                            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                            "line": lineno,
                            "rule": rule_id,
                            "severity": severity,
                            "message": message,
                            "snippet": line.strip(),
                        }
                    )

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    report = {
        "tool": "mini-scan (SonarQube stand-in)",
        "status": "failed" if errors else "passed",
        "files_scanned": len(list(APP.rglob("*.py"))),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
        "quality_gate": "errors must be 0",
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"[scan] files={report['files_scanned']} errors={len(errors)} warnings={len(warnings)}")
    print(f"[scan] wrote {REPORT}")
    if errors:
        for item in errors:
            print(f"  ERROR {item['file']}:{item['line']} {item['rule']}: {item['message']}")
        print("[scan] quality gate FAILED")
        return 1

    print("[scan] quality gate PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
