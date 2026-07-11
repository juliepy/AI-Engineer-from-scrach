import subprocess
import sys


def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> int:
    code = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    if code != 0:
        print("validate: FAIL")
        return code

    print("validate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
