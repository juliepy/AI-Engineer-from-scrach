"""
奖励模型损失函数模块

本模块实现了用于训练奖励模型（Reward Model）的损失函数。
这些损失函数用于学习人类偏好，通过比较不同响应的奖励分数来训练模型。
"""

from __future__ import annotations
import torch, torch.nn.functional as F


def bradley_terry_loss(r_pos: torch.Tensor, r_neg: torch.Tensor) -> torch.Tensor:
    """
    Bradley-Terry 损失函数
    
    该损失函数基于 Bradley-Terry 模型，用于学习成对比较的偏好。
    它假设偏好概率遵循 sigmoid 分布，即 P(pos > neg) = σ(r_pos - r_neg)。
    损失函数为负对数似然：-log σ(r_pos - r_neg) = softplus(-(r_pos - r_neg))
    
    Args:
        r_pos: 正样本（更优响应）的奖励分数，形状为 (batch_size,)
        r_neg: 负样本（较差响应）的奖励分数，形状为 (batch_size,)
    
    Returns:
        标量张量，表示平均损失值
    
    Note:
        - softplus(x) = log(1 + exp(x))，是 ReLU 的平滑版本
        - 当 r_pos > r_neg 时，损失较小；当 r_pos < r_neg 时，损失较大
        - 参考: https://docs.pytorch.org/docs/stable/generated/torch.nn.Softplus.html
    
    Example:
        >>> r_pos = torch.tensor([2.0, 1.5])
        >>> r_neg = torch.tensor([1.0, 1.2])
        >>> loss = bradley_terry_loss(r_pos, r_neg)
    """
    # 计算奖励分数差：r_pos - r_neg
    diff = r_pos - r_neg
    # 使用 softplus 计算损失并取平均
    # softplus(-diff) = log(1 + exp(-diff))，等价于 -log σ(diff)
    return F.softplus(-diff).mean()


def margin_ranking_loss(r_pos: torch.Tensor, r_neg: torch.Tensor, margin: float = 1.0) -> torch.Tensor:
    """
    边际排序损失函数（Margin Ranking Loss）
    
    该损失函数确保正样本的奖励分数比负样本至少高出指定的边际值。
    如果 r_pos - r_neg > margin，则损失为 0；否则损失为 margin - (r_pos - r_neg)。
    
    Args:
        r_pos: 正样本（更优响应）的奖励分数，形状为 (batch_size,)
        r_neg: 负样本（较差响应）的奖励分数，形状为 (batch_size,)
        margin: 边际值，默认值为 1.0。表示正样本奖励分数需要比负样本高出的最小值
    
    Returns:
        标量张量，表示平均损失值
    
    Note:
        - 损失公式：max(0, margin - (r_pos - r_neg))
        - 当 r_pos - r_neg >= margin 时，损失为 0
        - 当 r_pos - r_neg < margin 时，损失为 margin - (r_pos - r_neg)
        - 参考: https://docs.pytorch.org/docs/stable/generated/torch.nn.MarginRankingLoss.html
    
    Example:
        >>> r_pos = torch.tensor([2.0, 1.5])
        >>> r_neg = torch.tensor([1.0, 1.2])
        >>> loss = margin_ranking_loss(r_pos, r_neg, margin=1.0)
    """
    # y = 1 表示我们希望 r_pos > r_neg（即正样本排名更高）
    y = torch.ones_like(r_pos)
    # 计算边际排序损失
    return F.margin_ranking_loss(r_pos, r_neg, y, margin=margin)


pos = torch.tensor([2.0, 3.0])
neg = torch.tensor([1.0, 1.5])

print(f"\n=== Bradley-Terry Loss 单调性测试 ===")
print(f"初始正样本奖励分数 (pos): {pos}")
print(f"负样本奖励分数 (neg): {neg}")

l1 = bradley_terry_loss(pos, neg)
print(f"初始损失值 (l1): {l1.item():.6f}")

pos_updated = pos + 1.0
print(f"增加 margin 后的正样本奖励分数 (pos+1.0): {pos_updated}")

l2 = bradley_terry_loss(pos_updated, neg)  # increase margin
print(f"更新后的损失值 (l2): {l2.item():.6f}")

print(f"损失变化: l2 - l1 = {l2.item() - l1.item():.6f}")
print(f"验证单调性: l2 < l1 ? {l2.item() < l1.item()}")
print("=" * 40)

assert l2 < l1