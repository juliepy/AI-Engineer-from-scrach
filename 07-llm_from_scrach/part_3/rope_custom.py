"""
RoPE (Rotary Position Embedding) 自定义实现

RoPE 是一种旋转位置编码方法，通过将位置信息编码为旋转矩阵来增强 Transformer 模型的位置感知能力。
本模块实现了 RoPE 的缓存机制和应用函数。
"""

from __future__ import annotations
import torch
import math


class RoPECache:
    """
    RoPE 缓存类：预计算并缓存不同位置的 cos 和 sin 值
    
    为了高效计算 RoPE，我们预先计算所有可能位置的 cos 和 sin 值并缓存起来。
    当需要的位置超出当前缓存范围时，会自动扩展缓存表。
    """
    
    def __init__(self, head_dim: int, max_pos: int, base: float = 10000.0, device: torch.device | None = None):
        """
        初始化 RoPE 缓存
        
        Args:
            head_dim: 注意力头的维度，必须是偶数（因为 RoPE 需要成对处理）
            max_pos: 初始缓存的最大位置数
            base: RoPE 的基础频率参数，默认为 10000.0
            device: 计算设备（CPU 或 GPU）
        """
        assert head_dim % 2 == 0, "RoPE head_dim must be even"
        self.head_dim = head_dim  # 头维度
        self.base = base  # 基础频率参数
        self.device = device  # 计算设备
        self._build(max_pos)  # 构建初始缓存表
    
    def get(self, positions: torch.Tensor):
        """
        根据位置索引获取对应的 cos 和 sin 值
        
        Args:
            positions: 位置张量，形状为 (T,) 或 (1, T)，包含需要查询的位置索引
        
        Returns:
            tuple: (cos, sin) 两个张量，形状均为 (T, D/2)
                   cos 和 sin 值用于后续的旋转操作
        """
        # 处理输入：positions 可能是 (T,) 或 (1,T) 的形状
        if positions.dim() == 2:
            positions = positions[0]  # 如果是二维，取第一行
        
        # 计算所需的最大位置索引
        need = int(positions.max().item()) + 1 if positions.numel() > 0 else 1
        
        # 如果所需位置超出当前缓存范围，则扩展缓存表
        if need > self.max_pos:
            # 扩展策略：至少扩展到所需大小，或者扩展到当前大小的 2 倍（取较大值）
            self._build(max(need, int(self.max_pos * 2)))
        
        # 从缓存表中索引对应的 cos 和 sin 值
        cos = self.cos[positions]  # (T, D/2)
        sin = self.sin[positions]
        return cos, sin
    
    def _build(self, max_pos: int):
        """
        构建或重建 cos/sin 缓存表
        
        根据 RoPE 的公式，对于每个位置 t 和每个频率维度 i，计算：
        - inv_freq[i] = 1 / (base^(2i/head_dim))
        - freq[t, i] = t * inv_freq[i]
        - cos[t, i] = cos(freq[t, i])
        - sin[t, i] = sin(freq[t, i])
        
        Args:
            max_pos: 需要缓存的最大位置数
        """
        self.max_pos = max_pos
        
        # 计算逆频率：对于每个频率维度 i (i = 0, 2, 4, ..., head_dim-2)
        # inv_freq[i] = 1 / (base^(2i/head_dim))
        inv_freq = 1.0 / (10000.0 ** (torch.arange(0, self.head_dim, 2, device=self.device).float() / self.head_dim))
        
        # 位置序列：0, 1, 2, ..., max_pos-1
        t = torch.arange(max_pos, device=self.device).float()
        
        # 计算频率矩阵：freqs[t, i] = t * inv_freq[i]
        # 形状：(max_pos, head_dim/2)
        freqs = torch.outer(t, inv_freq)
        
        # 计算并缓存 cos 和 sin 值
        self.cos = torch.cos(freqs)
        self.sin = torch.sin(freqs)


