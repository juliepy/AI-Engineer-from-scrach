"""
专家混合（Mixture of Experts, MoE）架构中的单个专家MLP模块。

本模块实现了专家网络的前馈层，支持两种激活函数：
- SwiGLU (Swish-Gated Linear Unit): 使用门控机制的前馈网络
- GELU: 标准的高斯误差线性单元激活函数
"""
from __future__ import annotations
import torch.nn as nn

class ExpertMLP(nn.Module):
    """
    单个专家MLP模块，用于专家混合架构。
    
    支持两种前馈网络结构：
    1. SwiGLU: 使用两个线性层和SiLU激活函数的门控机制
    2. GELU: 标准的GELU激活函数前馈网络
    
    Args:
        dim: 输入和输出的维度
        mult: 隐藏层维度相对于输入维度的倍数，默认为4
        swiglu: 是否使用SwiGLU激活函数，默认为True。False时使用GELU
        dropout: Dropout概率，默认为0.0（不使用dropout）
    """
    def __init__(self, dim: int, mult: int = 4, swiglu: bool = True, dropout: float = 0.0):
        super().__init__()
        # 计算隐藏层维度：通常是输入维度的mult倍
        inner = mult * dim
        
        if swiglu:
            # SwiGLU结构：使用门控机制
            # inp1: 第一个线性变换层（门控分支）
            self.inp1 = nn.Linear(dim, inner, bias=False)
            # inp2: 第二个线性变换层（值分支）
            self.inp2 = nn.Linear(dim, inner, bias=False)
            # SiLU激活函数（Swish激活函数）
            self.act = nn.SiLU()
            # 输出线性层，将隐藏层维度映射回原始维度
            self.out = nn.Linear(inner, dim, bias=False)
            # Dropout层，用于正则化
            self.drop = nn.Dropout(dropout)
            self.swiglu = True
        else:
            # GELU结构：标准的全连接前馈网络
            self.ff = nn.Sequential(
                nn.Linear(dim, inner),      # 第一个线性层（扩展到隐藏层）
                nn.GELU(),                  # GELU激活函数
                nn.Linear(inner, dim),      # 第二个线性层（映射回原始维度）
                nn.Dropout(dropout)         # Dropout层
            )
            self.swiglu = False
    
    def forward(self, x):
        """
        前向传播函数。
        
        Args:
            x: 输入张量，形状为 (batch_size, seq_len, dim) 或 (batch_size, dim)
        
        Returns:
            输出张量，形状与输入相同
        """
        if self.swiglu:
            # SwiGLU前向传播：
            # a: 第一个线性变换的结果（门控分支）
            # b: 第二个线性变换后经过SiLU激活的结果（值分支）
            # 最终输出：a * b 经过输出层和dropout
            a = self.inp1(x)
            b = self.act(self.inp2(x))
            return self.drop(self.out(a * b))
        else:
            # GELU前向传播：直接通过Sequential模块
            return self.ff(x)


