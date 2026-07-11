"""
现代 Transformer 块实现

本模块实现了现代 Transformer 架构的核心组件，集成了多种先进的优化技术：
- RMSNorm 或 LayerNorm 归一化
- 现代因果自注意力机制（支持 RoPE、滑动窗口、attention sink、GQA 等）
- SwiGLU 激活函数或传统 FFN
- KV Cache 支持，用于推理加速

该实现遵循 Pre-Norm 架构，即先归一化再计算注意力/前馈网络。
"""

import torch.nn as nn
from rmsnorm import RMSNorm
from swiglu import SwiGLU
from attn_modern import CausalSelfAttentionModern


class TransformerBlockModern(nn.Module):
    """
    现代 Transformer 块
    
    实现了 Transformer 的核心结构，包含：
    1. 自注意力层（带归一化）
    2. 前馈网络层（带归一化）
    3. 残差连接
    
    支持多种现代优化技术，可根据需要灵活配置。
    
    Attributes:
        ln1: 注意力层前的归一化层（RMSNorm 或 LayerNorm）
        attn: 因果自注意力层
        ln2: 前馈网络层前的归一化层（RMSNorm 或 LayerNorm）
        ffn: 前馈网络（SwiGLU 或传统 FFN）
    """
    
    def __init__(self, n_embd: int, n_head: int, dropout: float = 0.0,
                 use_rmsnorm: bool = True, use_swiglu: bool = True,
                 rope: bool = True, max_pos: int = 4096,
                 sliding_window: int | None = None, attention_sink: int = 0, n_kv_head: int | None = None):
        """
        初始化现代 Transformer 块
        
        Args:
            n_embd: 嵌入维度（模型维度）
            n_head: 注意力头数
            dropout: Dropout 比率，默认为 0.0（无 dropout）
            use_rmsnorm: 是否使用 RMSNorm（True）或 LayerNorm（False），默认为 True
            use_swiglu: 是否使用 SwiGLU 激活函数（True）或传统 FFN（False），默认为 True
            rope: 是否使用 RoPE（旋转位置编码），默认为 True
            max_pos: 最大位置编码长度，用于 RoPE 缓存，默认为 4096
            sliding_window: 滑动窗口大小，限制注意力范围以节省内存，None 表示无限制，默认为 None
            attention_sink: attention sink 大小，保留开头的 token 数量，默认为 0
            n_kv_head: Key-Value 头数，用于 GQA（分组查询注意力），None 表示与 n_head 相同（MHA），默认为 None
        """
        super().__init__()
        
        # 根据配置选择归一化层类型
        Norm = RMSNorm if use_rmsnorm else nn.LayerNorm
        
        # 注意力层前的归一化（Pre-Norm 架构）
        self.ln1 = Norm(n_embd)
        
        # 现代因果自注意力层，支持多种优化技术
        self.attn = CausalSelfAttentionModern(
            n_embd, n_head, dropout, rope, max_pos, 
            sliding_window, attention_sink, n_kv_head
        )
        
        # 前馈网络层前的归一化（Pre-Norm 架构）
        self.ln2 = Norm(n_embd)
        
        # 前馈网络：SwiGLU 或传统 FFN
        if use_swiglu:
            # SwiGLU: 使用 Swish 激活的 GLU 变体，通常性能更好
            self.ffn = SwiGLU(n_embd, mult=4, dropout=dropout)
        else:
            # 传统 FFN: Linear -> GELU -> Linear，扩展比为 4
            self.ffn = nn.Sequential(
                nn.Linear(n_embd, 4*n_embd),  # 扩展到 4 倍维度
                nn.GELU(),                     # GELU 激活函数
                nn.Linear(4*n_embd, n_embd),   # 压缩回原始维度
                nn.Dropout(dropout)            # Dropout 正则化
            )
    
    def forward(self, x, kv_cache=None, start_pos: int = 0):
        """
        前向传播
        
        实现 Pre-Norm 架构的 Transformer 块：
        1. 归一化 -> 注意力 -> 残差连接
        2. 归一化 -> 前馈网络 -> 残差连接
        
        Args:
            x: 输入张量，形状为 (B, T, n_embd)
               B: batch size（批次大小）
               T: sequence length（序列长度）
               n_embd: 嵌入维度
            kv_cache: KV Cache，用于推理时缓存 Key 和 Value 向量，默认为 None
            start_pos: 当前序列的起始位置，用于 RoPE 位置编码，默认为 0
        
        Returns:
            tuple: (x, kv_cache)
                - x: 输出张量，形状为 (B, T, n_embd)
                - kv_cache: 更新后的 KV Cache（如果提供了 kv_cache）
        """
        # 注意力分支：归一化 -> 注意力 -> 残差连接
        a, kv_cache = self.attn(
            self.ln1(x),           # Pre-Norm: 先归一化
            kv_cache=kv_cache,     # 传递 KV Cache
            start_pos=start_pos    # 传递位置信息
        )
        x = x + a  # 残差连接
        
        # 前馈网络分支：归一化 -> FFN -> 残差连接
        x = x + self.ffn(self.ln2(x))  # Pre-Norm: 先归一化，然后 FFN，最后残差连接
        
        return x, kv_cache


