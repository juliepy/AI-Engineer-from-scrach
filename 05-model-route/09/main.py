# =============================================================================
#  金丝雀 vs 蓝绿部署
# =============================================================================

import sys

from deploy import BlueGreenRouter, describe_canary, pick_canary_version

sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    print("=== 金丝雀分流（10% → v2）===")
    print(f"  {describe_canary()}")
    counts = {"v1-stable": 0, "v2-canary": 0}
    for i in range(100):
        v = pick_canary_version(f"user-{i}", canary_pct=10)
        counts[v] += 1
    print(f"  100 用户分布: {counts}")
    print()

    print("=== 蓝绿切换 ===")
    print(f"  {BlueGreenRouter.describe()}")
    bg = BlueGreenRouter(active="blue")
    print(f"  当前活跃: {bg.route()}")
    bg.switch("green")
    print(f"  切换后:   {bg.route()}")
