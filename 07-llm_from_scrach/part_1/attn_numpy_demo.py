"""1.2 Self-attention from first principles on a tiny example (NumPy only).
我们使用 T=3 个 tokens, d_model=4, d_k=d_v=4, 单头注意力。
这个脚本打印中间张量，以便追踪数学计算过程。

维度总结 (单头注意力)
--------------------------------
X:          (B=1, T=3, d_model=4)  - 输入序列
Wq/Wk/Wv:   (d_model=4, d_k=4)     - Query/Key/Value 权重矩阵
Q,K,V:      (1, 3, 4)              - 投影后的 Query/Key/Value
Scores:     (1, 3, 3)              - 注意力分数 = Q @ K^T
Weights:    (1, 3, 3)              - softmax 后的注意力权重
Output:     (1, 3, 4)              - 输出 = Weights @ V
"""
import numpy as np

# 设置 NumPy 输出格式：保留4位小数，不使用科学计数法
np.set_printoptions(precision=4, suppress=True)

# ========== 1. 定义输入数据 ==========
# 玩具输入数据 (batch=1, seq_len=3, d_model=4)
# 模拟3个 token 的嵌入向量，每个 token 用4维向量表示
X = np.array([[[0.1, 0.2, 0.3, 0.4],  # Token 1 的嵌入向量
               [0.5, 0.4, 0.3, 0.2],  # Token 2 的嵌入向量
               [0.0, 0.1, 0.0, 0.1]]], dtype=np.float32)  # Token 3 的嵌入向量

print("=" * 50)
print("步骤 0: 定义输入数据")
print("=" * 50)
print("X shape:", X.shape, "\nX=\n", X[0])

# ========== 2. 定义权重矩阵 ==========
# 权重矩阵 (在真实模型中通过训练学习得到)。这里我们固定数值以保证结果可复现。
# 单头：d_model=4, d_k=d_v=4，投影前后维度相同

# Query 权重矩阵：用于生成查询向量 (d_model=4, d_k=4)
Wq = np.array([[ 0.2, -0.1,  0.05,  0.0 ],
               [ 0.0,  0.1, -0.05,  0.1 ],
               [ 0.1,  0.2,  0.0,  -0.1 ],
               [-0.1,  0.0,  0.15,  0.05]], dtype=np.float32)

# Key 权重矩阵：用于生成键向量 (d_model=4, d_k=4)
Wk = np.array([[ 0.1,  0.1,  0.0,   0.05],
               [ 0.0, -0.1,  0.1,   0.0 ],
               [ 0.2,  0.0, -0.05,  0.1 ],
               [ 0.0,  0.2,  0.05, -0.1]], dtype=np.float32)

# Value 权重矩阵：用于生成值向量 (d_model=4, d_v=4)
Wv = np.array([[ 0.1,  0.0,  0.05, -0.05],
               [-0.1,  0.1,  0.0,   0.1 ],
               [ 0.2, -0.1,  0.1,   0.0 ],
               [ 0.0,  0.2, -0.1,   0.15]], dtype=np.float32)

# ========== 3. 投影到 Q, K, V ==========
# 通过矩阵乘法将输入投影到查询、键、值空间
Q = X @ Wq  # Query:  (1, 3, 4) - 每个 token 的查询向量
K = X @ Wk  # Key:    (1, 3, 4) - 每个 token 的键向量
V = X @ Wv  # Value:  (1, 3, 4) - 每个 token 的值向量 (3,4) * (4,4) = (3,4)

print("=" * 50)
print("步骤 1: 投影到 Query, Key, Value")
print("=" * 50)
print("Q shape:", Q.shape, "\nQ=\n", Q[0])
print("\nK shape:", K.shape, "\nK=\n", K[0])
print("\nV shape:", V.shape, "\nV=\n", V[0])

# ========== 4. 计算注意力分数 ==========
# 使用缩放点积注意力：Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V
scale = 1.0 / np.sqrt(Q.shape[-1])  # 缩放因子 = 1/sqrt(d_k)，防止点积过大
attn_scores = (Q @ K.transpose(0, 2, 1)) * scale  # (1, 3, 3) - 每对 token 之间的相似度

print("\n" + "=" * 50)
print("步骤 2: 计算注意力分数 (scaled dot-product)")
print("=" * 50)
print(f"缩放因子: {scale:.4f}")
print("原始注意力分数 (QK^T / sqrt(d_k)):\n", attn_scores[0])
print("attention shape: ", attn_scores.shape)
print("matrix attention score: ", attn_scores)

# ========== 5. 应用因果掩码 ==========
# 因果掩码：上三角区域设为 -inf，使得 softmax 后为0
# 这确保每个 token 只能关注它自己和之前的 token (自回归特性)
mask = np.triu(np.ones((1, 3, 3), dtype=bool), k=1)  # k=1 表示主对角线上方
attn_scores = np.where(mask, -1e9, attn_scores)

print("\n因果掩码后的注意力分数:")
print(attn_scores[0])
print("attenshion shape: ", attn_scores.shape)
print("attention matrix: ", attn_scores)

# ========== 6. 计算注意力权重 ==========
# 对最后一维应用 softmax，得到归一化的注意力权重
weights = np.exp(attn_scores - attn_scores.max(axis=-1, keepdims=True))  # 数值稳定性技巧
weights = weights / weights.sum(axis=-1, keepdims=True)  # 归一化

print("\n" + "=" * 50)
print("步骤 3: Softmax 归一化得到注意力权重")
print("=" * 50)
print("Weights shape:", weights.shape, "\nAttention Weights (causal)=\n", weights[0])
print("\n注意：每行和为1，且上三角为0 (因果掩码)")
print("weights shape: ", weights.shape)
print("weights matrix: ", weights)

# ========== 7. 计算输出 ==========
# 用注意力权重对值向量进行加权求和
# 每个 token 的输出是所有 token 值向量的加权组合
out = weights @ V  # (1, 3, 4) - 最终的自注意力输出

print("\n" + "=" * 50)
print("步骤 4: 加权求和得到最终输出")
print("=" * 50)
print("Output shape:", out.shape, "\nOutput=\n", out[0])
print("\n每个 token 的输出是其可见 token 值向量的加权和")
print("例如：Token 0 只看到自己")
print("     Token 1 看到 Token 0 和 1")
print("     Token 2 看到所有 Token 0, 1, 2")


# ========== 8. 输出投影 (完整 Transformer 所需) ==========
# 在完整的 Transformer 中，输出投影 W_o 混合各通道信息
# 单头且 d_v=d_model=4 时，out 已是 (1,3,4)，W_o 做通道混合而非升维
print("\n" + "=" * 50)
print("步骤 5: 输出投影")
print("=" * 50)

# 输出投影矩阵：(d_v=4, d_model=4)
W_o = np.array([[ 0.3,  0.1, -0.2,  0.4],
                [-0.1,  0.2,  0.3, -0.1],
                [ 0.2, -0.1,  0.1,  0.2],
                [ 0.0,  0.15, -0.05, 0.3]], dtype=np.float32)

print(f"输出投影矩阵 W_o 的形状: {W_o.shape} - (d_v=4, d_model=4)")

# 执行输出投影
final_out = out @ W_o  # (1, 3, 4) @ (4, 4) = (1, 3, 4)

print(f"\n最终输出形状: {final_out.shape} - 与输入 X 的形状一致！")
print("Final Output=\n", final_out[0])
print("\n✅ 现在输出维度是 (1,3,4)，可以与输入做残差连接了：")
print("   residual_out = X + final_out  # 形状都是 (1,3,4)")
