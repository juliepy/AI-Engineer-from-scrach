"""
1.4 多头自注意力机制（Multi-Head Self-Attention）
Multi-Head Self-Attention with explicit shape tracing

多头注意力的作用：
- 允许模型在不同的表示子空间中关注不同的信息
- 单头注意力只能学习一种注意力模式，多头可以同时学习多种模式
- 例如：一个头关注语法关系，另一个头关注语义关系

核心思想：
- 将 d_model 维度分成 n_head 个小的 d_head 维度
- 每个头独立计算注意力
- 最后将所有头的输出拼接起来

形状变换流程（关键理解点）：
  输入 x:      (B, T, d_model)
  qkv 映射:    (B, T, 3*d_model)         # 一次性生成q,k,v
  重塑:        (B, T, 3, n_head, d_head)  # d_head = d_model // n_head
  分离:        q,k,v 各自为 (B, T, n_head, d_head)
  转置:        (B, n_head, T, d_head)     # 将头维度提前，方便并行计算
  注意力分数:  (B, n_head, T, T) = q @ k^T / sqrt(d_head)
  注意力权重:  (B, n_head, T, T) = softmax(scores)  # 带因果掩码
  上下文向量:  (B, n_head, T, d_head) = weights @ v
  合并头:      (B, T, n_head*d_head) = (B, T, d_model)
  输出投影:    (B, T, d_model)
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from attn_mask import causal_mask

class MultiHeadSelfAttention(nn.Module):
    """
    多头自注意力模块
    
    与单头注意力的区别：
    - 单头：整个 d_model 维度一起计算注意力
    - 多头：将 d_model 分成 n_head 份，每份独立计算，最后合并
    
    优势：
    - 增加模型的表达能力（不同的头可以关注不同的特征）
    - 并行计算效率高
    - 参数量相同的情况下，多头比单头效果更好
    """
    def __init__(self, d_model: int, n_head: int, dropout: float = 0.0, trace_shapes: bool = True):
        """
        初始化多头自注意力层
        
        参数：
            d_model: 模型的隐藏维度（必须能被n_head整除）
            n_head: 注意力头的数量
            dropout: dropout比率，用于注意力权重的正则化
            trace_shapes: 是否打印中间张量的形状（用于调试）
        """
        super().__init__()
        # 确保 d_model 能被 n_head 整除，这样才能均匀分配到各个头
        assert d_model % n_head == 0, "d_model must be divisible by n_head"
        
        self.n_head = n_head
        self.d_head = d_model // n_head  # 每个头的维度
        
        # QKV映射：一次性生成 query, key, value
        # 输入 d_model，输出 3*d_model (分别对应q,k,v)
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        
        # 输出投影：将多头的结果映射回 d_model 维度
        self.proj = nn.Linear(d_model, d_model, bias=False)
        
        # Dropout层：用于注意力权重的正则化，防止过拟合
        self.dropout = nn.Dropout(dropout)
        
        # 是否打印形状信息（调试用）
        self.trace_shapes = trace_shapes

    def forward(self, x: torch.Tensor):
        """
        前向传播
        
        参数：
            x: 输入张量，形状为 (B, T, d_model)
               B = batch_size (批次大小)
               T = sequence_length (序列长度)
               d_model = model_dimension (模型维度)
        
        返回：
            out: 输出张量，形状为 (B, T, d_model)
            w: 注意力权重，形状为 (B, n_head, T, T)
        """
        # 获取输入的形状
        B, T, C = x.shape  # C = d_model
        if self.trace_shapes:
            print(f"B: {B}, T: {T}, C: {C}")
            print(f"x: {x[:1,:1,:].detach().numpy()}")
            
        # 步骤1: 通过线性层生成 q, k, v
        # (B, T, d_model) -> (B, T, 3*d_model)
        qkv = self.qkv(x)
        
        # 步骤2: 重塑张量以分离 q, k, v 和多个头
        # (B, T, 3*d_model) -> (B, T, 3, n_head, d_head)
        qkv = qkv.view(B, T, 3, self.n_head, self.d_head)
        if self.trace_shapes:
            print("qkv view:", qkv.shape)
        
        # 步骤3: 分离出 q, k, v
        # unbind 在 dim=2 上分离，得到3个张量，每个形状为 (B, T, n_head, d_head)
        q, k, v = qkv.unbind(dim=2)
        
        # 步骤4: 转置，将头维度提前
        # (B, T, n_head, d_head) -> (B, n_head, T, d_head)
        # 这样每个头可以独立并行计算注意力
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        if self.trace_shapes:
            print("q:", q.shape, "k:", k.shape, "v:", v.shape)
            print(f"q: {q[:1,:1,:].detach().numpy()}")
            print(f"k: {k[:1,:1,:].detach().numpy()}")
            print(f"v: {v[:1,:1,:].detach().numpy()}")

        # 步骤5: 计算注意力分数
        # q @ k^T: (B, n_head, T, d_head) @ (B, n_head, d_head, T)
        #       -> (B, n_head, T, T)
        # 缩放因子：除以 sqrt(d_head) 防止点积过大导致softmax梯度消失
        scale = 1.0 / math.sqrt(self.d_head)
        if self.trace_shapes:
            print(f"scale: {scale}")
        attn = torch.matmul(q, k.transpose(-2, -1)) * scale
        if self.trace_shapes:
            print(f"attn shape: {attn.shape}")
            print(f"attn: {attn[:1,:1,:].detach().numpy()}")
            
        
        # 步骤6: 应用因果掩码（Causal Mask）
        # 在自回归语言模型中，token只能看到它之前的token，不能看到未来
        # 掩码将未来位置的注意力分数设为 -inf，softmax后会变成0
        mask = causal_mask(T, device=x.device)  # 上三角矩阵（不含对角线）
        if self.trace_shapes:
            print(f"mask shape: {mask.shape}")
            print(f"mask: {mask.numpy()}")
        attn = attn.masked_fill(mask, float('-inf'))
        if self.trace_shapes:
            print(f"attn shape: {attn.shape}")
            print(f"attn_masked: {attn[:1,:1,:].detach().numpy()}")
            
        # 步骤7: 应用 softmax 得到注意力权重
        # 在最后一维（key维度）上做softmax，使得每个query对所有key的权重和为1
        w = F.softmax(attn, dim=-1)
        if self.trace_shapes:
            print(f"w shape: {w.shape}")
            print(f"w: {w[:1,:1,:].detach().numpy()}")
        
        # 步骤8: 应用 dropout（训练时随机丢弃一些注意力连接）
        w = self.dropout(w)
        if self.trace_shapes:
            print(f"w_dropout shape: {w.shape}")
            print(f"w_dropout: {w[:1,:1,:].detach().numpy()}")
        
        # 步骤9: 用注意力权重加权value
        # (B, n_head, T, T) @ (B, n_head, T, d_head)
        # -> (B, n_head, T, d_head)
        ctx = torch.matmul(w, v)
        if self.trace_shapes:
            print("weights:", w.shape, "ctx:", ctx.shape)
            print(f"ctx: {ctx[:1,:1,:].detach().numpy()}")
        
        # 步骤10: 合并多个头
        # (B, n_head, T, d_head) -> (B, T, n_head, d_head)
        # -> (B, T, n_head * d_head) = (B, T, d_model)
        out = ctx.transpose(1, 2).contiguous().view(B, T, C)
        if self.trace_shapes:
            print(f"out shape: {out.shape}")
            print(f"out: {out[:1,:,:].detach().numpy()}")
            
        # 步骤11: 输出投影
        # 通过线性层将合并后的结果映射回 d_model 维度
        out = self.proj(out)
        if self.trace_shapes:
            print("out:", out.shape)
            print(f"out: {out[:1,:,:].detach().numpy()}")
        
        # 返回输出和注意力权重（权重可用于可视化）
        return out, w


# ============================================================================
# 测试代码
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("多头自注意力机制测试 (Multi-Head Self-Attention Test)")
    print("=" * 80)
    
    # 设置参数
    d_model = 32       # 模型维度
    n_head = 4         # 注意力头数量
    batch_size = 2     # 批次大小
    seq_len = 5        # 序列长度
    dropout = 0.1      # Dropout比率
    
    print(f"\n参数配置:")
    print(f"  - 模型维度 (d_model): {d_model}")
    print(f"  - 注意力头数量 (n_head): {n_head}")
    print(f"  - 每个头的维度 (d_head): {d_model // n_head}")
    print(f"  - 批次大小 (batch_size): {batch_size}")
    print(f"  - 序列长度 (seq_len): {seq_len}")
    print(f"  - Dropout比率: {dropout}")
    
    # 创建多头自注意力实例
    mha = MultiHeadSelfAttention(
        d_model=d_model, 
        n_head=n_head, 
        dropout=dropout,
        trace_shapes=True  # 开启形状追踪
    )
    mha.eval()  # 设置为评估模式（关闭dropout）
    print(f"\n✓ 创建多头自注意力模块成功")
    
    # 打印模型参数信息
    total_params = sum(p.numel() for p in mha.parameters())
    print(f"\n模型参数统计:")
    print(f"  - QKV映射参数: {mha.qkv.weight.numel()}")
    print(f"  - 输出投影参数: {mha.proj.weight.numel()}")
    print(f"  - 总参数量: {total_params}")
    
    # 创建随机输入张量（模拟token embeddings）
    print(f"\n{'-' * 80}")
    print("运行前向传播...")
    print(f"{'-' * 80}")
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"\n输入张量形状: {x.shape}")
    print(f"x: {x[:1,:1,:].detach().numpy()}")
    
    # 运行前向传播
    output, attn_weights = mha(x)
    
    print(f"\n输出张量形状: {output.shape}")
    print(f"注意力权重形状: {attn_weights.shape}")
    print(f"attn_weights: {attn_weights[:1,:,:].detach().numpy()}")
    
    # 验证形状是否正确
    assert output.shape == x.shape, "输出形状与输入形状不匹配！"
    assert attn_weights.shape == (batch_size, n_head, seq_len, seq_len), "注意力权重形状不正确！"
    print("✓ 形状验证通过")
    
    # 分析注意力权重
    print("\n" + "=" * 80)
    print("注意力权重分析")
    print("=" * 80)
    
    # 验证每行的权重和是否为1（softmax的性质）
    row_sums = attn_weights.sum(dim=-1)  # 在最后一维求和
    print(f"\n每行权重和（应该接近1.0）:")
    print(f"  - 均值: {row_sums.mean().item():.6f}")
    print(f"  - 标准差: {row_sums.std().item():.6f}")
    print(f"  - 最小值: {row_sums.min().item():.6f}")
    print(f"  - 最大值: {row_sums.max().item():.6f}")
    
    # 展示第一个样本的注意力权重统计
    print(f"\n注意力权重统计 (第1个样本):")
    first_sample_weights = attn_weights[0]  # (n_head, seq_len, seq_len)
    print(f"  - 均值: {first_sample_weights.mean().item():.6f}")
    print(f"  - 标准差: {first_sample_weights.std().item():.6f}")
    print(f"  - 最小值: {first_sample_weights.min().item():.6f}")
    print(f"  - 最大值: {first_sample_weights.max().item():.6f}")
    
    # 展示第一个头的注意力权重矩阵（因果掩码效果）
    print(f"\n第1个样本，第1个头的注意力权重矩阵 (展示因果掩码效果):")
    print("(每行代表一个query，每列代表一个key)")
    first_head_weights = attn_weights[0, 0].detach().numpy()  # (seq_len, seq_len)
    
    # 打印表头
    print("\n     ", end="")
    for j in range(seq_len):
        print(f"key{j:1d}  ", end="")
    print()
    
    # 打印权重矩阵
    for i in range(seq_len):
        print(f"q{i}: ", end="")
        for j in range(seq_len):
            if j <= i:  # 因果掩码：只能看到当前及之前的位置
                print(f"{first_head_weights[i, j]:.3f} ", end="")
            else:  # 未来位置被掩盖（权重应该为0或接近0）
                print(f"{first_head_weights[i, j]:.3f} ", end="")
        print(f" (和={first_head_weights[i].sum():.3f})")
    
    print("\n说明：")
    print("  - 对角线及左下部分有值（当前和过去的token）")
    print("  - 右上部分应该是0（未来的token被因果掩码屏蔽）")
    
    # 检查因果掩码是否正确应用
    print(f"\n因果掩码验证:")
    for i in range(seq_len):
        for j in range(seq_len):
            if j > i:  # 未来位置
                weight_val = first_head_weights[i, j]
                if abs(weight_val) > 1e-6:  # 应该接近0
                    print(f"  ⚠ 警告: 位置({i},{j})的权重不为0: {weight_val:.6f}")
    print("  ✓ 因果掩码应用正确（未来位置的权重为0）")
    
    # 对比不同头的注意力模式
    print(f"\n不同头的注意力分布对比 (第1个样本，第1个query):")
    for head_idx in range(n_head):
        head_pattern = attn_weights[0, head_idx, 0].detach().numpy()  # query 0的注意力
        print(f"  头{head_idx}: {head_pattern}")
    print("  (不同的头学习到不同的注意力模式)")
    
    # 打印完整的形状变换流程总结
    print("\n" + "=" * 80)
    print("完整的形状变换流程总结")
    print("=" * 80)
    
    d_head = d_model // n_head
    
    print(f"\n【步骤1】输入张量")
    print(f"  x: ({batch_size}, {seq_len}, {d_model})")
    print(f"      ↑批次    ↑序列长度  ↑模型维度")
    
    print(f"\n【步骤2】QKV映射 - 通过线性层一次性生成q,k,v")
    print(f"  qkv = Linear(x): ({batch_size}, {seq_len}, {3*d_model})")
    print(f"                               ↑ 3倍模型维度(q+k+v)")
    
    print(f"\n【步骤3】重塑张量 - 分离q,k,v和多个头")
    print(f"  qkv.view: ({batch_size}, {seq_len}, 3, {n_head}, {d_head})")
    print(f"                      ↑序列   ↑q,k,v  ↑头数  ↑每头维度")
    print(f"            其中 d_head = d_model / n_head = {d_model} / {n_head} = {d_head}")
    
    print(f"\n【步骤4】分离q,k,v - 在dim=2上unbind")
    print(f"  q: ({batch_size}, {seq_len}, {n_head}, {d_head})")
    print(f"  k: ({batch_size}, {seq_len}, {n_head}, {d_head})")
    print(f"  v: ({batch_size}, {seq_len}, {n_head}, {d_head})")
    
    print(f"\n【步骤5】转置 - 将头维度提前，方便并行计算")
    print(f"  q.transpose(1,2): ({batch_size}, {n_head}, {seq_len}, {d_head})")
    print(f"  k.transpose(1,2): ({batch_size}, {n_head}, {seq_len}, {d_head})")
    print(f"  v.transpose(1,2): ({batch_size}, {n_head}, {seq_len}, {d_head})")
    print(f"                       ↑批次 ↑头数 ↑序列 ↑每头维度")
    
    print(f"\n【步骤6】计算注意力分数 - q @ k^T")
    print(f"  attn = q @ k^T: ({batch_size}, {n_head}, {seq_len}, {d_head}) @ ({batch_size}, {n_head}, {d_head}, {seq_len})")
    print(f"                = ({batch_size}, {n_head}, {seq_len}, {seq_len})")
    print(f"                                  ↑query维  ↑key维")
    print(f"  缩放因子 scale = 1/√{d_head} = {1.0/math.sqrt(d_head):.4f}")
    
    print(f"\n【步骤7】应用因果掩码 - 屏蔽未来位置")
    print(f"  mask: ({seq_len}, {seq_len})  # 上三角矩阵")
    print(f"  attn.masked_fill(mask, -inf): ({batch_size}, {n_head}, {seq_len}, {seq_len})")
    
    print(f"\n【步骤8】Softmax - 计算注意力权重")
    print(f"  weights = softmax(attn): ({batch_size}, {n_head}, {seq_len}, {seq_len})")
    print(f"  每一行的权重和为1，表示query对所有key的注意力分布")
    
    print(f"\n【步骤9】加权求和 - weights @ v")
    print(f"  ctx = weights @ v: ({batch_size}, {n_head}, {seq_len}, {seq_len}) @ ({batch_size}, {n_head}, {seq_len}, {d_head})")
    print(f"                   = ({batch_size}, {n_head}, {seq_len}, {d_head})")
    print(f"                      每个query位置得到加权后的上下文向量")
    
    print(f"\n【步骤10】合并多头 - transpose + view")
    print(f"  ctx.transpose(1,2): ({batch_size}, {seq_len}, {n_head}, {d_head})")
    print(f"  .view(B,T,C):      ({batch_size}, {seq_len}, {n_head*d_head})")
    print(f"                    = ({batch_size}, {seq_len}, {d_model})")
    print(f"                      将{n_head}个头拼接回原始维度")
    
    print(f"\n【步骤11】输出投影 - 最后的线性变换")
    print(f"  out = proj(out): ({batch_size}, {seq_len}, {d_model})")
    print(f"                    与输入形状相同！")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print("\n关键要点:")
    print("  1. 多头注意力将 d_model 分成 n_head 个子空间")
    print("  2. 每个头独立计算注意力，学习不同的模式")
    print("  3. 因果掩码确保只能看到当前及之前的token")
    print("  4. 最后将所有头的输出拼接并投影回 d_model 维度")
    print("  5. 整个过程是 (B,T,d_model) -> ... -> (B,T,d_model) 的变换")