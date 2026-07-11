"""
KV Cache 教学模块

核心问题（自回归生成）：
  每生成 1 个新 token，都要做一次 attention。
  旧 token 的 K、V 不会变 → 缓存起来，下次只算新 token 的 K、V 并拼接。

教学主线
--------
1. demo_kv_cache()        — 无 cache vs 有 cache，逐步打印 shape
2. demo_attention_step()  — 单步 attention：新 Q  attend 全部历史 K/V
3. KVCache                — 数据结构（attn_modern.py 使用）
4. RollingKV              — 进阶：滑动窗口 + attention sink（3.5/3.6 节）

维度约定（与 attn_modern.py 一致）
--------------------------------
  k, v: (B, H, T, D)
    B = batch
    H = num heads（或 n_kv_head）
    T = 序列长度（cache 里已缓存的 token 数）
    D = head dimension
"""
from __future__ import annotations

import torch
from dataclasses import dataclass


# =============================================================================
# 教学演示 1：为什么需要 KV Cache
# =============================================================================

def demo_kv_cache() -> None:
    """逐步演示：无 cache 重复计算 vs 有 cache 只追加新 token。"""
    print("=" * 60)
    print("教学演示 1：为什么需要 KV Cache")
    print("=" * 60)
    print("场景：自回归生成，每步输入 1 个新 token，序列逐渐变长\n")

    max_steps = 4
    D = 4

    # --- 无 Cache ---
    print("[无 Cache] 每步对「当前全部 token」重新算 K、V")
    print("-" * 40)
    total_kv_compute = 0
    for step in range(1, max_steps + 1):
        T = step
        kv_ops = T  # 本步要算 T 个 token 的 K 和 V
        total_kv_compute += kv_ops
        print(f"  Step {step}: 序列长 T={T}")
        print(f"           计算 K,V: ({T} 个 token) x 2")
        print(f"           attention 分数矩阵: ({T} x {T})\n")
    print(f"  累计 K/V 计算 token 数: {total_kv_compute}  (1+2+3+4=10)\n")

    # --- 有 Cache ---
    print("[有 Cache] 每步只算「新 token」的 K、V，历史从 cache 读取")
    print("-" * 40)
    total_kv_compute_cached = 0
    cache_T = 0
    for step in range(1, max_steps + 1):
        total_kv_compute_cached += 1
        print(f"  Step {step}: 新 token 1 个")
        print(f"           计算 K_new,V_new: shape (1,1,1,{D})")
        print(f"           cache 中已有 T={cache_T}")
        print(f"           concat 后 K_all,V_all: T={cache_T + 1}\n")
        cache_T += 1
    print(f"  累计 K/V 计算 token 数: {total_kv_compute_cached}  (每步只算 1 个)")
    print(f"\n  节省: {total_kv_compute} -> {total_kv_compute_cached} "
          f"({total_kv_compute // total_kv_compute_cached}x 量级，序列越长差距越大)")


# =============================================================================
# 教学演示 2：用真实张量走一遍 append
# =============================================================================

def demo_attention_step() -> None:
    """用固定张量演示：3 步生成，每步 append K/V 并做 attention。"""
    print("\n" + "=" * 60)
    print("教学演示 2：逐步 append K/V（单头，便于手算）")
    print("=" * 60)

    torch.manual_seed(42)
    B, H, D = 1, 1, 4

    # 3 个 token 的「嵌入」（真实模型里来自 tok_emb）
    token_embeds = [
        torch.tensor([[0.1, 0.2, 0.3, 0.4]], dtype=torch.float32),
        torch.tensor([[0.5, 0.4, 0.3, 0.2]], dtype=torch.float32),
        torch.tensor([[0.0, 0.1, 0.0, 0.1]], dtype=torch.float32),
    ]

    # 简化的投影矩阵（真实模型里是 nn.Linear）
    Wk = torch.eye(D)
    Wv = torch.eye(D) * 0.5

    cache: KVCache | None = None

    for step, x_t in enumerate(token_embeds):
        # x_t: (1, D) -> (B, 1, D)
        x_t = x_t.unsqueeze(0)
        print(f"\n--- Step {step + 1}: 新 token embedding shape {tuple(x_t.shape)} ---")

        # 只投影「当前这一步」的 token → K_new, V_new
        k_new = (x_t @ Wk).unsqueeze(1)   # (B, H=1, T=1, D)
        v_new = (x_t @ Wv).unsqueeze(1)
        print(f"  K_new: {tuple(k_new.shape)}   V_new: {tuple(v_new.shape)}")

        if cache is None:
            k_all, v_all = k_new, v_new
            print("  cache: 空（首 token，直接作为 cache）")
        else:
            k_all = torch.cat([cache.k, k_new], dim=2)
            v_all = torch.cat([cache.v, v_new], dim=2)
            print(f"  cache: 已有 T={cache.T}，concat 后 T={cache.T + 1}")

        cache = KVCache(k=k_all, v=v_all)
        print(f"  K_all: {tuple(k_all.shape)}   (历史 + 新 token 全部 K)")

        # 当前 token 的 Q attend 所有历史 K/V
        q = k_new  # 简化：Q 投影同 K
        scores = (q @ k_all.transpose(-2, -1)) / (D ** 0.5)  # (B,H,1,T)
        weights = torch.softmax(scores, dim=-1)
        out = weights @ v_all  # (B,H,1,D)
        print(f"  attention: Q(1) @ K_all({k_all.size(2)}) -> weights {tuple(weights.shape)}")
        print(f"  output:    {tuple(out.shape)}")

    print("\n要点：Step 3 时只算了 1 个新 K/V，但 attention 仍覆盖全部 3 个 token。")


