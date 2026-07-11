"""
SwiGLU 激活函数模块

SwiGLU (Swish-Gated Linear Unit) 是一种改进的前馈网络激活函数，
结合了 Swish 激活函数和门控机制，在 Transformer 模型中表现优异。

公式: output = (xW1) ⊗ swish(xW2) W3
其中 ⊗ 表示逐元素相乘（Hadamard 积）
"""

import torch.nn as nn


class SwiGLU(nn.Module):
    """SwiGLU 前馈网络模块
    
    实现 SwiGLU 激活函数的前馈网络层，公式为: (xW1) ⊗ swish(xW2) W3
    其中 mult 是扩展因子，用于控制内部维度的大小。
    
    Args:
        dim (int): 输入和输出的特征维度
        mult (int, optional): 扩展因子，内部维度 = mult * dim。默认为 4
        dropout (float, optional): Dropout 概率，用于正则化。默认为 0.0
    
    Attributes:
        w1 (nn.Linear): 第一个线性变换层，将输入从 dim 维度映射到 inner 维度
        w2 (nn.Linear): 第二个线性变换层，将输入从 dim 维度映射到 inner 维度
        w3 (nn.Linear): 第三个线性变换层，将 inner 维度映射回 dim 维度
        act (nn.SiLU): SiLU (Swish) 激活函数，即 x * sigmoid(x)
        drop (nn.Dropout): Dropout 层，用于防止过拟合
    """
    
    def __init__(self, dim: int, mult: int = 4, dropout: float = 0.0):
        """
        初始化 SwiGLU 模块
        
        Args:
            dim (int): 输入和输出的特征维度
            mult (int, optional): 扩展因子，内部维度 = mult * dim。默认为 4
            dropout (float, optional): Dropout 概率，用于正则化。默认为 0.0
        """
        super().__init__()
        # 计算内部维度：扩展后的特征维度
        inner = mult * dim
        
        # 第一个线性层：xW1，用于门控机制
        self.w1 = nn.Linear(dim, inner, bias=False)
        
        # 第二个线性层：xW2，经过激活函数后用于门控
        self.w2 = nn.Linear(dim, inner, bias=False)
        
        # 第三个线性层：将门控后的结果映射回原始维度
        self.w3 = nn.Linear(inner, dim, bias=False)
        
        # SiLU (Swish) 激活函数：x * sigmoid(x)
        self.act = nn.SiLU()
        
        # Dropout 层，用于正则化
        self.drop = nn.Dropout(dropout)
    
    def forward(self, x):
        """
        前向传播
        
        执行 SwiGLU 激活函数计算：
        1. 计算 a = xW1（门控的线性部分）
        2. 计算 b = swish(xW2)（门控的非线性部分）
        3. 计算门控结果：a ⊗ b（逐元素相乘）
        4. 通过 W3 映射回原始维度并应用 dropout
        
        Args:
            x (torch.Tensor): 输入张量，形状为 (..., dim)
        
        Returns:
            torch.Tensor: 输出张量，形状与输入相同 (..., dim)
        """
        # 计算第一个线性变换：xW1
        # print("swiglu forward")
        # print(f"x: {x.shape}")
        a = self.w1(x)
        # print(f"a: {a.shape}")
        
        # 计算第二个线性变换并应用 Swish 激活：swish(xW2)
        b = self.act(self.w2(x))
        # print(f"b: {b.shape}")
        
        # 门控机制：逐元素相乘 (xW1) ⊗ swish(xW2)，然后通过 W3 映射并应用 dropout
        output = self.drop(self.w3(a * b))
        # print(f"output: {output.shape}")
        #print("swiglu end")
        return output


if __name__ == "__main__":
    """测试代码"""
    import torch
    
    print("=" * 60)
    print("SwiGLU 模块测试")
    print("=" * 60)
    
    # 设置随机种子以确保可重复性
    torch.manual_seed(42)
    
    # 测试 1: 基本功能测试
    print("\n[测试 1] 基本功能测试")
    print("-" * 60)
    dim = 128
    batch_size = 4
    seq_len = 10
    
    model = SwiGLU(dim=dim, mult=4, dropout=0.0)
    x = torch.randn(batch_size, seq_len, dim)
    
    print(f"输入形状: {x.shape}")
    output = model(x)
    print(f"输出形状: {output.shape}")
    assert x.shape == output.shape, "输出形状应该与输入形状相同"
    print("✓ 基本功能测试通过")
    
    # 测试 2: 不同扩展因子
    print("\n[测试 2] 不同扩展因子测试")
    print("-" * 60)
    for mult in [2, 4, 8]:
        model = SwiGLU(dim=64, mult=mult, dropout=0.0)
        x = torch.randn(2, 5, 64)
        output = model(x)
        print(f"mult={mult}: 输入形状 {x.shape} -> 输出形状 {output.shape}")
        assert output.shape == x.shape, f"mult={mult} 时输出形状不正确"
    print("✓ 不同扩展因子测试通过")
    
    # 测试 3: 梯度检查
    print("\n[测试 3] 梯度检查")
    print("-" * 60)
    model = SwiGLU(dim=32, mult=4, dropout=0.0)
    x = torch.randn(2, 5, 32, requires_grad=True)
    output = model(x)
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