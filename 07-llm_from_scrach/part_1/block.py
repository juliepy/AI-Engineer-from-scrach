"""
Transformer Block 模块
实现标准的 Transformer 编码器块，包含多头自注意力和前馈神经网络
"""

import torch.nn as nn
from multi_head import MultiHeadSelfAttention
from ffn import FeedForward

class TransformerBlock(nn.Module):
    """
    Transformer 编码器块
    
    架构流程：
        输入 → LayerNorm1 → 多头自注意力 → 残差连接1 → 
        LayerNorm2 → 前馈网络 → 残差连接2 → 输出
    
    这是 Transformer 的核心构建块，采用 Pre-LN 架构（先归一化再计算）
    """
    
    def __init__(self, d_model: int, n_head: int, dropout: float = 0.0):
        """
        初始化 Transformer Block
        
        参数:
            d_model (int): 模型的隐藏层维度（词向量维度）
            n_head (int): 多头注意力的头数，d_model 必须能被 n_head 整除
            dropout (float): Dropout 概率，用于正则化防止过拟合，默认为 0.0
        """
        super().__init__()
        
        # 第一个层归一化：用于注意力层之前
        self.ln1 = nn.LayerNorm(d_model)
        
        # 多头自注意力层：捕捉序列中不同位置之间的依赖关系
        self.attn = MultiHeadSelfAttention(d_model, n_head, dropout, False)
        
        # 第二个层归一化：用于前馈网络之前
        self.ln2 = nn.LayerNorm(d_model)
        
        # 前馈神经网络：对每个位置独立进行非线性变换
        # mult=4 表示中间层维度是 d_model 的 4 倍（标准设置）
        self.ffn = FeedForward(d_model, mult=4, dropout=dropout)

    def forward(self, x):
        """
        前向传播
        
        参数:
            x: 输入张量，形状为 (batch_size, seq_len, d_model)
        
        返回:
            输出张量，形状为 (batch_size, seq_len, d_model)
        """
        print(f"\n【Transformer Block 前向传播】")
        print(f"  输入 x 的形状: {tuple(x.shape)}")
        
        # ==================== 第一个子层：多头自注意力 ====================
        # 步骤1: 第一次 LayerNorm
        x_ln1 = self.ln1(x)
        print(f"  LayerNorm1 后的形状: {tuple(x_ln1.shape)}")
        print(f"  LayerNorm1 后的 x: {x_ln1[:1,:1,:].detach().numpy()}")
        
        # 步骤2: 多头自注意力 (返回 output 和 attention_weights)
        attn_output, attn_weights = self.attn(x_ln1)
        print(f"  多头注意力输出形状: {tuple(attn_output.shape)}")
        print(f"  注意力权重形状: {tuple(attn_weights.shape)}")
        print(f"  注意力权重: {attn_weights[:1,:,:].detach().numpy()}")
        
        # 步骤3: 残差连接
        x = x + attn_output
        print(f"  残差连接后的形状: {tuple(x.shape)}")
        print(f"  残差连接后的 x: {x[:1,:1,:].detach().numpy()}")
        
        # ==================== 第二个子层：前馈网络 ====================
        # 步骤4: 第二次 LayerNorm
        x_ln2 = self.ln2(x)
        print(f"  LayerNorm2 后的形状: {tuple(x_ln2.shape)}")
        print(f"  LayerNorm2 后的 x: {x_ln2[:1,:1,:].detach().numpy()}")
        
        # 步骤5: 前馈网络
        ffn_output = self.ffn(x_ln2)
        print(f"  前馈网络输出形状: {tuple(ffn_output.shape)}")
        print(f"  前馈网络输出: {ffn_output[:1,:1,:].detach().numpy()}")
        
        # 步骤6: 残差连接
        x = x + ffn_output
        print(f"  最终输出形状: {tuple(x.shape)}")
        print(f"  最终输出: {x[:1,:1,:].detach().numpy()}")
        return x


# ==================== 测试代码 ====================
if __name__ == "__main__":
    import torch
    
    print("=" * 60)
    print("TransformerBlock 测试")
    print("=" * 60)
    
    # 测试配置
    batch_size = 2
    seq_len = 5
    d_model = 16
    n_head = 4
    dropout = 0.1
    
    print(f"\n【配置参数】")
    print(f"  批次大小: {batch_size}")
    print(f"  序列长度: {seq_len}")
    print(f"  模型维度: {d_model}")
    print(f"  注意力头数: {n_head}")
    print(f"  Dropout率: {dropout}")
    
    # 1. 创建模型
    print(f"\n【1. 创建 TransformerBlock】")
    block = TransformerBlock(d_model=d_model, n_head=n_head, dropout=dropout)
    print(f"  ✓ 模型创建成功")
    
    # 2. 统计参数量
    total_params = sum(p.numel() for p in block.parameters())
    trainable_params = sum(p.numel() for p in block.parameters() if p.requires_grad)
    print(f"\n【2. 模型参数统计】")
    print(f"  总参数量: {total_params:,}")
    print(f"  可训练参数: {trainable_params:,}")
    
    # 参数详细分解
    print(f"\n  各组件参数量:")
    print(f"    - LayerNorm1: {sum(p.numel() for p in block.ln1.parameters()):,}")
    print(f"    - 多头注意力: {sum(p.numel() for p in block.attn.parameters()):,}")
    print(f"    - LayerNorm2: {sum(p.numel() for p in block.ln2.parameters()):,}")
    print(f"    - 前馈网络: {sum(p.numel() for p in block.ffn.parameters()):,}")
    
    # 3. 前向传播测试
    print(f"\n【3. 前向传播测试】")
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"  输入形状: {tuple(x.shape)}")
    
    block.eval()  # 评估模式（关闭 dropout）
    with torch.no_grad():
        output = block(x)
    
    print(f"  输出形状: {tuple(output.shape)}")
    print(f"  ✓ 形状保持不变")
    
    # 4. 输出统计
    print(f"\n【4. 输出统计】")
    print(f"  输入均值: {x.mean():.6f}, 标准差: {x.std():.6f}")
    print(f"  输出均值: {output.mean():.6f}, 标准差: {output.std():.6f}")
    print(f"  输出范围: [{output.min():.3f}, {output.max():.3f}]")
    
    