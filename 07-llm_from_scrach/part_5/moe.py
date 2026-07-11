"""
专家混合（Mixture of Experts, MoE）层实现。

本模块实现了基于 token 级别的 top-k 路由机制的 MoE 层。
该实现针对单 GPU 友好设计（通过循环遍历专家以提高代码清晰度）。

参考论文: https://arxiv.org/pdf/2101.03961
"""
from __future__ import annotations
import torch, torch.nn as nn
from gating import TopKGate
from experts import ExpertMLP

class MoE(nn.Module):
    """
    专家混合（Mixture-of-Experts, MoE）层。
    
    该层实现了基于 token 级别的 top-k 路由机制，将每个 token 分配给 k 个专家进行处理。
    实现方式对单 GPU 友好（通过循环遍历专家以提高代码清晰度）。
    
    参考论文: https://arxiv.org/pdf/2101.03961
    
    Args:
        dim: 输入和输出的特征维度
        n_expert: 专家数量
        k: 每个 token 路由到的专家数量，默认为 1（Switch Transformer 风格）
        mult: 专家 MLP 隐藏层维度相对于输入维度的倍数，默认为 4
        swiglu: 是否在专家 MLP 中使用 SwiGLU 激活函数，默认为 True
        dropout: Dropout 概率，默认为 0.0（不使用 dropout）
    """
    def __init__(self, dim: int, n_expert: int, k: int = 1, mult: int = 4, swiglu: bool = True, dropout: float = 0.0):
        """
        初始化 MoE 层。
        
        Args:
            dim: 输入和输出的特征维度
            n_expert: 专家数量
            k: 每个 token 路由到的专家数量，默认为 1
            mult: 专家 MLP 隐藏层维度相对于输入维度的倍数，默认为 4
            swiglu: 是否在专家 MLP 中使用 SwiGLU 激活函数，默认为 True
            dropout: Dropout 概率，默认为 0.0
        """
        super().__init__()
        self.dim = dim              # 特征维度
        self.n_expert = n_expert    # 专家数量
        self.k = k                  # 每个 token 选择的专家数量
        # 初始化门控网络，用于决定每个 token 应该路由到哪些专家
        self.gate = TopKGate(dim, n_expert, k=k)
        # 创建 n_expert 个专家 MLP 模块
        self.experts = nn.ModuleList([ExpertMLP(dim, mult=mult, swiglu=swiglu, dropout=dropout) for _ in range(n_expert)])

    def forward(self, x: torch.Tensor):
        """
        前向传播函数。
        
        处理流程：
        1. 将输入展平为 token 序列
        2. 通过门控网络决定每个 token 路由到哪些专家
        3. 对每个专家，处理分配给它的 token
        4. 将专家输出按权重聚合并恢复原始形状
        
        Args:
            x: 输入张量，形状为 (B, T, C)
               B = batch size（批次大小）
               T = sequence length（序列长度）
               C = feature dimension（特征维度）
        
        Returns:
            y: 输出张量，形状为 (B, T, C)，与输入形状相同
            aux: 辅助损失（负载均衡损失），用于鼓励专家被均匀使用
        """
        B, T, C = x.shape           # 获取批次大小、序列长度和特征维度
        S = B * T                    # 计算 token 总数
        # 将输入展平为 (S, C)，其中 S = B * T（所有 token）
        x_flat = x.reshape(S, C)
        # 通过门控网络获取每个 token 的专家索引、权重和辅助损失
        # idx: (S, k) 每个 token 选择的 k 个专家索引
        # w: (S, k) 每个 token 对应的 k 个专家权重
        # aux: 标量，负载均衡辅助损失
        idx, w, aux = self.gate(x_flat)  # (S,k), (S,k)

        # 初始化输出张量，形状与展平后的输入相同
        y = torch.zeros_like(x_flat)     # (S,C)
        # 遍历每个专家
        for e in range(self.n_expert):
            # 遍历每个路由槽位（k 个槽位）
            for slot in range(self.k):
                # 找出在当前槽位被分配给专家 e 的 token
                sel = (idx[:, slot] == e)
                # 如果有 token 被分配给该专家
                if sel.any():
                    # 提取分配给专家 e 的 token 输入
                    x_e = x_flat[sel]
                    # 通过专家 e 处理这些 token
                    y_e = self.experts[e](x_e)
                    # 将专家输出按权重累加到对应位置
                    # w[sel, slot:slot+1] 保持维度以便广播
                    y[sel] += w[sel, slot:slot+1] * y_e
        # 将输出恢复为原始形状 (B, T, C)
        y = y.view(B, T, C)
        return y, aux


