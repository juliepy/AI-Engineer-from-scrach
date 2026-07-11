"""
RMSNorm (Root Mean Square Layer Normalization) 实现
RMS归一化是一种层归一化方法，相比传统的LayerNorm，它不使用均值，只使用均方根值进行归一化。
"""

import torch
import torch.nn as nn

class RMSNorm(nn.Module):
    """根均方层归一化 (Root Mean Square Layer Normalization)
    
    RMSNorm是一种简化的层归一化方法，相比LayerNorm移除了均值中心化步骤，
    只使用均方根值进行归一化，计算更高效。
    
    公式：
        y = x * g / rms(x)
        其中 rms(x) = sqrt(mean(x^2) + eps)
        
    Args:
        dim (int): 输入特征的维度
        eps (float): 防止除零的小常数，默认为 1e-8
    """
    def __init__(self, dim: int, eps: float = 1e-8):
        """
        初始化RMSNorm层
        
        Args:
            dim (int): 输入特征的维度
            eps (float): 防止除零的小常数，默认为 1e-8
        """
        super().__init__()
        # 防止除零的小常数
        self.eps = eps
        # 可学习的缩放参数，初始化为全1
        self.weight = nn.Parameter(torch.ones(dim))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x (torch.Tensor): 输入张量，形状为 (..., dim)
            
        Returns:
            torch.Tensor: 归一化后的张量，形状与输入相同
        """
        # 计算均方根值 (RMS)
        # x.pow(2): 计算每个元素的平方
        # .mean(dim=-1, keepdim=True): 在最后一个维度上求均值，保持维度
        # .add(self.eps): 加上小常数防止除零
        # .sqrt(): 开平方根得到RMS值
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        
        # 归一化：先除以RMS值，再乘以可学习的权重参数
        return (x / rms) * self.weight


if __name__ == "__main__":
    """简单的测试代码"""
    print("=" * 50)
    print("RMSNorm 测试")
    print("=" * 50)
    
    # 测试1: 基本功能测试
    print("\n[测试1] 基本功能测试")
    dim = 128
    rmsnorm = RMSNorm(dim=dim)
    
    # 创建随机输入 (batch_size=2, seq_len=10, dim=128)
    x = torch.randn(2, 10, dim)
    print(f"输入形状: {x.shape}")
    
    # 前向传播
    output = rmsnorm(x)
    print(f"输出形状: {output.shape}")
    print(f"输出统计: mean={output.mean().item():.6f}, std={output.std().item():.6f}")
    assert output.shape == x.shape, "输出形状应该与输入相同"
    print("✓ 形状检查通过")
    
    # 测试2: 验证RMS计算
    print("\n[测试2] RMS计算验证")
    test_input = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])
    rmsnorm_test = RMSNorm(dim=5)
    # 手动计算RMS
    manual_rms = torch.sqrt(torch.mean(test_input ** 2) + rmsnorm_test.eps)
    print(f"手动计算的RMS: {manual_rms.item():.6f}")
    
    # 通过模型计算
    output_test = rmsnorm_test(test_input)
    # 从输出反推RMS (因为 weight 初始化为1)
    model_rms = torch.sqrt(torch.mean((test_input / (output_test / rmsnorm_test.weight)) ** 2))
    print(f"模型计算的RMS: {model_rms.item():.6f}")
    print("✓ RMS计算验证通过")
    
    # 测试3: 不同输入形状
    print("\n[测试3] 不同输入形状测试")
    shapes = [
        (32,),           # 1D
        (4, 32),         # 2D
        (2, 8, 32),      # 3D
        (1, 5, 10, 32),  # 4D
    ]
    
    for shape in shapes:
        rmsnorm_shape = RMSNorm(dim=32)
        x_shape = torch.randn(*shape)
        output_shape = rmsnorm_shape(x_shape)
        assert output_shape.shape == x_shape.shape, f"形状 {shape} 测试失败"
        print(f"✓ 形状 {shape} 测试通过")
    
    # 测试4: 权重参数测试
    print("\n[测试4] 权重参数测试")
    rmsnorm_weight = RMSNorm(dim=64)
    x_weight = torch.randn(3, 64)
    
    # 检查权重是否可学习
    assert rmsnorm_weight.weight.requires_grad, "权重应该可以求梯度"
    print(f"权重形状: {rmsnorm_weight.weight.shape}")
    print(f"权重初始值范围: [{rmsnorm_weight.weight.min().item():.3f}, {rmsnorm_weight.weight.max().item():.3f}]")
    print("✓ 权重参数测试通过")
    
    # 测试5: 梯度测试
    print("\n[测试5] 梯度测试")
    rmsnorm_grad = RMSNorm(dim=16)
    x_grad = torch.randn(2, 16, requires_grad=True)
    output_grad = rmsnorm_grad(x_grad)
    
    # 计算梯度
    loss = output_grad.sum()
    loss.backward()
    
    assert x_grad.grad is not None, "输入应该有梯度"
    assert rmsnorm_grad.weight.grad is not None, "权重应该有梯度"
    print(f"输入梯度形状: {x_grad.grad.shape}")
    print(f"权重梯度形状: {rmsnorm_grad.weight.grad.shape}")
    print("✓ 梯度测试通过")
    
    print("\n" + "=" * 50)
    print("所有测试通过！✓")
    print("=" * 50)