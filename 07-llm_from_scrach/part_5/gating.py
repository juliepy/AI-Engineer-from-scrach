from __future__ import annotations
import torch, torch.nn as nn

class TopKGate(nn.Module):
    """Top‑k softmax 门控机制，带有 Switch 风格的负载均衡辅助损失。
    
    该类实现了专家混合（Mixture of Experts, MoE）模型中的路由机制，
    用于将每个 token 分配给 k 个专家，并计算负载均衡损失以防止专家利用不均。
    
    Args:
      dim: 输入隐藏层维度大小
      n_expert: 专家数量
      k: 每个 token 路由到的专家数量（通常为 1 或 2）
    
    Returns:
      (indices, weights, aux_loss) 其中：
        indices: (S, k) 长整型张量，每个 token 对应的专家 ID
        weights: (S, k) 浮点型张量，门控权重（每个 token 的权重和 ≤ 1）
        aux_loss: 标量，负载均衡惩罚项
    """
    def __init__(self, dim: int, n_expert: int, k: int = 1):
        """
        初始化 TopK 门控层。
        
        Args:
            dim: 输入特征维度
            n_expert: 专家数量
            k: 每个 token 选择的专家数量
        """
        super().__init__()
        # 确保 k 在有效范围内
        assert k >= 1 and k <= n_expert
        self.n_expert = n_expert  # 专家总数
        self.k = k                # 每个 token 选择的专家数量
        # 门控网络：将输入特征映射到专家分数
        self.w_g = nn.Linear(dim, n_expert, bias=True)

    def forward(self, x: torch.Tensor):
        """
        前向传播：计算每个 token 应该路由到哪些专家。
        
        Args:
            x: (S, C) 输入张量，其中 S = token 数量（batch * seq_len），C = 特征维度
        
        Returns:
            topk_idx: (S, k) 每个 token 选择的 top-k 专家索引
            topk_vals: (S, k) 每个 token 对应的 top-k 专家权重
            aux_loss: 负载均衡辅助损失
        """
        # x: (S, C) 其中 S = token 数量（batch * seq_len）
        # 计算每个专家对每个 token 的原始分数（logits）
        logits = self.w_g(x)                  # (S, E) E = 专家数量
        # 通过 softmax 归一化得到每个专家的概率分布
        probs = torch.softmax(logits, dim=-1) # (S, E)
        # 选择每个 token 的 top-k 专家及其对应的概率值
        topk_vals, topk_idx = torch.topk(probs, k=self.k, dim=-1)  # (S, k)

        # 计算负载均衡辅助损失（Switch Transformer 风格）：
        # 该损失鼓励所有专家被均匀使用，避免某些专家过载而其他专家闲置
        S, E = probs.size(0), probs.size(1)  # S = token 数量, E = 专家数量
        
        # importance: 每个专家的平均概率（反映专家的重要性）
        importance = probs.mean(dim=0)                 # (E,)
        
        # load: 每个专家被分配为 primary（top-1）的 token 比例
        # 使用硬分配（hard assignment）计算负载
        hard1 = topk_idx[:, 0]                         # (S,) 每个 token 的 top-1 专家索引
        load = torch.zeros(E, device=x.device)        # (E,) 初始化每个专家的负载为 0
        # 统计每个专家被选为 top-1 的次数
        load.scatter_add_(0, hard1, torch.ones_like(hard1, dtype=load.dtype))
        # 归一化为比例（每个专家处理的 token 比例）
        load = load / max(S, 1)
        
        # 计算负载均衡损失：importance * load 的乘积和，乘以专家数量
        # 当所有专家的 importance 和 load 都相等时，损失最小
        aux_loss = (E * (importance * load).sum())
        
        # 调试用打印语句（已注释）
        # print("*"*50)
        # print(probs, importance, hard1, load, aux_loss)
        # print("*"*50)

        return topk_idx, topk_vals, aux_loss


