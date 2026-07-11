"""
1.3 单头自注意力机制（Single-Head Self-Attention）
Single-head attention with explicit shape tracking

自注意力机制的作用：
- 让序列中的每个token能够关注到序列中的所有其他token
- 通过计算Query、Key、Value三个矩阵来实现注意力权重的计算
- 使用缩放点积注意力（Scaled Dot-Product Attention）机制
"""
import math
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from attn_mask import causal_mask

class SingleHeadSelfAttention(nn.Module):
    """
    单头自注意力机制（Single-Head Self-Attention）
    
    原理：
    - 自注意力允许模型在处理每个位置时，关注输入序列的所有位置
    - 通过三个线性变换将输入映射为Query、Key、Value
    - 计算Query和Key的点积得到注意力分数
    - 使用Softmax将分数归一化为概率分布
    - 用注意力权重对Value进行加权求和
    
    核心公式：
        Attention(Q, K, V) = softmax(Q·K^T / sqrt(d_k)) · V
    
    其中：
    - Q (Query): 查询矩阵，表示"我想要什么信息"
    - K (Key): 键矩阵，表示"我有什么信息"
    - V (Value): 值矩阵，表示"实际的信息内容"
    - d_k: Key的维度，用于缩放防止点积过大
    """
    def __init__(self, d_model: int, d_k: int, dropout: float = 0.0, trace_shapes: bool = False):
        """
        初始化单头自注意力层
        参数：
            d_model: 输入的模型维度（embedding维度）
            d_k: Query、Key、Value的目标维度（注意力头的维度）
            dropout: Dropout概率，用于正则化注意力权重
            trace_shapes: 是否打印中间张量的形状（用于调试）
        """
        super().__init__()
        # 创建三个线性投影层，将输入从d_model维映射到d_k维
        # 不使用bias，这是Transformer中的标准做法
        self.q = nn.Linear(d_model, d_k, bias=False)  # Query投影
        self.k = nn.Linear(d_model, d_k, bias=False)  # Key投影
        self.v = nn.Linear(d_model, d_k, bias=False)  # Value投影
        
        # Dropout层，用于在训练时随机丢弃一些注意力权重，防止过拟合
        self.dropout = nn.Dropout(dropout)
        
        # 是否打印形状信息（调试用）
        self.trace_shapes = trace_shapes

    def forward(self, x: torch.Tensor):
        """
        前向传播：计算自注意力
        
        参数：
            x: 输入张量，形状为 (B, T, d_model)
               B = batch_size (批次大小)
               T = sequence_length (序列长度)
               d_model = embedding_dimension (嵌入维度)
        
        返回：
            out: 注意力输出，形状为 (B, T, d_k)
            w: 注意力权重矩阵，形状为 (B, T, T)，表示每个位置对其他位置的关注程度
        """
        # 获取输入的批次大小和序列长度
        B, T, _ = x.shape
        
        # 步骤1: 通过线性层计算Query、Key、Value
        # 每个形状都是 (B, T, d_k)
        q = self.q(x)  # Query: "我想要什么信息"
        k = self.k(x)  # Key: "我有什么信息"
        v = self.v(x)  # Value: "实际的信息内容"
        
        if self.trace_shapes:
            print(f"q {q.shape}  k {k.shape}  v {v.shape}")
        
        # 步骤2: 计算缩放因子
        # 使用 1/sqrt(d_k) 来缩放点积，防止梯度消失
        # 当d_k很大时，点积的方差会很大，导致softmax进入饱和区
        scale = 1.0 / math.sqrt(q.size(-1))
        
        # 步骤3: 计算注意力分数（未归一化）
        # Q·K^T 得到每对位置之间的相似度
        # transpose(-2, -1) 交换最后两个维度：(B,T,d_k) -> (B,d_k,T)
        # matmul结果形状: (B,T,d_k) × (B,d_k,T) -> (B,T,T)
        attn = torch.matmul(q, k.transpose(-2, -1)) * scale
        
        # 步骤4: 应用因果掩码（Causal Mask）
        # 在自回归生成任务中，每个位置只能看到它之前的位置
        # 掩码会将"未来"位置的注意力分数设为-inf，softmax后变为0
        mask = causal_mask(T, device=x.device)  # 形状: (1, T, T) 或 (T, T)
        attn = attn.masked_fill(mask.squeeze(1), float('-inf'))
        
        # 步骤5: 使用Softmax归一化注意力分数
     
        
        # dim=-1 表示在最后一个维度（T维度）上做softmax
        w = F.softmax(attn, dim=-1)  # 形状: (B, T, T)
        
        # 步骤6: 应用Dropout（训练时随机丢弃部分注意力连接）
        w = self.dropout(w)
        
        # 步骤7: 用注意力权重对Value进行加权求和
        # (B,T,T) × (B,T,d_k) -> (B,T,d_k)
        # 每个位置的输出是所有位置Value的加权和，权重由注意力决定
        out = torch.matmul(w, v)
        
        if self.trace_shapes:
            print(f"weights {w.shape}  out {out.shape}")
        
        # 返回输出和注意力权重（权重可用于可视化）
        return out, w


