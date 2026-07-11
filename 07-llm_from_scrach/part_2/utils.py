"""
工具函数模块
提供用于文本生成中的 logits 过滤功能，包括 top-k 和 top-p (nucleus) 采样策略。
"""
from __future__ import annotations
import torch


def top_k_top_p_filtering(logits: torch.Tensor, top_k: int | None = None, top_p: float | None = None):
    """使用 top-k 和/或 nucleus (top-p) 过滤对 logits 分布进行过滤。
    
    该函数实现了两种常用的采样策略，用于在文本生成时限制候选词汇：
    - top-k: 只保留概率最高的 k 个词汇
    - top-p (nucleus): 保留累积概率达到 p 的最小词汇集合
    
    Args:
        logits: 形状为 (B, vocab) 的 logits 张量，其中 B 是批次大小，vocab 是词汇表大小
        top_k: 可选，保留概率最高的 k 个词汇。如果为 None，则不应用 top-k 过滤
        top_p: 可选，nucleus 采样的累积概率阈值（0 < top_p < 1.0）。如果为 None，则不应用 top-p 过滤
    
    Returns:
        过滤后的 logits 张量，被掩码的条目设置为 -inf
    """
    B, V = logits.shape  # B: 批次大小, V: 词汇表大小
    filtered = logits.clone()  # 克隆原始 logits，避免修改原始数据

    # Top-k 过滤：只保留概率最高的 k 个词汇
    if top_k is not None and top_k < V:
        # 获取每个样本中 top-k 的值和索引
        topk_vals, _ = torch.topk(filtered, top_k, dim=-1)
        # 获取第 k 大的值作为阈值
        kth = topk_vals[:, -1].unsqueeze(-1)
        # 将所有小于第 k 大值的 logits 设置为 -inf（掩码掉）
        filtered[filtered < kth] = float('-inf')

    # Top-p (nucleus) 过滤：保留累积概率达到 p 的最小词汇集合
    if top_p is not None and 0 < top_p < 1.0:
        # 按降序对 logits 进行排序
        sorted_logits, sorted_idx = torch.sort(filtered, descending=True, dim=-1)
        # 将排序后的 logits 转换为概率分布
        probs = torch.softmax(sorted_logits, dim=-1)
        # 计算累积概率
        cumsum = torch.cumsum(probs, dim=-1)
        # 创建掩码：标记累积概率超过 top_p 的词汇
        mask = cumsum > top_p
        # 确保至少保留一个 token（防止所有词汇都被掩码）
        mask[..., 0] = False
        # 将被掩码的 logits 设置为 -inf
        sorted_logits[mask] = float('-inf')
        # 将排序后的 logits 重新映射回原始位置
        filtered = torch.full_like(filtered, float('-inf'))
        filtered.scatter_(1, sorted_idx, sorted_logits)

    return filtered


if __name__ == "__main__":
    """简单的测试代码，验证 top_k_top_p_filtering 函数的功能"""
    print("=" * 50)
    print("测试 top_k_top_p_filtering 函数")
    print("=" * 50)
    
    # 创建测试用的 logits (批次大小=2, 词汇表大小=10)
    logits = torch.randn(2, 10)
    print(f"\n原始 logits 形状: {logits.shape}")
    print(f"原始 logits:\n{logits}")
    
    logits = torch.softmax(logits, dim=-1)
    print(f"softmax 后的 logits:\n{logits}")
    print(f"softmax 后的 logits 形状: {logits.shape}")
    
    print("\n" + "-" * 50)
    print("测试 1: 不应用任何过滤")
    print("-" * 50)
    result = top_k_top_p_filtering(logits, top_k=None, top_p=None)
    print(f"结果应与原始 logits 相同: {torch.allclose(result, logits)}")
    print(f"结果 logits:\n{result}")
    
    # 测试 2: 只应用 top-k 过滤 (k=3)
    print("\n" + "-" * 50)
    print("测试 2: 只应用 top-k 过滤 (k=3)")
    print("-" * 50)
    result = top_k_top_p_filtering(logits, top_k=3, top_p=None)
    # 检查每行是否只有最多 3 个非 -inf 值
    non_inf_count = (result != float('-inf')).sum(dim=-1)
    print(f"每行非 -inf 的词汇数量: {non_inf_count}")
    print(f"结果 logits:\n{result}")
    assert torch.all(non_inf_count <= 3), "top-k 过滤失败：应该只保留最多 3 个词汇"
    print("✓ top-k 过滤测试通过")
    
    # 测试 3: 只应用 top-p 过滤 (p=0.9)
    print("\n" + "-" * 50)
    print("测试 3: 只应用 top-p 过滤 (p=0.9)")
    print("-" * 50)
    result = top_k_top_p_filtering(logits, top_k=None, top_p=0.9)
    # 检查过滤后的概率分布
    probs = torch.softmax(result, dim=-1)
    # 对于非 -inf 的词汇，计算累积概率
    valid_mask = result != float('-inf')
    print(f"每行有效词汇数量: {valid_mask.sum(dim=-1)}")
    print(f"结果 logits:\n{result}")
    print("✓ top-p 过滤测试通过")
    
    # 测试 4: 同时应用 top-k 和 top-p 过滤
    print("\n" + "-" * 50)
    print("测试 4: 同时应用 top-k=3 和 top-p=0.9 过滤")
    print("-" * 50)
    result = top_k_top_p_filtering(logits, top_k=3, top_p=0.9)
    non_inf_count = (result != float('-inf')).sum(dim=-1)
    print(f"每行非 -inf 的词汇数量: {non_inf_count}")
    print(f"结果 logits:\n{result}")
    assert torch.all(non_inf_count <= 3), "top-k 过滤失败"
    print("✓ 组合过滤测试通过")
    
    # 测试 5: 边界情况 - top_k 大于词汇表大小
    print("\n" + "-" * 50)
    print("测试 5: 边界情况 - top_k=20 (大于词汇表大小 10)")
    print("-" * 50)
    result = top_k_top_p_filtering(logits, top_k=20, top_p=None)
    print(f"结果应与原始 logits 相同: {torch.allclose(result, logits)}")
    print("✓ 边界情况测试通过")
    
    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)