if __name__ == "__main__":
    """测试 TopKGate 的功能"""
    print("=" * 60)
    print("测试 TopKGate 门控机制")
    print("=" * 60)
    
    # 设置随机种子以便结果可复现
    torch.manual_seed(42)
    
    # 测试参数
    batch_size = 4
    seq_len = 8
    dim = 64          # 输入特征维度
    n_expert = 4      # 专家数量
    k = 2             # 每个 token 选择的专家数量
    
    # 创建测试输入
    S = batch_size * seq_len  # token 总数
    x = torch.randn(S, dim)
    
    print(f"\n输入形状: {x.shape}")
    print(f"参数设置: dim={dim}, n_expert={n_expert}, k={k}")
    print(f"Token 总数: {S}")
    
    # 测试 1: k=2 的情况
    print("\n" + "-" * 60)
    print("测试 1: k=2 (每个 token 选择 2 个专家)")
    print("-" * 60)
    gate_k2 = TopKGate(dim=dim, n_expert=n_expert, k=k)
    topk_idx, topk_vals, aux_loss = gate_k2(x)
    
    print(f"输出形状:")
    print(f"  topk_idx: {topk_idx.shape} (应该是 ({S}, {k}))")
    print(f"  topk_vals: {topk_vals.shape} (应该是 ({S}, {k}))")
    print(f"  aux_loss: {aux_loss.item():.4f} (标量)")
    
    # 验证输出形状
    assert topk_idx.shape == (S, k), f"topk_idx 形状错误: {topk_idx.shape}"
    assert topk_vals.shape == (S, k), f"topk_vals 形状错误: {topk_vals.shape}"
    assert aux_loss.dim() == 0, f"aux_loss 应该是标量，但形状是 {aux_loss.shape}"
    
    # 验证索引范围
    assert topk_idx.min() >= 0 and topk_idx.max() < n_expert, \
        f"专家索引超出范围: [{topk_idx.min()}, {topk_idx.max()}]"
    
    # 验证权重和（应该 <= 1，因为只取了 top-k）
    weights_sum = topk_vals.sum(dim=-1)
    print(f"\n权重验证:")
    print(f"  每个 token 的权重和范围: [{weights_sum.min():.4f}, {weights_sum.max():.4f}]")
    print(f"  权重和应该 <= 1.0: {torch.all(weights_sum <= 1.0 + 1e-5)}")
    
    # 测试 2: k=1 的情况（Switch Transformer 风格）
    print("\n" + "-" * 60)
    print("测试 2: k=1 (每个 token 选择 1 个专家，Switch 风格)")
    print("-" * 60)
    gate_k1 = TopKGate(dim=dim, n_expert=n_expert, k=1)
    topk_idx_k1, topk_vals_k1, aux_loss_k1 = gate_k1(x)
    
    print(f"输出形状:")
    print(f"  topk_idx: {topk_idx_k1.shape}")
    print(f"  topk_vals: {topk_vals_k1.shape}")
    print(f"  aux_loss: {aux_loss_k1.item():.4f}")
    
    # 验证 k=1 时权重和应该接近 1.0（因为只取 top-1）
    weights_sum_k1 = topk_vals_k1.sum(dim=-1)
    print(f"\n权重验证 (k=1):")
    print(f"  每个 token 的权重和范围: [{weights_sum_k1.min():.4f}, {weights_sum_k1.max():.4f}]")
    print(f"  权重和应该接近 1.0: {torch.allclose(weights_sum_k1, torch.ones_like(weights_sum_k1), atol=1e-5)}")
    
    # 测试 3: 检查专家分配分布
    print("\n" + "-" * 60)
    print("测试 3: 专家分配分布统计")
    print("-" * 60)
    expert_counts = torch.bincount(topk_idx_k1.squeeze(), minlength=n_expert)
    expert_proportions = expert_counts.float() / S
    print(f"每个专家被选中的次数: {expert_counts.tolist()}")
    print(f"每个专家被选中的比例: {expert_proportions.tolist()}")
    print(f"理想情况下每个专家应该被选中 {S // n_expert} 次")
    
    # 测试 4: 梯度测试
    print("\n" + "-" * 60)
    print("测试 4: 梯度反向传播")
    print("-" * 60)
    gate_test = TopKGate(dim=dim, n_expert=n_expert, k=k)
    x_test = torch.randn(S, dim, requires_grad=True)
    topk_idx_test, topk_vals_test, aux_loss_test = gate_test(x_test)
    
    # 计算一个简单的损失并反向传播
    loss = aux_loss_test + topk_vals_test.mean()
    loss.backward()
    
    print(f"输入梯度形状: {x_test.grad.shape}")
    print(f"门控层权重梯度存在: {gate_test.w_g.weight.grad is not None}")
    print(f"门控层偏置梯度存在: {gate_test.w_g.bias.grad is not None}")
    
    assert x_test.grad is not None, "输入梯度应该存在"
    assert gate_test.w_g.weight.grad is not None, "权重梯度应该存在"
    assert gate_test.w_g.bias.grad is not None, "偏置梯度应该存在"
    
    
    print("\n" + "=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)