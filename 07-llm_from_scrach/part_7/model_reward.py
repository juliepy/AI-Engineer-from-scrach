"""
奖励模型（Reward Model）模块

奖励模型的训练规则和工作原理：

1. 【训练数据格式】
   - 使用偏好对（preference pairs）数据，格式为 (prompt, chosen, rejected)
   - chosen: 被选中的回复（更好的回复，应该得到更高的奖励分数）
   - rejected: 被拒绝的回复（更差的回复，应该得到更低的奖励分数）
   - 使用 SFT 模板格式化文本：将 prompt 和 response 组合成完整序列

2. 【训练目标】
   - 学习区分更好的回复和更差的回复
   - 核心规则：确保 chosen 回复的奖励分数 > rejected 回复的奖励分数
   - 通过对比学习（contrastive learning）的方式训练

3. 【损失函数】
   支持两种损失函数：
   
   a) Bradley-Terry 损失（默认）：
      loss = -log σ(r_pos - r_neg) = softplus(-(r_pos - r_neg))
      - r_pos: 正样本（chosen）的奖励分数
      - r_neg: 负样本（rejected）的奖励分数
      - 当 r_pos > r_neg 时，损失接近 0
      - 当 r_pos < r_neg 时，损失增大，惩罚模型
   
   b) Margin Ranking 损失：
      loss = max(0, margin - (r_pos - r_neg))
      - 确保 r_pos > r_neg + margin
      - margin: 边界值（默认 1.0），要求正负样本奖励分数有足够的差距

4. 【模型架构】
   - 使用 Transformer Encoder（双向编码器）
   - 输入：完整的 prompt + response 序列（token IDs）
   - 处理流程：
     a) 词嵌入 + 位置嵌入
     b) Transformer 编码器处理序列（忽略 padding）
     c) 层归一化
     d) 掩码平均池化（对所有非 padding 的 token 求平均）
     e) 线性层输出标量奖励分数
   - 输出：标量奖励分数 r ∈ ℝ

5. 【训练过程】
   - 对每个批次：
     a) 将 (prompt, chosen) 格式化为正样本序列，计算奖励分数 r_pos
     b) 将 (prompt, rejected) 格式化为负样本序列，计算奖励分数 r_neg
     c) 计算损失：loss = f(r_pos, r_neg)，其中 f 是 Bradley-Terry 或 Margin Ranking 损失
     d) 反向传播更新模型参数
   - 训练指标：准确率 acc = (r_pos > r_neg).float().mean()
     表示模型正确区分正负样本的比例

6. 【关键特性】
   - Padding token ID = 2（在 forward 中通过 mask 忽略）
   - 使用双向编码器（不是生成式模型），可以同时看到整个序列
   - 通过平均池化将变长序列压缩为固定维度的表示
   - 输出是标量，不需要归一化到特定范围

7. 【应用场景】
   - 用于强化学习人类反馈（RLHF）流程
   - 在 PPO 训练中，奖励模型为生成的回复提供奖励信号
   - 帮助语言模型学习人类偏好，生成更符合人类期望的文本
"""
from __future__ import annotations
import torch, torch.nn as nn

class RewardModel(nn.Module):
    """奖励模型：使用 Transformer 编码器将输入序列编码为池化表示，然后输出标量奖励分数。
    
    使用双向编码器（Transformer Encoder）进行奖励建模是合适的，因为奖励模型不用于生成，
    只需要理解整个序列的语义来给出奖励分数。
    
    架构流程：Transformer 编码器 → 池化表示 → 标量奖励
    """
    def __init__(self, vocab_size: int, block_size: int, n_layer: int = 4, n_head: int = 4, n_embd: int = 256, dropout: float = 0.1):
        """
        初始化奖励模型。
        
        Args:
            vocab_size: 词汇表大小，即 token 的总数量
            block_size: 序列的最大长度（块大小）
            n_layer: Transformer 编码器的层数，默认为 4
            n_head: 多头注意力的头数，默认为 4
            n_embd: 嵌入维度，默认为 256
            dropout: Dropout 比率，默认为 0.1
        """
        super().__init__()
        self.vocab_size = vocab_size  # 词汇表大小
        self.block_size = block_size  # 序列最大长度
        
        # 词嵌入层：将 token ID 映射为向量表示
        self.tok_emb = nn.Embedding(vocab_size, n_embd)
        # 位置嵌入层：为每个位置提供位置信息
        self.pos_emb = nn.Embedding(block_size, n_embd)
        
        # Transformer 编码器层配置
        # d_model: 模型维度（嵌入维度）
        # nhead: 注意力头数
        # dim_feedforward: 前馈网络的隐藏层维度（通常为 4 倍嵌入维度）
        # activation: 激活函数使用 GELU
        # batch_first: 输入张量的第一个维度是批次大小
        enc_layer = nn.TransformerEncoderLayer(d_model=n_embd, nhead=n_head, dim_feedforward=4*n_embd,
                                               dropout=dropout, activation='gelu', batch_first=True)
        # 堆叠多个 Transformer 编码器层
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_layer)
        
        # 层归一化：稳定训练过程
        self.ln = nn.LayerNorm(n_embd)
        # 输出头：将池化后的表示映射为单个标量奖励分数
        self.head = nn.Linear(n_embd, 1)

    def forward(self, x: torch.Tensor):
        """
        前向传播：将输入序列转换为奖励分数。
        
        Args:
            x: 输入 token 序列，形状为 (B, T)，其中 B 是批次大小，T 是序列长度
               假设 padding token 的 ID 为 2
        
        Returns:
            r: 奖励分数，形状为 (B,)，每个样本对应一个标量奖励值
        """
        B, T = x.shape  # B: 批次大小, T: 序列长度
        
        # 生成位置索引：[0, 1, 2, ..., T-1]，并扩展为批次维度
        pos = torch.arange(T, device=x.device).unsqueeze(0)
        
        # 词嵌入 + 位置嵌入：将 token ID 和位置信息结合
        h = self.tok_emb(x) + self.pos_emb(pos)  # (B, T, n_embd)
        
        # 创建 padding mask：标记哪些位置是 padding（假设 padding token ID 为 2）
        # True 表示该位置是 padding，需要被 mask 掉
        pad_mask = (x == 2)
        
        # 通过 Transformer 编码器处理序列
        # src_key_padding_mask: 告诉编码器哪些位置是 padding，需要忽略
        h = self.encoder(h, src_key_padding_mask=pad_mask)  # (B, T, n_embd)
        
        # 层归一化
        h = self.ln(h)
        
        # 掩码平均池化：对所有非 padding 的 token 进行平均池化
        # 将 padding mask 反转（~pad_mask），True 表示有效 token
        mask = (~pad_mask).float().unsqueeze(-1)  # (B, T, 1)
        
        # 对有效 token 的隐藏状态求和
        h_sum = (h * mask).sum(dim=1)  # (B, n_embd)
        
        # 计算每个序列中有效 token 的数量（至少为 1，避免除零）
        len_ = mask.sum(dim=1).clamp_min(1.0)  # (B, 1)
        
        # 平均池化：得到序列的池化表示
        pooled = h_sum / len_  # (B, n_embd)
        
        # 通过线性层输出奖励分数，并移除最后一个维度
        r = self.head(pooled).squeeze(-1)  # (B,)
        return r


