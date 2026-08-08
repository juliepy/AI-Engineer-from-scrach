"""Force LF line endings on demos/*.sh (Windows editors often rewrite CRLF)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in sorted(HERE.glob("*.sh")):
    data = p.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    p.write_bytes(data.encode("utf-8"))
    left = b"\r" in p.read_bytes()
    print(f"LF {p.name} CR_left={left}")
