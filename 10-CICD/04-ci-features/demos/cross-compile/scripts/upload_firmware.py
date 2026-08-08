"""Upload cross-built firmware under out/firmware/ to the demo HTTP repo."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="out/firmware")
    p.add_argument("--base-url", default="http://127.0.0.1:8765")
    args = p.parse_args()

    fw_dir = Path(args.dir)
    bins = sorted(fw_dir.glob("fw-*.bin"))
    if not bins:
        print("No fw-*.bin under", fw_dir, file=sys.stderr)
        return 1

    uploaded = []
    for path in bins:
        url = f"{args.base_url.rstrip('/')}/{path.name}"
        data = path.read_bytes()
        req = urllib.request.Request(url, data=data, method="PUT")
        req.add_header("Content-Type", "application/octet-stream")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(resp.read().decode().strip())
        except urllib.error.URLError as exc:
            print(f"Upload failed: {exc}", file=sys.stderr)
            print("Start server first: python scripts/http_repo_server.py", file=sys.stderr)
            return 1
        uploaded.append({"name": path.name, "url": url, "bytes": len(data)})

    meta = fw_dir / "build-meta.json"
    if meta.exists():
        murl = f"{args.base_url.rstrip('/')}/{meta.name}"
        req = urllib.request.Request(murl, data=meta.read_bytes(), method="PUT")
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(resp.read().decode().strip())

    manifest = {"artifacts": uploaded, "install_hint": "device pulls URL and flashes; CI PC does not run the binary"}
    print(json.dumps(manifest, indent=2))
    print()
    print("========== 板端安装测试（本 Demo 只指到这一步） ==========")
    print("测试架 / 板子：curl -O", uploaded[-1]["url"])
    print("然后按产品流程刷机、冒烟；失败回写 CI / 测试报告。")
    print("PC / Runner 职责到「交叉编译 + 上传制品库」为止。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