if __name__ == "__main__":
    """简单的测试代码，用于验证奖励模型的功能"""
    print("=" * 60)
    print("奖励模型测试")
    print("=" * 60)
    
    # 设置随机种子以便结果可复现
    torch.manual_seed(42)
    
    # 模型配置参数
    vocab_size = 1000  # 词汇表大小
    block_size = 128   # 序列最大长度
    n_layer = 4        # Transformer 层数
    n_head = 4         # 注意力头数
    n_embd = 256       # 嵌入维度
    batch_size = 2     # 批次大小
    seq_len = 64       # 实际序列长度（小于 block_size）
    
    print(f"\n【模型配置】")
    print(f"词汇表大小: {vocab_size}")
    print(f"序列最大长度: {block_size}")
    print(f"Transformer 层数: {n_layer}")
    print(f"注意力头数: {n_head}")
    print(f"嵌入维度: {n_embd}")
    print(f"批次大小: {batch_size}")
    print(f"实际序列长度: {seq_len}")
    
    # 创建模型实例
    print(f"\n【创建模型】")
    model = RewardModel(
        vocab_size=vocab_size,
        block_size=block_size,
        n_layer=n_layer,
        n_head=n_head,
        n_embd=n_embd,
        dropout=0.1
    )
    
    # 计算模型参数数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"模型总参数数量: {total_params:,}")
    print(f"可训练参数数量: {trainable_params:,}")
    
    # 创建示例输入
    # 第一个样本：正常序列 + padding
    # 第二个样本：较短的序列 + padding
    print(f"\n【创建输入数据】")
    # 生成随机 token ID（0 到 vocab_size-1）
    x1 = torch.randint(0, vocab_size-1, (seq_len,))
    x2 = torch.randint(0, vocab_size-1, (seq_len // 2,))
    
    # 添加 padding（padding token ID = 2）
    pad_token_id = 2
    x1_padded = torch.cat([x1, torch.full((block_size - seq_len,), pad_token_id)])
    x2_padded = torch.cat([x2, torch.full((block_size - seq_len // 2,), pad_token_id)])
    
    # 组合成批次
    x = torch.stack([x1_padded, x2_padded])
    
    print(f"输入张量形状: {x.shape}")
    print(f"输入张量内容（前10个token，第一个样本）: {x[0, :10].tolist()}")
    print(f"输入张量内容（前10个token，第二个样本）: {x[1, :10].tolist()}")
    print(f"第一个样本: {x[0]}")
    print(f"第二个样本: {x[1]}")
    print(f"Padding token ID: {pad_token_id}")
    print(f"第一个样本中 padding 的数量: {(x[0] == pad_token_id).sum().item()}")
    print(f"第二个样本中 padding 的数量: {(x[1] == pad_token_id).sum().item()}")
    
    # 前向传播
    print(f"\n【前向传播】")
    model.eval()  # 设置为评估模式
    with torch.no_grad():
        rewards = model(x)
    
    print(f"输出奖励分数形状: {rewards.shape}")
    print(f"输出奖励分数值: {rewards.tolist()}")
    print(f"第一个样本的奖励分数: {rewards[0].item():.4f}")
    print(f"第二个样本的奖励分数: {rewards[1].item():.4f}")
    
    # 测试不同长度的输入
    print(f"\n【测试不同序列长度】")
    test_lengths = [16, 32, 64, 96]
    for length in test_lengths:
        test_x = torch.randint(0, vocab_size-1, (1, length))
        test_x_padded = torch.cat([test_x.squeeze(0), torch.full((block_size - length,), pad_token_id)]).unsqueeze(0)
        with torch.no_grad():
            test_reward = model(test_x_padded)
        print(f"序列长度 {length:3d}: 奖励分数 = {test_reward[0].item():.4f}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)