# ==================== 测试代码 ====================

if __name__ == "__main__":
    """测试代码"""
    import torch
    
    print("=" * 60)
    print("TransformerBlockModern 模块测试")
    print("=" * 60)
    
    # 设置随机种子以确保可重复性
    torch.manual_seed(42)
    
    # 测试参数
    B, T, n_embd, n_head = 2, 5, 16, 4  # batch=2, seq_len=5, dim=16, heads=4
    
    # 测试 1: 基本功能测试（默认配置：RMSNorm + SwiGLU + RoPE）
    print("\n[测试 1] 基本功能测试（RMSNorm + SwiGLU + RoPE）")
    print("-" * 60)
    model = TransformerBlockModern(n_embd=n_embd, n_head=n_head, dropout=0.0)
    x = torch.randn(B, T, n_embd)
    
    print(f"输入形状: {x.shape}")
    output, kv_cache = model(x)
    print(f"输出形状: {output.shape}")
    print(f"KV Cache - k形状: {kv_cache.k.shape}, v形状: {kv_cache.v.shape}, 序列长度: {kv_cache.T}")
    print(f"KV Cache k (batch=0, head=0): \n{kv_cache.k[0, 0, :, :]}")
    print(f"KV Cache v (batch=0, head=0): \n{kv_cache.v[0, 0, :, :]}")
    
    assert output.shape == x.shape, "输出形状应该与输入形状相同"
    print("✓ 基本功能测试通过")
    
    # 测试 2: 不同配置测试（LayerNorm + 传统 FFN）
    print("\n[测试 2] 不同配置测试（LayerNorm + 传统 FFN）")
    print("-" * 60)
    model2 = TransformerBlockModern(
        n_embd=n_embd, n_head=n_head, 
        use_rmsnorm=False, use_swiglu=False, rope=False
    )
    output2, _ = model2(x)
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output2.shape}")
    assert output2.shape == x.shape, "输出形状应该与输入形状相同"
    print("✓ 不同配置测试通过")
    
    # 测试 3: KV Cache 测试（推理模式）
    print("\n[测试 3] KV Cache 测试（推理模式）")
    print("-" * 60)
    print("说明：KV Cache 在自回归生成中会累积存储每个 token 的 k 和 v")
    print("      每次处理新 token 时，新的 k 和 v 会追加到缓存中")
    print("-" * 60)
    model.eval()  # 设置为评估模式
    with torch.no_grad():
        # 第一次前向传播（无 KV Cache）
        x1 = torch.randn(B, 1, n_embd)  # 单个 token
        output1, kv_cache = model(x1, kv_cache=None, start_pos=0)
        print(f"步骤 1 - 输入形状: {x1.shape}, 输出形状: {output1.shape}")
        if kv_cache is not None:
            print(f"  步骤 1 后 KV Cache 序列长度: {kv_cache.T} (存储了第 1 个 token 的 k 和 v)")
        
        # 第二次前向传播（使用 KV Cache）
        x2 = torch.randn(B, 1, n_embd)  # 下一个 token
        output2, kv_cache = model(x2, kv_cache=kv_cache, start_pos=1)
        print(f"步骤 2 - 输入形状: {x2.shape}, 输出形状: {output2.shape}")
        if kv_cache is not None:
            print(f"  步骤 2 后 KV Cache 序列长度: {kv_cache.T} (存储了第 1 和第 2 个 token 的 k 和 v)")
            print(f"  KV Cache 形状: k={kv_cache.k.shape}, v={kv_cache.v.shape}")
            print(f"  解释：序列长度 T=2 是因为累积了 2 次前向传播的 token")
            # 显示第一个 batch、第一个 head 的 k 和 v 的前几个维度
            print(f"\n  KV Cache k (batch=0, head=0): \n{kv_cache.k[0, 0, :, :]}")
            print(f"  KV Cache v (batch=0, head=0): \n{kv_cache.v[0, 0, :, :]}")
        else:
            print("KV Cache: None")
    
    assert output1.shape == (B, 1, n_embd), "第一次输出形状不正确"
    assert output2.shape == (B, 1, n_embd), "第二次输出形状不正确"
    print("✓ KV Cache 测试通过")
    
    # 测试 4: 梯度检查
    print("\n[测试 4] 梯度检查")
    print("-" * 60)
    model.train()  # 设置为训练模式
    x = torch.randn(B, T, n_embd, requires_grad=True)
    output, _ = model(x)
    loss = output.sum()
    loss.backward()
    
    print(f"输入梯度是否存在: {x.grad is not None}")
    print(f"输入梯度形状: {x.grad.shape if x.grad is not None else None}")
    assert x.grad is not None, "输入应该具有梯度"
    assert x.grad.shape == x.shape, "梯度形状应该与输入形状相同"
    print("✓ 梯度检查通过")
    
    print("\n" + "=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)