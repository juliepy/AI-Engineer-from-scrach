"""
前馈神经网络模块 (Feed-Forward Network)

该模块实现了Transformer中的前馈神经网络层，采用两层线性变换和GELU激活函数。
中间层维度通过扩展因子 `mult` 进行扩展，典型的GPT架构中 mult=4。
"""
import torch.nn as nn

class FeedForward(nn.Module):
    """前馈神经网络 - 带扩展因子 `mult` 的FFN
    
    1.5 FFN with expansion factor `mult`.

    维度说明 / Dimensions:
      输入 input:     (B, T, d_model)
      中间 inner:     (B, T, mult*d_model)
      输出 output:    (B, T, d_model)

    其中 `mult*d_model` 表示隐藏层宽度是 `d_model` 的 `mult` 倍。
    `mult*d_model` means the hidden width is `mult` times larger than `d_model`.
    
    典型取值：GPT风格的模块中使用 mult=4 和 GELU 激活函数。
    Typical values: mult=4 for GELU FFN in GPT-style blocks.
    """
    def __init__(self, d_model: int, mult: int = 4, dropout: float = 0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, mult * d_model),
            nn.GELU(),
            nn.Linear(mult * d_model, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


if __name__ == "__main__":
    import torch
    
    print("=" * 60)
    print("前馈神经网络 (FeedForward) 测试")
    print("Feed-Forward Network Test")
    print("=" * 60)
    
    # 设置参数
    batch_size = 2      # B: 批次大小
    seq_length = 5     # T: 序列长度
    d_model = 16        # 模型维度
    mult = 4            # 扩展因子
    
    print(f"\n参数设置 / Parameters:")
    print(f"  批次大小 Batch size (B): {batch_size}")
    print(f"  序列长度 Sequence length (T): {seq_length}")
    print(f"  模型维度 Model dimension (d_model): {d_model}")
    print(f"  扩展因子 Expansion factor (mult): {mult}")
    print(f"  中间层维度 Hidden dimension: {mult * d_model}")
    
    # 创建模型
    ffn = FeedForward(d_model=d_model, mult=mult, dropout=0.1)
    
    # 创建测试输入
    x = torch.randn(batch_size, seq_length, d_model)
    
    print(f"\n维度变化 / Shape Transformation:")
    print(f"  输入 Input shape:  {tuple(x.shape)} = (B={batch_size}, T={seq_length}, d_model={d_model})")
    print(f"  输入 x: {x[:1,:1,:].detach().numpy()}")
    
    # 前向传播并打印中间维度
    with torch.no_grad():
        # 手动展示每一层的变化
        layer1_out = ffn.net[0](x)  # Linear: d_model -> mult*d_model
        print(f"  第1层后 After Linear1: {tuple(layer1_out.shape)} = (B={batch_size}, T={seq_length}, mult*d_model={mult*d_model})")
        print(f"  第1层后 layer1_out: {layer1_out[:1,:1,:].detach().numpy()}")
        
        layer2_out = ffn.net[1](layer1_out)  # GELU
        print(f"  第2层后 After GELU:    {tuple(layer2_out.shape)} = (B={batch_size}, T={seq_length}, mult*d_model={mult*d_model})")
        print(f"  第2层后 layer2_out: {layer2_out[:1,:1,:].detach().numpy()}")
        layer3_out = ffn.net[2](layer2_out)  # Linear: mult*d_model -> d_model
        print(f"  第3层后 After Linear2: {tuple(layer3_out.shape)} = (B={batch_size}, T={seq_length}, d_model={d_model})")
        print(f"  第3层后 layer3_out: {layer3_out[:1,:1,:].detach().numpy()}")
        # 完整的前向传播
        output = ffn(x)
        print(f"  最终输出 Final output:  {tuple(output.shape)} = (B={batch_size}, T={seq_length}, d_model={d_model})")
        print(f"  最终输出 output: {output[:1,:1,:].detach().numpy()}")
    # 打印参数统计
    total_params = sum(p.numel() for p in ffn.parameters())
    print(f"\n模型信息 / Model Info:")
    print(f"  总参数量 Total parameters: {total_params:,}")
    print(f"  可训练参数 Trainable params: {sum(p.numel() for p in ffn.parameters() if p.requires_grad):,}")
    
    print("\n" + "=" * 60)
    print("测试完成 / Test completed successfully!")
    print("=" * 60)