# =============================================================================
# 数据结构（供 attn_modern.py 使用）
# =============================================================================

@dataclass
class KVCache:
    """存储已算好的 K、V，推理时逐步 append 新 token 的 K/V。"""
    k: torch.Tensor  # (B, H, T, D)
    v: torch.Tensor  # (B, H, T, D)

    @property
    def T(self) -> int:
        return self.k.size(2)


# =============================================================================
# 进阶：滚动窗口 KV Cache（3.5 / 3.6 节）
# =============================================================================

class RollingKV:
    """
    限制 cache 长度：保留前 sink 个 token + 最后 window 个 token。

    普通 KVCache 无限增长；长序列推理时用这个控制显存。
    """

    def __init__(self, window: int, sink: int = 0):
        self.window = window
        self.sink = sink
        self.k: torch.Tensor | None = None
        self.v: torch.Tensor | None = None

    def step(self, k_new: torch.Tensor, v_new: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if self.k is None:
            self.k, self.v = k_new, v_new
        else:
            self.k = torch.cat([self.k, k_new], dim=2)
            self.v = torch.cat([self.v, v_new], dim=2)

        limit = self.window + self.sink
        if self.k.size(2) > limit:
            sink_k = self.k[:, :, : self.sink, :]
            sink_v = self.v[:, :, : self.sink, :]
            tail_k = self.k[:, :, -self.window :, :]
            tail_v = self.v[:, :, -self.window :, :]
            self.k = torch.cat([sink_k, tail_k], dim=2)
            self.v = torch.cat([sink_v, tail_v], dim=2)

        return self.k, self.v


def demo_rolling_window() -> None:
    """演示滑动窗口：超过 window+sink 后丢弃中间 token。"""
    print("\n" + "=" * 60)
    print("教学演示 3：RollingKV（滑动窗口，进阶）")
    print("=" * 60)
    print("window=3, sink=1 → 最多保留 4 个 token（1 个 sink + 3 个最近）\n")

    B, H, D = 1, 1, 4
    rolling = RollingKV(window=3, sink=1)

    for i in range(6):
        k_new = torch.full((B, H, 1, D), float(i + 1))
        v_new = k_new.clone()
        k, v = rolling.step(k_new, v_new)
        print(f"  追加 token #{i + 1}  ->  cache 长度 T={k.size(2)}")


# =============================================================================
# 单元测试（pytest / CI 用，课堂可跳过）
# =============================================================================

def test_kvcache_basic() -> None:
    B, H, T, D = 2, 4, 5, 16
    k = torch.randn(B, H, T, D)
    v = torch.randn(B, H, T, D)
    cache = KVCache(k=k, v=v)
    assert cache.T == T
    assert cache.k.shape == (B, H, T, D)


def test_rollingkv_window() -> None:
    B, H, D = 1, 2, 8
    rolling = RollingKV(window=3, sink=0)
    for _ in range(6):
        k_new = torch.randn(B, H, 1, D)
        v_new = torch.randn(B, H, 1, D)
        k, v = rolling.step(k_new, v_new)
    assert k.size(2) == 3


def test_rollingkv_with_sink() -> None:
    B, H, D = 1, 2, 8
    rolling = RollingKV(window=3, sink=2)
    for _ in range(8):
        k_new = torch.randn(B, H, 1, D)
        v_new = torch.randn(B, H, 1, D)
        k, v = rolling.step(k_new, v_new)
    assert k.size(2) == 5  # sink(2) + window(3)


if __name__ == "__main__":
    demo_kv_cache()
    demo_attention_step()
    demo_rolling_window()

    print("\n" + "=" * 60)
    print("单元测试")
    print("=" * 60)
    test_kvcache_basic()
    test_rollingkv_window()
    test_rollingkv_with_sink()
    print("全部通过")