if __name__ == "__main__":
    """
    测试代码：验证 ExpertMLP 模块的功能。
    """
    import torch
    
    print("=" * 60)
    print("ExpertMLP 测试")
    print("=" * 60)
    
    # 设置随机种子以便结果可复现
    torch.manual_seed(42)
    
    # 测试参数
    batch_size = 2
    seq_len = 10
    dim = 64
    mult = 4
    
    # ========== 测试1: SwiGLU模式 ==========
    print("\n[测试1] SwiGLU模式（无dropout）")
    print("-" * 60)
    expert_swiglu = ExpertMLP(dim=dim, mult=mult, swiglu=True, dropout=0.0)
    expert_swiglu.eval()  # 设置为评估模式
    
    # 测试2D输入 (batch_size, dim)
    x_2d = torch.randn(seq_len, dim)
    out_2d = expert_swiglu(x_2d)
    print(f"输入形状 (2D): {x_2d.shape}")
    print(f"输出形状 (2D): {out_2d.shape}")
    assert out_2d.shape == x_2d.shape, f"输出形状不匹配！期望 {x_2d.shape}, 得到 {out_2d.shape}"
    print("✓ 2D输入测试通过")
    
    # 测试3D输入 (batch_size, seq_len, dim)
    x_3d = torch.randn(batch_size, seq_len, dim)
    out_3d = expert_swiglu(x_3d)
    print(f"输入形状 (3D): {x_3d.shape}")
    print(f"输出形状 (3D): {out_3d.shape}")
    assert out_3d.shape == x_3d.shape, f"输出形状不匹配！期望 {x_3d.shape}, 得到 {out_3d.shape}"
    print("✓ 3D输入测试通过")
    
    # ========== 测试2: GELU模式 ==========
    print("\n[测试2] GELU模式（无dropout）")
    print("-" * 60)
    expert_gelu = ExpertMLP(dim=dim, mult=mult, swiglu=False, dropout=0.0)
    expert_gelu.eval()
    
    out_2d_gelu = expert_gelu(x_2d)
    print(f"输入形状 (2D): {x_2d.shape}")
    print(f"输出形状 (2D): {out_2d_gelu.shape}")
    assert out_2d_gelu.shape == x_2d.shape, f"输出形状不匹配！期望 {x_2d.shape}, 得到 {out_2d_gelu.shape}"
    print("✓ 2D输入测试通过")
    
    out_3d_gelu = expert_gelu(x_3d)
    print(f"输入形状 (3D): {x_3d.shape}")
    print(f"输出形状 (3D): {out_3d_gelu.shape}")
    assert out_3d_gelu.shape == x_3d.shape, f"输出形状不匹配！期望 {x_3d.shape}, 得到 {out_3d_gelu.shape}"
    print("✓ 3D输入测试通过")
    
    # ========== 测试3: Dropout功能 ==========
    print("\n[测试3] Dropout功能测试")
    print("-" * 60)
    expert_dropout = ExpertMLP(dim=dim, mult=mult, swiglu=True, dropout=0.5)
    
    # 训练模式下，dropout应该生效
    expert_dropout.train()
    out_train = expert_dropout(x_2d)
    print(f"训练模式输出形状: {out_train.shape}")
    print("✓ Dropout训练模式测试通过")
    
    # 评估模式下，dropout应该被禁用
    expert_dropout.eval()
    out_eval = expert_dropout(x_2d)
    print(f"评估模式输出形状: {out_eval.shape}")
    print("✓ Dropout评估模式测试通过")
    
    # ========== 测试4: 梯度计算 ==========
    print("\n[测试4] 梯度计算测试")
    print("-" * 60)
    expert_swiglu.train()
    x_requires_grad = torch.randn(batch_size, dim, requires_grad=True)
    out = expert_swiglu(x_requires_grad)
    
    # 计算梯度
    loss = out.sum()
    loss.backward()
    
    assert x_requires_grad.grad is not None, "输入梯度未计算！"
    print(f"输入梯度形状: {x_requires_grad.grad.shape}")
    print("✓ 梯度计算测试通过")
    
    # ========== 测试5: 不同mult值 ==========
    print("\n[测试5] 不同mult值测试")
    print("-" * 60)
    for mult_val in [2, 4, 8]:
        expert = ExpertMLP(dim=dim, mult=mult_val, swiglu=True, dropout=0.0)
        expert.eval()
        out = expert(x_2d)
        assert out.shape == x_2d.shape, f"mult={mult_val} 时输出形状不匹配！"
        print(f"✓ mult={mult_val} 测试通过")
    
    # ========== 测试6: 参数统计 ==========
    print("\n[测试6] 参数统计")
    print("-" * 60)
    expert_swiglu = ExpertMLP(dim=dim, mult=mult, swiglu=True, dropout=0.0)
    expert_gelu = ExpertMLP(dim=dim, mult=mult, swiglu=False, dropout=0.0)
    
    def count_parameters(model):
        return sum(p.numel() for p in model.parameters())
    
    params_swiglu = count_parameters(expert_swiglu)
    params_gelu = count_parameters(expert_gelu)
    
    print(f"SwiGLU模式参数数量: {params_swiglu:,}")
    print(f"GELU模式参数数量: {params_gelu:,}")
    print(f"参数数量差异: {abs(params_swiglu - params_gelu):,}")
    
    # SwiGLU应该有更多参数（因为有两个输入层）
    assert params_swiglu > params_gelu, "SwiGLU参数应该多于GELU"
    print("✓ 参数统计测试通过")
    
    # ========== 测试总结 ==========
    print("\n" + "=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)