def apply_rope_single(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """
    对输入张量应用 RoPE 旋转操作
    
    RoPE 的核心思想是将位置信息编码为旋转矩阵。对于每个位置 t，我们将特征向量的
    相邻维度对 (x[2i], x[2i+1]) 视为复数 x[2i] + j*x[2i+1]，然后应用旋转：
    
        [x'[2i]  ]   [cos(θ)  -sin(θ)] [x[2i]  ]
        [x'[2i+1]] = [sin(θ)   cos(θ)] [x[2i+1]]
    
    其中 θ 是根据位置和频率维度计算的角度。
    
    Args:
        x: 输入张量，形状为 (B, H, T, D)，其中 D 必须是偶数
           B: batch size, H: 注意力头数, T: 序列长度, D: 特征维度
        cos: cos 值，形状为 (T, D/2)
        sin: sin 值，形状为 (T, D/2)
    
    Returns:
        应用 RoPE 后的输出张量，形状与输入相同 (B, H, T, D)
    """
    assert x.size(-1) % 2 == 0, "特征维度 D 必须是偶数"
    
    # 扩展 cos 和 sin 的维度以匹配输入张量：(T, D/2) -> (1, 1, T, D/2)
    # 这样可以进行广播操作
    cos = cos.unsqueeze(0).unsqueeze(0)  # (1, 1, T, D/2)
    sin = sin.unsqueeze(0).unsqueeze(0)
    
    # 将特征维度分成两部分：偶数索引和奇数索引
    # x1: 偶数索引位置的元素 (..., 0, 2, 4, ...)
    # x2: 奇数索引位置的元素 (..., 1, 3, 5, ...)
    x1 = x[..., ::2]   # 形状: (B, H, T, D/2)
    x2 = x[..., 1::2]  # 形状: (B, H, T, D/2)
    
    # 应用旋转矩阵变换：
    # xr1 = x1 * cos - x2 * sin  (旋转后的偶数位置)
    # xr2 = x1 * sin + x2 * cos  (旋转后的奇数位置)
    xr1 = x1 * cos - x2 * sin
    xr2 = x1 * sin + x2 * cos
    
    # 创建输出张量并填充旋转后的值
    out = torch.empty_like(x)
    out[..., ::2] = xr1   # 将旋转后的值放回偶数位置
    out[..., 1::2] = xr2  # 将旋转后的值放回奇数位置
    
    return out


# ==================== 测试代码 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("RoPE 功能测试")
    print("=" * 60)
    
    # 设置随机种子以便结果可复现
    torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}\n")
    
    # ========== 测试 1: RoPECache 基本功能 ==========
    print("测试 1: RoPECache 基本功能")
    print("-" * 60)
    head_dim = 64
    max_pos = 128
    rope_cache = RoPECache(head_dim=head_dim, max_pos=max_pos, device=device)
    
    # 测试获取 cos/sin 值
    positions = torch.tensor([0, 1, 2, 10, 50], device=device)
    cos, sin = rope_cache.get(positions)
    
    print(f"✓ 缓存初始化成功: max_pos={rope_cache.max_pos}, head_dim={head_dim}")
    print(f"✓ 获取 cos/sin 值: positions={positions.tolist()}")
    print(f"  - cos 形状: {cos.shape}, 期望: (5, {head_dim//2})")
    print(f"  - sin 形状: {sin.shape}, 期望: (5, {head_dim//2})")
    assert cos.shape == (5, head_dim // 2), "cos 形状不正确"
    assert sin.shape == (5, head_dim // 2), "sin 形状不正确"
    print("✓ 测试通过！\n")
    
    # ========== 测试 2: 缓存自动扩展 ==========
    print("测试 2: 缓存自动扩展功能")
    print("-" * 60)
    initial_max_pos = rope_cache.max_pos
    print(f"初始 max_pos: {initial_max_pos}")
    
    # 请求超出缓存范围的位置
    large_positions = torch.tensor([200, 300], device=device)
    cos, sin = rope_cache.get(large_positions)
    
    print(f"请求位置: {large_positions.tolist()}")
    print(f"扩展后 max_pos: {rope_cache.max_pos}")
    assert rope_cache.max_pos >= 301, "缓存未正确扩展"
    print("✓ 缓存自动扩展成功！\n")
    
    # ========== 测试 3: apply_rope_single 基本功能 ==========
    print("测试 3: apply_rope_single 基本功能")
    print("-" * 60)
    B, H, T, D = 2, 4, 8, 64
    x = torch.randn(B, H, T, D, device=device)
    
    # 获取对应位置的 cos/sin
    positions = torch.arange(T, device=device)
    cos, sin = rope_cache.get(positions)
    
    # 应用 RoPE
    x_rotated = apply_rope_single(x, cos, sin)
    
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {x_rotated.shape}")
    assert x_rotated.shape == x.shape, "输出形状应与输入相同"
    print("✓ 形状检查通过！\n")
    
    # ========== 测试 4: 旋转操作的数值特性 ==========
    print("测试 4: 旋转操作的数值特性")
    print("-" * 60)
    
    # 测试 1: 相同位置应该产生相同的旋转
    x1 = torch.randn(1, 1, 1, D, device=device)
    pos_single = torch.tensor([5], device=device)
    cos1, sin1 = rope_cache.get(pos_single)
    x1_rot1 = apply_rope_single(x1, cos1, sin1)
    x1_rot2 = apply_rope_single(x1, cos1, sin1)
    
    assert torch.allclose(x1_rot1, x1_rot2), "相同输入应产生相同输出"
    print("✓ 相同位置旋转结果一致")
    
    # 测试 2: 不同位置应该产生不同的旋转
    pos_diff = torch.tensor([10], device=device)
    cos2, sin2 = rope_cache.get(pos_diff)
    x1_rot3 = apply_rope_single(x1, cos2, sin2)
    
    assert not torch.allclose(x1_rot1, x1_rot3, atol=1e-5), "不同位置应产生不同旋转"
    print("✓ 不同位置旋转结果不同")
    
    # ========== 演示: 不同位置不同旋转的详细说明 ==========
    print("\n" + "=" * 60)
    print("演示: 不同位置不同旋转的含义")
    print("=" * 60)
    print("""
【核心概念解释】
"不同位置不同旋转" 指的是：
1. 序列中的每个位置（0, 1, 2, ...）都有自己独特的旋转角度
2. 位置越靠后，旋转角度越大
3. 这样可以让模型区分不同位置的词元，并理解相对位置关系

【数学原理】
对于位置 t，旋转角度 θ 的计算公式：
    θ[t, i] = t / (base^(2i/head_dim))
其中：
    - t: 位置索引（0, 1, 2, ...）
    - i: 频率维度索引（0, 2, 4, ..., head_dim-2）
    - base: 基础频率（通常为 10000.0）

可以看出：位置 t 越大，旋转角度 θ 也越大！
""")
    
    # 创建演示用的简单向量
    demo_cache = RoPECache(head_dim=8, max_pos=10, device=device)
    
    # 演示不同位置的旋转角度
    print("【数值演示】")
    print("-" * 60)
    positions_demo = [0, 1, 2, 5]
    demo_x = torch.tensor([[[[1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]]]], device=device)
    
    print("原始向量（前4个维度）: [1.0, 0.0, 0.0, 1.0]")
    print("（这代表一个复数对：1.0 + 0.0j 和 0.0 + 1.0j）\n")
    
    for pos in positions_demo:
        pos_tensor = torch.tensor([pos], device=device)
        cos_demo, sin_demo = demo_cache.get(pos_tensor)
        
        # 应用旋转
        demo_x_rot = apply_rope_single(demo_x, cos_demo, sin_demo)
        
        # 显示第一个频率维度（前两个元素）的旋转结果
        rotated_pair = demo_x_rot[0, 0, 0, :2].cpu().numpy()
        angle = math.atan2(sin_demo[0, 0].item(), cos_demo[0, 0].item()) * 180 / math.pi
        
        print(f"位置 {pos:2d}:")
        print(f"  - 旋转角度: {angle:7.2f}°")
        print(f"  - cos值: {cos_demo[0, 0].item():7.4f}, sin值: {sin_demo[0, 0].item():7.4f}")
        print(f"  - 旋转后向量（前2维）: [{rotated_pair[0]:6.3f}, {rotated_pair[1]:6.3f}]")
        print()
    
    print("【关键观察】")
    print("-" * 60)
    print("1. 每个位置都有不同的 cos/sin 值（不同的旋转角度）")
    print("2. 位置越大，旋转角度越大")
    print("3. 相同的输入向量，在不同位置会被旋转到不同的方向")
    print("4. 这样，模型可以通过旋转后的向量来识别词元的位置信息")
    print()
    
    # 演示相对位置关系
    print("【相对位置关系】")
    print("-" * 60)
    print("RoPE 的巧妙之处：两个词元之间的相对位置关系会编码在它们的旋转中")
    print("例如：位置 5 和位置 7 之间的相对距离是 2")
    print("这个相对距离信息会体现在它们旋转后的向量之间的角度差中")
    print()
    
    pos_a, pos_b = 5, 7
    cos_a, sin_a = demo_cache.get(torch.tensor([pos_a], device=device))
    cos_b, sin_b = demo_cache.get(torch.tensor([pos_b], device=device))
    
    angle_a = math.atan2(sin_a[0, 0].item(), cos_a[0, 0].item()) * 180 / math.pi
    angle_b = math.atan2(sin_b[0, 0].item(), cos_b[0, 0].item()) * 180 / math.pi
    angle_diff = angle_b - angle_a
    
    print(f"位置 {pos_a} 的旋转角度: {angle_a:.2f}°")
    print(f"位置 {pos_b} 的旋转角度: {angle_b:.2f}°")
    print(f"角度差（相对位置）: {angle_diff:.2f}°")
    print("这个角度差编码了它们之间的相对位置关系！")
    print("=" * 60 + "\n")
    
    # 测试 3: 旋转应该保持向量长度（近似）
    x_norm_before = torch.norm(x1, dim=-1)
    x_norm_after = torch.norm(x1_rot1, dim=-1)
    norm_diff = torch.abs(x_norm_before - x_norm_after).max().item()
    
    print(f"  旋转前向量长度: {x_norm_before.item():.6f}")
    print(f"  旋转后向量长度: {x_norm_after.item():.6f}")
    print(f"  长度差异: {norm_diff:.8f}")
    assert norm_diff < 1e-5, f"旋转应保持向量长度，但差异为 {norm_diff}"
    print("✓ 旋转保持向量长度（旋转矩阵特性）\n")
    
    # ========== 测试 5: 边界情况 ==========
    print("测试 5: 边界情况")
    print("-" * 60)
    
    # 测试最小维度
    x_min = torch.randn(1, 1, 1, 2, device=device)  # 最小偶数维度
    rope_cache_min = RoPECache(head_dim=2, max_pos=10, device=device)
    pos_min = torch.tensor([0], device=device)
    cos_min, sin_min = rope_cache_min.get(pos_min)
    x_min_rot = apply_rope_single(x_min, cos_min, sin_min)
    assert x_min_rot.shape == x_min.shape, "最小维度测试失败"
    print("✓ 最小维度 (D=2) 测试通过")
    
    # 测试单 token 序列
    x_single = torch.randn(1, 1, 1, D, device=device)
    pos_single = torch.tensor([0], device=device)
    cos_single, sin_single = rope_cache.get(pos_single)
    x_single_rot = apply_rope_single(x_single, cos_single, sin_single)
    assert x_single_rot.shape == x_single.shape, "单 token 测试失败"
    print("✓ 单 token 序列测试通过")
    
    # 测试二维 positions 输入
    pos_2d = torch.tensor([[0, 1, 2]], device=device)
    cos_2d, sin_2d = rope_cache.get(pos_2d)
    assert cos_2d.shape[0] == 3, "二维 positions 处理失败"
    print("✓ 二维 positions 输入测试通过\n")
    
    # ========== 测试总结 ==========
    print("=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)
    print("\nRoPE 功能验证:")
    print("  ✓ 缓存初始化和查询")
    print("  ✓ 缓存自动扩展")
    print("  ✓ 旋转操作正确性")
    print("  ✓ 数值特性（长度保持、位置差异）")
    print("  ✓ 边界情况处理")
