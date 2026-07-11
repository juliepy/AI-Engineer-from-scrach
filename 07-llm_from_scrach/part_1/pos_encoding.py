"""
1.1 位置编码（绝对位置 - 学习式 + 正弦式）
Positional encodings (absolute learned + sinusoidal)

位置编码的作用：
- Transformer 是并行处理序列的，不像RNN那样有天然的顺序信息
- 位置编码为模型提供了token在序列中的位置信息
- 两种主流方式：学习式（可训练参数）和正弦式（固定公式）
"""
import math
import torch
import torch.nn as nn

class LearnedPositionalEncoding(nn.Module):
    """
    学习式位置编码（Learned Positional Encoding）
    
    原理：
    - 使用一个可训练的Embedding层来学习每个位置的表示
    - 每个位置索引(0, 1, 2, ..., max_len-1)都有对应的d_model维向量
    - 这些向量会在训练过程中被优化
    
    优点：灵活，可以学习到数据中的位置模式
    缺点：无法处理超过max_len的序列长度（外推能力差）
    """
    def __init__(self, max_len: int, d_model: int):
        """
        初始化学习式位置编码
        
        参数：
            max_len: 支持的最大序列长度
            d_model: 模型的隐藏维度（embedding维度）
        """
        super().__init__()
        # 创建一个可训练的位置嵌入表，大小为 (max_len, d_model)
        # 每个位置索引对应一个d_model维的向量
        self.emb = nn.Embedding(max_len, d_model)

    def forward(self, x: torch.Tensor):
        """
        前向传播：将位置编码加到输入上
        
        参数：
            x: 输入张量，形状为 (B, T, d_model)
               B = batch_size (批次大小)
               T = sequence_length (序列长度)
               d_model = embedding_dimension (嵌入维度)
        
        返回：
            形状为 (B, T, d_model) 的张量，已加上位置信息
        """
        # 获取序列的批次大小、序列长度和隐藏维度
        B, T, _ = x.shape
        
        # 生成位置索引：[0, 1, 2, ..., T-1]
        # 需要与输入在同一设备上（CPU或GPU）
        pos = torch.arange(T, device=x.device)
        
        # 通过嵌入层获取位置编码，形状：(T, d_model)
        pos_emb = self.emb(pos)
        
        # 将位置编码加到输入上
        # unsqueeze(0) 将形状从 (T, d_model) 变为 (1, T, d_model)
        # 然后广播到 (B, T, d_model)，与x相加
        return x + pos_emb.unsqueeze(0)

