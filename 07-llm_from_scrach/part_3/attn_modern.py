"""
现代因果自注意力机制实现

本模块实现了支持多种现代优化技术的自注意力机制，包括：
- GQA (Grouped Query Attention): 通过减少 K/V 头数量来降低内存和计算开销
- RoPE (Rotary Position Embedding): 旋转位置编码，更好地处理位置信息
- KV Cache: 缓存机制，加速自回归生成
- Sliding Window Attention: 滑动窗口注意力，限制注意力范围
- Attention Sink: 注意力汇聚机制，保留部分历史信息
"""

from __future__ import annotations
import math, torch
import torch.nn as nn
import torch.nn.functional as F
from rope_custom import RoPECache, apply_rope_single
from kv_cache import KVCache  # your existing class

class CausalSelfAttentionModern(nn.Module):
    """
    现代因果自注意力模块
    
    实现了支持 GQA、RoPE、KV Cache、滑动窗口等优化技术的自注意力机制。
    适用于训练和推理场景，特别优化了自回归生成性能。
    """
    def __init__(self, n_embd: int, n_head: int, dropout: float = 0.0,
                 rope: bool = True, max_pos: int = 4096,
                 sliding_window: int | None = None, attention_sink: int = 0,
                 n_kv_head: int | None = None):
        """
        初始化现代因果自注意力模块
        
        Args:
            n_embd: 嵌入维度，即模型的特征维度
            n_head: 查询头（Q）的数量
            dropout: Dropout 概率，用于训练时的正则化
            rope: 是否使用旋转位置编码（RoPE）
            max_pos: 最大位置编码长度，用于 RoPE 缓存
            sliding_window: 滑动窗口大小，限制注意力范围。None 表示不使用滑动窗口
            attention_sink: 注意力汇聚数量，保留前 N 个 token 的注意力（用于滑动窗口）
            n_kv_head: K/V 头的数量，用于 GQA。None 时等于 n_head（标准多头注意力）
                     当 n_kv_head < n_head 时启用 GQA，减少内存和计算开销
        """
        super().__init__()
        # 确保嵌入维度能被头数整除
        assert n_embd % n_head == 0, "n_embd must be divisible by n_head"
        self.n_head = n_head
        # GQA: 如果未指定，默认使用标准多头注意力（n_kv_head = n_head）
        self.n_kv_head = n_kv_head or n_head
        # GQA 要求：查询头数必须是 K/V 头数的倍数
        assert self.n_head % self.n_kv_head == 0, "n_head must be multiple of n_kv_head (GQA grouping)"
        # 每个 K/V 头对应的 Q 头数量（GQA 分组大小）
        self.group_size = self.n_head // self.n_kv_head
        # 每个头的维度
        self.d_head = n_embd // n_head

        # 投影层：Q、K、V 分别投影（GQA 下 K/V 的维度更小）
        self.wq  = nn.Linear(n_embd, self.n_head   * self.d_head, bias=False)  # Q: (n_embd -> n_head * d_head)
        self.wk  = nn.Linear(n_embd, self.n_kv_head * self.d_head, bias=False)  # K: (n_embd -> n_kv_head * d_head)
        self.wv  = nn.Linear(n_embd, self.n_kv_head * self.d_head, bias=False)  # V: (n_embd -> n_kv_head * d_head)
        # 输出投影层
        self.proj = nn.Linear(n_embd, n_embd, bias=False)
        self.dropout = nn.Dropout(dropout)

        # RoPE 相关配置
        self.use_rope = rope
        self.rope_cache: RoPECache | None = None  # 延迟初始化，在第一次前向传播时创建
        self.max_pos = max_pos
        
        # 滑动窗口和注意力汇聚配置
        self.sliding_window = sliding_window
        self.attention_sink = attention_sink

    def _maybe_init_rope(self, device):
        """
        延迟初始化 RoPE 缓存
        
        在第一次前向传播时根据设备创建 RoPE 缓存，避免在 __init__ 时指定设备。
        
        Args:
            device: 张量所在的设备（CPU 或 CUDA）
        """
        if self.use_rope and self.rope_cache is None:
            self.rope_cache = RoPECache(self.d_head, self.max_pos, device=device)

    def forward(self, x: torch.Tensor, kv_cache: KVCache | None = None, start_pos: int = 0):
        """
        前向传播
        
        Args:
            x: 输入张量，形状为 (B, T, C)
               - B: 批次大小
               - T: 序列长度（训练时通常较大，推理时通常为 1）
               - C: 嵌入维度（n_embd）
            kv_cache: KV 缓存，用于自回归生成加速。None 表示训练模式或首次推理
            start_pos: 当前 token 的起始位置，用于 RoPE 位置编码
        
        Returns:
            y: 输出张量，形状为 (B, T, C)
            new_cache: 更新后的 KV 缓存，用于下一次前向传播
        """
        B, T, C = x.shape
        # 延迟初始化 RoPE 缓存（如果需要）
        self._maybe_init_rope(x.device)

        # 步骤 1: 线性投影得到 Q、K、V
        # Q: (B, T, C) -> (B, T, n_head * d_head) -> (B, n_head, T, d_head)
        q = self.wq(x).view(B, T, self.n_head,   self.d_head).transpose(1, 2)
        # K: (B, T, C) -> (B, T, n_kv_head * d_head) -> (B, n_kv_head, T, d_head)
        k = self.wk(x).view(B, T, self.n_kv_head, self.d_head).transpose(1, 2)
        # V: (B, T, C) -> (B, T, n_kv_head * d_head) -> (B, n_kv_head, T, d_head)
        v = self.wv(x).view(B, T, self.n_kv_head, self.d_head).transpose(1, 2)

        # 步骤 2: 应用旋转位置编码（RoPE）
        # 注意：缓存中的 K/V 已经旋转过，这里只旋转当前 token 的 Q/K
        if self.use_rope:
            # 计算当前 token 的位置索引
            pos = torch.arange(start_pos, start_pos + T, device=x.device)
            # 从缓存中获取对应位置的 cos 和 sin 值
            cos, sin = self.rope_cache.get(pos)
            # 应用 RoPE 旋转
            q = apply_rope_single(q, cos, sin)   # (B, n_head, T, d_head)
            k = apply_rope_single(k, cos, sin)   # (B, n_kv_head, T, d_head)

        # 步骤 3: 合并历史 KV 缓存（如果存在）
        # 缓存以紧凑的 n_kv_head 格式存储，而不是展开后的 n_head 格式
        if kv_cache is not None:
            # 将历史缓存与当前 K/V 拼接：沿着序列长度维度（dim=2）
            k_all = torch.cat([kv_cache.k, k], dim=2)  # (B, n_kv_head, T_past + T, d_head)
            v_all = torch.cat([kv_cache.v, v], dim=2)
        else:
            # 训练模式或首次推理：没有历史缓存
            k_all, v_all = k, v

        # 步骤 4: 应用滑动窗口和注意力汇聚
        # 滑动窗口：只保留最近的 N 个 token 的注意力
        # 注意力汇聚：保留前 M 个 token（通常用于模型稳定性）
        if self.sliding_window is not None and k_all.size(2) > (self.sliding_window + self.attention_sink):
            s = self.attention_sink
            # 保留前 s 个 token（注意力汇聚）+ 最后 sliding_window 个 token（滑动窗口）
            k_all = torch.cat([k_all[:, :, :s, :], k_all[:, :, -self.sliding_window:, :]], dim=2)
            v_all = torch.cat([v_all[:, :, :s, :], v_all[:, :, -self.sliding_window:, :]], dim=2)

        # 步骤 5: GQA 扩展 - 将 K/V 头复制以匹配 Q 头数量
        # 在 GQA 模式下，多个 Q 头共享同一个 K/V 头
        if self.n_kv_head != self.n_head:
            # 沿着头维度（dim=1）重复每个 K/V 头 group_size 次
            k_attn = k_all.repeat_interleave(self.group_size, dim=1)  # (B, n_head, T_k, d_head)
            v_attn = v_all.repeat_interleave(self.group_size, dim=1)  # (B, n_head, T_k, d_head)
        else:
            # 标准多头注意力：K/V 头数等于 Q 头数，无需扩展
            k_attn, v_attn = k_all, v_all

        # 步骤 6: 计算缩放点积注意力
        # is_causal: 训练时使用因果掩码，推理时（有缓存）不需要（因为缓存已包含历史信息）
        is_causal = kv_cache is None
        y = F.scaled_dot_product_attention(
            q, k_attn, v_attn,
            attn_mask=None,  # 使用 is_causal 参数处理因果掩码
            dropout_p=self.dropout.p if self.training else 0.0,  # 训练时应用 dropout
            is_causal=is_causal
        )  # 输出形状: (B, n_head, T, d_head)

        # 步骤 7: 重塑并投影输出
        # 将多头输出合并: (B, n_head, T, d_head) -> (B, T, n_head * d_head) = (B, T, C)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        # 输出投影
        y = self.proj(y)

        # 步骤 8: 更新 KV 缓存
        # 注意：缓存中存储的是紧凑的 n_kv_head 格式，而不是展开后的格式
        # 这样可以节省内存，因为展开操作在每次前向传播时重新执行
        if kv_cache is not None:
            # 将新的 K/V 追加到缓存中
            k_new = torch.cat([kv_cache.k, k], dim=2)  # (B, n_kv_head, T_total, d_head)
            v_new = torch.cat([kv_cache.v, v], dim=2)
        else:
            # 首次推理或训练：创建新的缓存
            k_new, v_new = k, v
        
        # 如果启用了滑动窗口，也需要对缓存应用限制
        # 这样缓存本身的大小也会被限制，而不仅仅是在注意力计算时
        if self.sliding_window is not None and k_new.size(2) > (self.sliding_window + self.attention_sink):
            s = self.attention_sink
            # 保留前 s 个 token（注意力汇聚）+ 最后 sliding_window 个 token（滑动窗口）
            k_new = torch.cat([k_new[:, :, :s, :], k_new[:, :, -self.sliding_window:, :]], dim=2)
            v_new = torch.cat([v_new[:, :, :s, :], v_new[:, :, -self.sliding_window:, :]], dim=2)
        
        # 创建新的缓存对象并返回
        new_cache = KVCache(k_new, v_new)
        return y, new_cache


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("测试 CausalSelfAttentionModern")
    print("=" * 60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}\n")
    
    # 测试参数
    B, T, n_embd, n_head = 2, 10, 64, 4
    d_head = n_embd // n_head
    
    # ========== 测试 1: 形状变化详细展示 ==========
    print("测试 1: 形状变化详细展示（标准多头注意力 + RoPE）")
    print("-" * 60)
    attn = CausalSelfAttentionModern(n_embd=n_embd, n_head=n_head, rope=True).to(device)
    x = torch.randn(B, T, n_embd, device=device)
    
    print(f"输入 x: {x.shape}")
    print(f"  - 批次大小 (B): {B}")
    print(f"  - 序列长度 (T): {T}")
    print(f"  - 嵌入维度 (C): {n_embd}")
    print(f"  - 注意力头数 (H): {n_head}")
    print(f"  - 每个头维度 (d_head): {d_head}")
    
    # 手动展示各步骤的形状变化
    with torch.no_grad():
        # 步骤 1: 线性投影
        q = attn.wq(x)  # (B, T, n_head * d_head)
        k = attn.wk(x)  # (B, T, n_kv_head * d_head)
        v = attn.wv(x)  # (B, T, n_kv_head * d_head)
        print(f"\n步骤 1 - 线性投影后:")
        print(f"  Q: {q.shape} -> view -> (B, T, {n_head}, {d_head}) -> transpose -> (B, {n_head}, T, {d_head})")
        print(f"  K: {k.shape} -> view -> (B, T, {n_head}, {d_head}) -> transpose -> (B, {n_head}, T, {d_head})")
        print(f"  V: {v.shape} -> view -> (B, T, {n_head}, {d_head}) -> transpose -> (B, {n_head}, T, {d_head})")
        
        q = q.view(B, T, n_head, d_head).transpose(1, 2)  # (B, n_head, T, d_head)
        k = k.view(B, T, n_head, d_head).transpose(1, 2)  # (B, n_head, T, d_head)
        v = v.view(B, T, n_head, d_head).transpose(1, 2)  # (B, n_head, T, d_head)
        print(f"  重塑后 Q: {q.shape}, K: {k.shape}, V: {v.shape}")
        
        # 步骤 2: RoPE（如果有）
        if attn.use_rope:
            pos = torch.arange(0, T, device=x.device)
            cos, sin = attn.rope_cache.get(pos) if attn.rope_cache else (None, None)
            if cos is not None:
                print(f"\n步骤 2 - RoPE 应用:")
                print(f"  位置索引: {pos.shape}")
                print(f"  cos/sin: {cos.shape}, {sin.shape}")
                print(f"  Q/K 应用 RoPE 后形状不变: {q.shape}")
        
        # 步骤 3-6: 注意力计算
        print(f"\n步骤 3-6 - 注意力计算:")
        print(f"  Q: {q.shape}")
        print(f"  K: {k.shape}")
        print(f"  V: {v.shape}")
        print(f"  scaled_dot_product_attention(Q, K, V) -> (B, {n_head}, T, {d_head})")
        
        # 实际前向传播
        y, cache = attn(x)
        print(f"\n步骤 7 - 输出投影:")
        print(f"  注意力输出: (B, {n_head}, T, {d_head})")
        print(f"  transpose + view -> (B, T, {n_embd})")
        print(f"  最终输出 y: {y.shape}")
        print(f"  KV Cache - K: {cache.k.shape}, V: {cache.v.shape}")
    
    print("\n" + "=" * 60 + "\n")
    
    # ========== 测试 2: GQA 形状变化展示 ==========
    print("测试 2: GQA 形状变化详细展示")
    print("-" * 60)
    n_kv_head = 2  # K/V 头数减半
    group_size = n_head // n_kv_head
    attn_gqa = CausalSelfAttentionModern(
        n_embd=n_embd, n_head=n_head, n_kv_head=n_kv_head, rope=True
    ).to(device)
    x = torch.randn(B, T, n_embd, device=device)
    
    print(f"GQA 配置:")
    print(f"  Q 头数 (n_head): {n_head}")
    print(f"  K/V 头数 (n_kv_head): {n_kv_head}")
    print(f"  分组大小 (group_size): {group_size}")
    print(f"  每个 K/V 头对应 {group_size} 个 Q 头")
    
    with torch.no_grad():
        # 展示投影后的形状
        q_proj = attn_gqa.wq(x)  # (B, T, n_head * d_head)
        k_proj = attn_gqa.wk(x)  # (B, T, n_kv_head * d_head)
        v_proj = attn_gqa.wv(x)  # (B, T, n_kv_head * d_head)
        
        print(f"\n步骤 1 - 线性投影后:")
        print(f"  Q: {q_proj.shape} -> (B, {n_head}, T, {d_head})")
        print(f"  K: {k_proj.shape} -> (B, {n_kv_head}, T, {d_head})  [更小！]")
        print(f"  V: {v_proj.shape} -> (B, {n_kv_head}, T, {d_head})  [更小！]")
        
        # 实际前向传播
        y, cache = attn_gqa(x)
        
        print(f"\n步骤 5 - GQA 扩展:")
        print(f"  K/V 缓存（紧凑格式）: K {cache.k.shape}, V {cache.v.shape}")
        print(f"  repeat_interleave(K, group_size={group_size}, dim=1)")
        print(f"  -> K 扩展后: (B, {n_head}, T, {d_head})")
        print(f"  -> V 扩展后: (B, {n_head}, T, {d_head})")
        print(f"\n最终输出 y: {y.shape}")
        print(f"KV Cache（紧凑格式，节省内存）: K {cache.k.shape}, V {cache.v.shape}")
    
    print("\n" + "=" * 60 + "\n")
    
    # ========== 测试 3: KV Cache 一致性测试 ==========
    print("测试 3: KV Cache 一致性测试（分步生成 vs 一次性生成）")
    print("-" * 60)
    attn = CausalSelfAttentionModern(n_embd=n_embd, n_head=n_head, rope=True).to(device)
    x_full = torch.randn(B, T, n_embd, device=device)
    
    print(f"一次性生成（训练模式）:")
    print(f"  输入: {x_full.shape}")
    # 一次性生成（训练模式）
    y_full, _ = attn(x_full, kv_cache=None)
    print(f"  输出: {y_full.shape}\n")
    
    # 分步生成（推理模式，使用 KV Cache）
    print(f"分步生成（推理模式，使用 KV Cache）:")
    attn.eval()  # 确保 dropout 关闭
    kv_cache = None
    y_stepwise = []
    for t in range(T):
        x_t = x_full[:, t:t+1, :]  # (B, 1, C)
        y_t, kv_cache = attn(x_t, kv_cache=kv_cache, start_pos=t)
        y_stepwise.append(y_t)
        if t < 3:  # 只打印前几步的形状变化
            print(f"  步骤 {t}: 输入 {x_t.shape} -> 输出 {y_t.shape}, 缓存 K {kv_cache.k.shape}, V {kv_cache.v.shape}")
        elif t == 3:
            print(f"  ...")
    y_stepwise = torch.cat(y_stepwise, dim=1)  # (B, T, C)
    print(f"  最终拼接输出: {y_stepwise.shape}")
    print(f"  最终缓存: K {kv_cache.k.shape}, V {kv_cache.v.shape}")
    
    # 检查输出是否一致（允许小的数值误差）
    max_diff = (y_full - y_stepwise).abs().max().item()
    print(f"\n  ✓ 最大差异: {max_diff:.2e}")
    assert max_diff < 1e-5, f"分步生成与一次性生成结果不一致: {max_diff}"
    print("  ✓ 分步生成与一次性生成结果一致\n")
    
    # ========== 测试 4: 滑动窗口测试 ==========
    print("测试 4: 滑动窗口 + 注意力汇聚测试")
    print("-" * 60)
    window_size = 4
    sink_size = 2
    attn_sw = CausalSelfAttentionModern(
        n_embd=n_embd, n_head=n_head, 
        sliding_window=window_size, attention_sink=sink_size, rope=True
    ).to(device)
    attn_sw.eval()
    
    # 生成一个较长的序列
    T_long = 20
    x_long = torch.randn(B, T_long, n_embd, device=device)
    
    print(f"配置: 窗口大小={window_size}, 注意力汇聚={sink_size}, 最大缓存长度={window_size + sink_size}")
    print(f"输入序列长度: {T_long}")
    print(f"\n分步生成过程中的缓存形状变化:")
    
    # 分步生成，检查缓存大小是否被限制
    kv_cache = None
    for t in range(T_long):
        x_t = x_long[:, t:t+1, :]
        cache_before = kv_cache.k.size(2) if kv_cache is not None else 0
        y_t, kv_cache = attn_sw(x_t, kv_cache=kv_cache, start_pos=t)
        cache_after = kv_cache.k.size(2)
        
        # 打印关键步骤的形状变化
        if t < 5 or t >= T_long - 3 or cache_after != cache_before + 1:
            status = "✓" if cache_after <= window_size + sink_size else "⚠"
            print(f"  步骤 {t:2d}: 输入 {x_t.shape} -> 缓存长度 {cache_before} -> {cache_after} {status}")
        
        # 检查缓存长度是否被正确限制
        actual_len = kv_cache.k.size(2)
        expected_max = window_size + sink_size
        # 缓存长度应该始终不超过限制
        assert actual_len <= expected_max, \
            f"滑动窗口未生效: 缓存长度 {actual_len} > {expected_max} (步骤 {t})"
        # 当序列长度足够长时，缓存应该被限制在最大值
        if t >= expected_max - 1:  # 从 expected_max-1 开始就应该达到最大值
            assert actual_len == expected_max, \
                f"缓存长度应为 {expected_max}，但实际为 {actual_len} (步骤 {t})"
    
    print(f"\n最终状态:")
    print(f"  ✓ 最终缓存长度: {kv_cache.k.size(2)} (应 <= {window_size + sink_size})")
    print(f"  ✓ 缓存形状: K {kv_cache.k.shape}, V {kv_cache.v.shape}")
    print(f"  ✓ 滑动窗口正常工作\n")
    
   
    # ========== 测试 5: 不同序列长度测试 ==========
    print("测试 5: 不同序列长度测试")
    print("-" * 60)
    attn = CausalSelfAttentionModern(n_embd=n_embd, n_head=n_head, rope=True).to(device)
    print("测试不同序列长度的形状:")
    for seq_len in [1, 5, 10, 20]:
        x = torch.randn(B, seq_len, n_embd, device=device)
        y, cache = attn(x)
        assert y.shape == (B, seq_len, n_embd), f"序列长度 {seq_len} 测试失败"
        assert cache.k.size(2) == seq_len, f"缓存长度不匹配: {cache.k.size(2)} != {seq_len}"
        print(f"  序列长度 {seq_len:2d}: 输入 {x.shape} -> 输出 {y.shape}, 缓存 K {cache.k.shape}, V {cache.v.shape}")
    print("  ✓ 所有序列长度均正常工作\n")
    
    print("=" * 60)
    print("所有测试通过！✅")
    print("=" * 60)