if __name__ == "__main__":
    """
    测试代码：验证 MoE 层的功能。
    """
    print("=" * 60)
    print("测试 MoE 层")
    print("=" * 60)
    
    # 设置随机种子以便结果可复现
    torch.manual_seed(42)
    
    # 测试参数
    batch_size = 2
    seq_len = 8
    dim = 64          # 输入特征维度
    n_expert = 4      # 专家数量
    k = 2             # 每个 token 选择的专家数量
    
    # 创建测试输入
    x = torch.randn(batch_size, seq_len, dim)
    
    print(f"\n输入形状: {x.shape}")
    print(f"参数设置: dim={dim}, n_expert={n_expert}, k={k}")
    
    # ========== 测试1: 基本功能测试 (k=2) ==========
    print("\n" + "-" * 60)
    print("测试 1: 基本功能测试 (k=2, SwiGLU)")
    print("-" * 60)
    moe_k2 = MoE(dim=dim, n_expert=n_expert, k=k, swiglu=True, dropout=0.0)
    moe_k2.eval()  # 设置为评估模式
    
    y, aux_loss = moe_k2(x)
    
    print(f"输出形状: {y.shape} (应该是 {x.shape})")
    print(f"辅助损失: {aux_loss.item():.4f}")
    
    # 验证输出形状
    assert y.shape == x.shape, f"输出形状错误: 期望 {x.shape}, 得到 {y.shape}"
    assert aux_loss.dim() == 0, f"辅助损失应该是标量，但形状是 {aux_loss.shape}"
    print("✓ 基本功能测试通过")
    
    # ========== 测试2: k=1 的情况 (Switch Transformer 风格) ==========
    print("\n" + "-" * 60)
    print("测试 2: k=1 (Switch Transformer 风格)")
    print("-" * 60)
    moe_k1 = MoE(dim=dim, n_expert=n_expert, k=1, swiglu=True, dropout=0.0)
    moe_k1.eval()
    
    y_k1, aux_loss_k1 = moe_k1(x)
    
    print(f"输出形状: {y_k1.shape}")
    print(f"辅助损失: {aux_loss_k1.item():.4f}")
    assert y_k1.shape == x.shape, f"输出形状错误: {y_k1.shape}"
    print("✓ k=1 测试通过")
    
    # ========== 测试3: GELU 模式 ==========
    print("\n" + "-" * 60)
    print("测试 3: GELU 模式 (非 SwiGLU)")
    print("-" * 60)
    moe_gelu = MoE(dim=dim, n_expert=n_expert, k=k, swiglu=False, dropout=0.0)
    moe_gelu.eval()
    
    y_gelu, aux_loss_gelu = moe_gelu(x)
    
    print(f"输出形状: {y_gelu.shape}")
    print(f"辅助损失: {aux_loss_gelu.item():.4f}")
    assert y_gelu.shape == x.shape, f"输出形状错误: {y_gelu.shape}"
    print("✓ GELU 模式测试通过")
    
    # ========== 测试4: Dropout 功能 ==========
    print("\n" + "-" * 60)
    print("测试 4: Dropout 功能")
    print("-" * 60)
    moe_dropout = MoE(dim=dim, n_expert=n_expert, k=k, swiglu=True, dropout=0.5)
    
    # 训练模式
    moe_dropout.train()
    y_train, _ = moe_dropout(x)
    print(f"训练模式输出形状: {y_train.shape}")
    
    # 评估模式
    moe_dropout.eval()
    y_eval, _ = moe_dropout(x)
    print(f"评估模式输出形状: {y_eval.shape}")
    
    assert y_train.shape == x.shape and y_eval.shape == x.shape
    print("✓ Dropout 功能测试通过")
    
    # ========== 测试5: 梯度计算 ==========
    print("\n" + "-" * 60)
    print("测试 5: 梯度计算")
    print("-" * 60)
    moe_grad = MoE(dim=dim, n_expert=n_expert, k=k, swiglu=True, dropout=0.0)
    moe_grad.train()
    
    x_grad = torch.randn(batch_size, seq_len, dim, requires_grad=True)
    y_grad, aux_grad = moe_grad(x_grad)
    
    # 计算损失并反向传播
    loss = y_grad.sum() + 0.01 * aux_grad  # 包含辅助损失
    loss.backward()
    
    assert x_grad.grad is not None, "输入梯度未计算"
    print(f"输入梯度形状: {x_grad.grad.shape}")
    print("✓ 梯度计算测试通过")
    
    # ========== 测试6: 不同维度测试 ==========
    print("\n" + "-" * 60)
    print("测试 6: 不同维度测试")
    print("-" * 60)
    test_dims = [32, 64, 128]
    for test_dim in test_dims:
        moe_test = MoE(dim=test_dim, n_expert=n_expert, k=k, swiglu=True, dropout=0.0)
        moe_test.eval()
        x_test = torch.randn(batch_size, seq_len, test_dim)
        y_test, _ = moe_test(x_test)
        assert y_test.shape == x_test.shape, f"维度 {test_dim} 测试失败"
        print(f"✓ dim={test_dim} 测试通过")
    
    # ========== 测试7: 不同专家数量 ==========
    print("\n" + "-" * 60)
    print("测试 7: 不同专家数量")
    print("-" * 60)
    test_n_experts = [2, 4, 8]
    for test_n_exp in test_n_experts:
        moe_test = MoE(dim=dim, n_expert=test_n_exp, k=1, swiglu=True, dropout=0.0)
        moe_test.eval()
        y_test, aux_test = moe_test(x)
        assert y_test.shape == x.shape, f"专家数量 {test_n_exp} 测试失败"
        print(f"✓ n_expert={test_n_exp} 测试通过 (辅助损失: {aux_test.item():.4f})")
    
    # ========== 测试总结 ==========
    print("\n" + "=" * 60)
    print("所有测试通过！✓")
    print("=" * 60)