class SinusoidalPositionalEncoding(nn.Module):
    """
    正弦位置编码（Sinusoidal Positional Encoding）
    
    原理（来自原始Transformer论文 "Attention is All You Need"）：
    - 使用不同频率的正弦和余弦函数来编码位置
    - 对于位置pos和维度i，编码公式为：
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    
    优点：
    - 不需要训练，节省参数
    - 理论上可以外推到更长的序列（虽然实际效果有限）
    - 不同维度使用不同频率，能捕捉多尺度的位置信息
    
    特性：
    - 相对位置关系可以通过线性变换表示（PE(pos+k)可由PE(pos)线性表示）
    - 这使得模型更容易学习相对位置关系
    """
    def __init__(self, max_len: int, d_model: int):
        """
        初始化正弦位置编码
        
        参数：
            max_len: 支持的最大序列长度
            d_model: 模型的隐藏维度（必须是偶数，因为需要成对使用sin/cos）
        """
        super().__init__()
        
        # 创建位置编码矩阵，形状：(max_len, d_model)
        pe = torch.zeros(max_len, d_model)
        
        # 生成位置索引：[[0], [1], [2], ..., [max_len-1]]
        # unsqueeze(1) 将 (max_len,) 变为 (max_len, 1)，方便后续广播
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # 计算除数项（用于控制不同维度的频率）
        # 对于维度 i，除数为 10000^(2i/d_model)
        # 使用对数技巧计算：exp(2i * -log(10000) / d_model)
        # torch.arange(0, d_model, 2) 生成 [0, 2, 4, ..., d_model-2]
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        
        # 偶数维度使用sin函数
        # pe[:, 0::2] 选择所有行的第 0, 2, 4, ... 列
        # position * div_term 广播为 (max_len, d_model/2)
        pe[:, 0::2] = torch.sin(position * div_term)
        
        # 奇数维度使用cos函数
        # pe[:, 1::2] 选择所有行的第 1, 3, 5, ... 列
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # 将位置编码注册为buffer（不是模型参数，不会被优化器更新）
        # buffer会被保存到模型的state_dict中，可以随模型一起保存和加载
        self.register_buffer('pe', pe)  # (max_len, d_model)

    def forward(self, x: torch.Tensor):
        """
        前向传播：将位置编码加到输入上
        
        参数：
            x: 输入张量，形状为 (B, T, d_model)
               B = batch_size (批次大小)
               T = sequence_length (序列长度，必须 <= max_len)
               d_model = embedding_dimension (嵌入维度)
        
        返回：
            形状为 (B, T, d_model) 的张量，已加上位置信息
        """
        # 获取序列的批次大小和长度
        B, T, _ = x.shape
        print(f"[SinusoidalPE] 输入x形状: {x.shape}")
        
        # 取出前T个位置的编码：self.pe[:T] 形状为 (T, d_model)
        pos_encoding = self.pe[:T]
        print(f"[SinusoidalPE] 位置编码形状: {pos_encoding.shape}")
        
        # unsqueeze(0) 将形状变为 (1, T, d_model)
        pos_encoding_unsqueezed = pos_encoding.unsqueeze(0)
        print(f"[SinusoidalPE] unsqueeze后形状: {pos_encoding_unsqueezed.shape}")
        
        # 然后广播到 (B, T, d_model)，与x相加
        result = x + pos_encoding_unsqueezed
        print(f"[SinusoidalPE] 输出结果形状: {result.shape}")
        
        return result


# ============================================================================
# 测试代码
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("正弦位置编码测试 (Sinusoidal Positional Encoding Test)")
    print("=" * 80)
    
    # 设置参数
    max_len = 100      # 最大序列长度
    d_model = 64       # 模型维度
    batch_size = 2     # 批次大小
    seq_len = 20       # 当前序列长度
    
    print(f"\n参数配置:")
    print(f"  - 最大序列长度 (max_len): {max_len}")
    print(f"  - 模型维度 (d_model): {d_model}")
    print(f"  - 批次大小 (batch_size): {batch_size}")
    print(f"  - 当前序列长度 (seq_len): {seq_len}")
    
    # 创建正弦位置编码实例
    pos_encoder = SinusoidalPositionalEncoding(max_len, d_model)
    print(f"\n✓ 创建正弦位置编码器成功\n")
    
    # 创建一个随机输入张量（模拟token embeddings）
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"输入张量形状: {x.shape}\n")
    print(f"输入张量: {x}\n")
    
    # 应用位置编码
    output = pos_encoder(x)
    print(f"输出张量形状: {output.shape}\n")
    print(f"输出张量: {output}\n")
    
    # 验证形状是否正确
    assert output.shape == x.shape, "输出形状与输入形状不匹配！"
    print("✓ 形状验证通过\n")
    
    # 打印前几个位置的编码（部分维度）
    print(f"\n前5个位置，前8个维度的编码值:\n")
    pe_sample = pos_encoder.pe[:5, :8]
    for i, pos_vec in enumerate(pe_sample):
        print(f"  位置 {i}: {pos_vec.numpy()}")
    
    # 计算统计信息
    print(f"\n位置编码矩阵统计:\n ")
    print(f"  - 均值: {pos_encoder.pe.mean().item():.6f}")
    print(f"  - 标准差: {pos_encoder.pe.std().item():.6f}")
    print(f"  - 最小值: {pos_encoder.pe.min().item():.6f}")
    print(f"  - 最大值: {pos_encoder.pe.max().item():.6f}")
    
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)