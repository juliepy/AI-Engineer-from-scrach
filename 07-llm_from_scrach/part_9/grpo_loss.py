"""
GRPO损失函数模块
实现Group Relative Policy Optimization (GRPO)的损失计算
GRPO是PPO的变体，使用轨迹级别的优势估计，无需价值函数头
"""
# grpo_loss.py
from __future__ import annotations
import torch
from dataclasses import dataclass

@dataclass
class PolicyOnlyLossOut:
    """策略损失输出数据类（仅策略，无价值头）"""
    policy_loss: torch.Tensor  # PPO裁剪策略损失
    entropy: torch.Tensor      # 熵（用于探索）
    approx_kl: torch.Tensor    # 近似KL散度（新策略 vs 旧策略）
    kl_ref: torch.Tensor       # 与参考策略的KL散度
    total_loss: torch.Tensor   # 总损失


def ppo_policy_only_losses(new_logp, old_logp, adv, clip_ratio=0.2, ent_coef=0.0,
                           kl_coef: float = 0.0, kl_mean: torch.Tensor | None = None):
    """
    PPO风格的裁剪策略损失，仅策略部分（无价值头），
    加上单独的KL(π||π_ref)惩罚项：total = L_PPO + kl_coef * KL
    
    Args:
        new_logp: 新策略的对数概率，形状为(N_act,)，展平的动作token
        old_logp: 旧策略的对数概率，形状为(N_act,)
        adv: 优势值，形状为(N_act,)
        clip_ratio: PPO裁剪比例，默认0.2
        ent_coef: 熵系数（原始GRPO论文中未使用）
        kl_coef: KL散度系数
        kl_mean: 标量张量，动作token上的平均KL散度
    
    Returns:
        PolicyOnlyLossOut: 包含各项损失的输出对象
    """
    device = new_logp.device if new_logp.is_cuda else None
    # 处理空输入的情况
    if new_logp.numel() == 0:
        zero = torch.tensor(0.0, device=device)
        return PolicyOnlyLossOut(zero, zero, zero, zero, zero)

    # 计算重要性采样比率
    ratio = torch.exp(new_logp - old_logp)  # (N,)
    
    # PPO裁剪：取未裁剪和裁剪后的最小值
    unclipped = ratio * adv
    clipped = torch.clamp(ratio, 1.0 - clip_ratio, 1.0 + clip_ratio) * adv
    policy_loss = -torch.mean(torch.min(unclipped, clipped))

    # 计算熵（用于鼓励探索，但GRPO原始论文中未使用）
    entropy = -new_logp.mean() if ent_coef != 0.0 else new_logp.new_tensor(0.0)
    
    # 近似KL散度：旧策略 vs 新策略
    approx_kl = torch.mean(old_logp - new_logp)

    # 与参考策略的KL散度
    kl_ref = kl_mean if kl_mean is not None else new_logp.new_tensor(0.0)

    # 总损失 = 策略损失 - 熵奖励 + KL惩罚
    # 注意：原始GRPO论文中未使用熵奖励
    total = policy_loss - ent_coef * entropy + kl_coef * kl_ref
    return PolicyOnlyLossOut(policy_loss, entropy, approx_kl, kl_ref, total)


if __name__ == "__main__":
    # 简单测试
    torch.manual_seed(42)
    N = 10
    
    # 生成测试数据
    new_logp = torch.randn(N) * 0.1  # 新策略对数概率
    old_logp = torch.randn(N) * 0.1  # 旧策略对数概率
    adv = torch.randn(N) * 0.5       # 优势值
    kl_mean = torch.tensor(0.05)     # 与参考策略的KL散度
    
    # 测试基本功能
    result = ppo_policy_only_losses(
        new_logp, old_logp, adv,
        clip_ratio=0.2,
        ent_coef=0.01,
        kl_coef=0.1,
        kl_mean=kl_mean
    )
    
    # 打印结果
    print("=" * 50)
    print("GRPO Loss Test")
    print("=" * 50)
    print(f"Policy Loss:    {result.policy_loss.item():.6f}")
    print(f"Entropy:        {result.entropy.item():.6f}")
    print(f"Approx KL:      {result.approx_kl.item():.6f}")
    print(f"KL (ref):       {result.kl_ref.item():.6f}")
    print(f"Total Loss:     {result.total_loss.item():.6f}")
    print("=" * 50)