# ============================================================================
# 测试代码
# ============================================================================
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 80)
    print("单头自注意力机制测试 (Single-Head Self-Attention Test)")
    print("=" * 80)
    
    # 设置参数
    d_model = 32       # 输入的模型维度
    d_k = 16           # 注意力头的维度
    batch_size = 2     # 批次大小
    seq_len = 5       # 序列长度
    dropout = 0.1      # Dropout概率
    
    print(f"\n ===== step1: 参数配置: =====\n")
    print(f"  - 输入模型维度 (d_model): {d_model}")
    print(f"  - 注意力头维度 (d_k): {d_k}")
    print(f"  - 批次大小 (batch_size): {batch_size}")
    print(f"  - 序列长度 (seq_len): {seq_len}")
    print(f"  - Dropout概率: {dropout}")
    
    # 创建单头自注意力实例
    print(f"\n ===== step2: 创建单头自注意力层: =====\n")
    attn_layer = SingleHeadSelfAttention(
        d_model=d_model,
        d_k=d_k,
        dropout=dropout,
        trace_shapes=False  # 先关闭内部形状打印，我们手动打印
    )
    print(f"✓ 创建成功")
    
    # 打印模型参数信息
    print(f"\n ===== step3: 模型参数: =====\n")
    total_params = sum(p.numel() for p in attn_layer.parameters())
    print(f"  - Q投影层参数: {d_model} × {d_k} = {d_model * d_k}")
    print(f"  - K投影层参数: {d_model} × {d_k} = {d_model * d_k}")
    print(f"  - V投影层参数: {d_model} × {d_k} = {d_model * d_k}")
    print(f"  - 总参数量: {total_params}")
    
    # 创建随机输入（模拟token embeddings）
    print(f"\n ===== step4: 创建随机输入: =====\n")
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"输入张量形状: {x.shape}\n")
    print(f"输入张量: {x}\n")
    
    # 手动追踪forward过程
    with torch.no_grad():  # 测试时不需要计算梯度   
        print(f"\n ===== step5: 计算 Query、Key、Value: =====\n")
        q = attn_layer.q(x)
        k = attn_layer.k(x)
        v = attn_layer.v(x)
        print(f"  Query形状: {q.shape}")
        print(f"  Key形状:   {k.shape}")
        print(f"  Value形状: {v.shape}")
        print(f"  说明: 所有投影后的形状都是 (batch_size={batch_size}, seq_len={seq_len}, d_k={d_k})")
        print(f"Query: {q}\n")
        print(f"Key: {k}\n")
        print(f"Value: {v}\n")
        
        print(f"\n ===== step6: 计算缩放因子: =====\n")
        scale = 1.0 / math.sqrt(q.size(-1))
        print(f"  缩放因子: {scale:.6f}")
        print(f"  说明: 1/sqrt(d_k) = 1/sqrt({d_k}) = {scale:.6f}")
        
        print(f"\n ===== step7: 计算注意力分数 (Q·K^T): =====\n")
        k_transposed = k.transpose(-2, -1)
        print(f"  Key转置后形状: {k_transposed.shape}\n")
        
        attn_scores = torch.matmul(q, k_transposed) * scale
        print(f"  注意力分数形状: {attn_scores.shape}\n")
        print(f"  说明: Q({q.shape}) × K^T({k_transposed.shape}) = ({attn_scores.shape})")
        print(f"        每个位置对其他位置的相似度分数")
        print(f"attn_scores: {attn_scores[:1,:,:].numpy()}")
        
        print(f"\n ===== step8: 应用因果掩码: =====\n")
        mask = causal_mask(seq_len, device=x.device)
        print(f"  掩码形状: {mask.shape}\n")
        
        attn_masked = attn_scores.masked_fill(mask.squeeze(1), float('-inf'))
        print(f"  掩码后形状: {attn_masked.shape}\n")
        print(f"  说明: 将未来位置的分数设为-inf，保证自回归特性\n")
        print(f"attn_masked: {attn_masked[:1,:,:].numpy()}\n")
        
        print(f"\n ===== step9: Softmax归一化: =====\n")
        attn_weights = F.softmax(attn_masked, dim=-1)
        print(f"  注意力权重形状: {attn_weights.shape}")
        print(f"  说明: 每行的权重和为1，表示概率分布")
        print(f"attn_weights: {attn_weights[:1,:,:].numpy()}")
        
        print(f"\n ===== step10: 应用Dropout (测试模式下跳过): =====\n")
        attn_weights_dropout = attn_layer.dropout(attn_weights)
        print(f"  Dropout后形状: {attn_weights_dropout.shape}\n")
        print(f"attn_weights_dropout: {attn_weights_dropout[:1,:,:].numpy()}\n")
        
        print(f"\n ===== step11: 加权求和 (Attention_Weights × V): =====\n")
        output = torch.matmul(attn_weights_dropout, v)
        print(f"  输出形状: {output.shape}")
        print(f"  说明: Weights({attn_weights_dropout.shape}) × V({v.shape}) = ({output.shape})")
        print(f"        每个位置的输出是所有位置Value的加权和")
        print(f"output: {output[:1,:,:].numpy()}\n")
    
    # 使用完整的forward方法验证
    print(f"\n ===== step12: 完整前向传播测试: =====\n")
    output_full, weights_full = attn_layer(x)
    print(f"输入形状:   {x.shape}\n")
    print(f"输出形状:   {output_full.shape}\n")
    print(f"权重形状:   {weights_full.shape}\n")
    print(f"输出: {output_full}\n")
    print(f"权重: {weights_full}\n")
    
    # 验证形状是否正确
    assert output_full.shape == (batch_size, seq_len, d_k), "输出形状不正确！"
    assert weights_full.shape == (batch_size, seq_len, seq_len), "权重形状不正确！"
    print(f"\n✓ 形状验证通过\n")
    
    # 分析注意力权重
    print(f"\n ===== step13: 注意力权重分析: =====\n")
    print("注意力权重分析")
    print(f"第一个样本的注意力权重矩阵 (前5×5):\n")
    print(f"行: 当前位置, 列: 关注的位置\n")
    print(f"注意力权重: {weights_full[0]}\n")
    
    # 验证因果掩码是否生效
    print(f"\n ===== step14: 验证因果掩码 (上三角应该都为0): =====\n")
    w0 = weights_full[0]
    print(f"位置0只能看到自己: 非零权重数 = {(w0[0] > 1e-6).sum()}")
    print(f"位置1可以看到0和1: 非零权重数 = {(w0[1] > 1e-6).sum()}")
    print(f"位置2可以看到0,1,2: 非零权重数 = {(w0[2] > 1e-6).sum()}")
    
    # 统计信息
    print(f"\n ===== step15: 注意力权重统计: =====\n")
    print(f"  - 均值: {weights_full.mean().item():.6f}")
    print(f"  - 标准差: {weights_full.std().item():.6f}\n")
    print(f"  - 最小值: {weights_full.min().item():.6f}\n")
    print(f"  - 最大值: {weights_full.max().item():.6f}\n")
    
    print("\n ===== step16: 测试完成！: =====\n")
    print("测试完成！")
    print("=" * 80)
    print("\n核心要点:")
    print("  1. 输入经过Q、K、V三个线性变换，维度从d_model变为d_k")
    print("  2. Q·K^T计算相似度，得到(seq_len × seq_len)的注意力分数矩阵")
    print("  3. 因果掩码确保每个位置只能看到它之前的位置")
    print("  4. Softmax将分数转换为概率分布")
    print("  5. 用注意力权重对Value加权求和，得到最终输出")
    print("=" * 80)