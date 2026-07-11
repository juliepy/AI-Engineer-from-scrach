import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/validate.py"],
        cwd=".",
        check=False,
    )

    if result.returncode == 0:
        print("stop hook: validation passed, safe to finish")
        return 0

    print("stop hook: validation failed, continue fixing before stop")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
