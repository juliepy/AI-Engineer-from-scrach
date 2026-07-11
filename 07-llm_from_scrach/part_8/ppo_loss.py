from __future__ import annotations
import torch, torch.nn.functional as F
from dataclasses import dataclass

@dataclass
class PPOLossOut:
    """PPO损失函数的输出结果"""
    policy_loss: torch.Tensor  # 策略损失
    value_loss: torch.Tensor  # 价值损失
    entropy: torch.Tensor  # 熵（用于鼓励探索）
    approx_kl: torch.Tensor  # 近似KL散度（用于监控策略变化）
    total_loss: torch.Tensor  # 总损失


def ppo_losses(new_logp, old_logp, adv, new_values, old_values, returns,
               clip_ratio=0.2, vf_coef=0.5, ent_coef=0.0):
    """
    计算PPO（Proximal Policy Optimization）损失
    
    参数:
        new_logp: 新策略的对数概率 (N,)
        old_logp: 旧策略的对数概率 (N,)
        adv: 优势函数值 (N,)
        new_values: 新策略的价值估计 (N,)
        old_values: 旧策略的价值估计 (N,)
        returns: 实际回报值 (N,)
        clip_ratio: 裁剪比例，默认0.2
        vf_coef: 价值损失系数，默认0.5
        ent_coef: 熵系数，默认0.0
    
    返回:
        PPOLossOut: 包含各项损失的输出对象
    """
    # 策略损失：使用clipped surrogate objective
    ratio = torch.exp(new_logp - old_logp)  # 重要性采样比率 (N,)
    unclipped = ratio * adv  # 未裁剪的策略梯度
    clipped = torch.clamp(ratio, 1.0 - clip_ratio, 1.0 + clip_ratio) * adv  # 裁剪后的策略梯度
    policy_loss = -torch.mean(torch.min(unclipped, clipped))  # 取最小值并取负（因为要最大化）

    # 价值损失：使用MSE损失
    value_loss = F.mse_loss(new_values, returns)

    # 熵奖励：鼓励探索（通过负对数概率的均值近似）
    entropy = -new_logp.mean()

    # 近似KL散度：用于监控策略变化程度
    approx_kl = torch.mean(old_logp - new_logp)

    # 总损失：策略损失 + 价值损失 * 系数 - 熵奖励 * 系数
    total = policy_loss + vf_coef * value_loss - ent_coef * entropy
    return PPOLossOut(policy_loss, value_loss, entropy, approx_kl, total)


def test_ppo_losses():
    """简单的PPO损失函数测试"""
    print("=" * 50)
    print("PPO损失函数测试")
    print("=" * 50)
    
    # 创建模拟数据
    batch_size = 8
    new_logp = torch.randn(batch_size) * 0.1  # 新策略对数概率
    old_logp = torch.randn(batch_size) * 0.1  # 旧策略对数概率
    adv = torch.randn(batch_size)  # 优势函数
    new_values = torch.randn(batch_size)  # 新价值估计
    old_values = torch.randn(batch_size)  # 旧价值估计
    returns = torch.randn(batch_size)  # 实际回报
    
    print(f"\n输入数据形状:")
    print(f"  new_logp: {new_logp.shape}")
    print(f"  old_logp: {old_logp.shape}")
    print(f"  adv: {adv.shape}")
    print(f"  returns: {returns.shape}")
    
    # 计算损失
    result = ppo_losses(new_logp, old_logp, adv, new_values, old_values, returns,
                       clip_ratio=0.2, vf_coef=0.5, ent_coef=0.01)
    
    # 打印重要信息
    print(f"\n损失计算结果:")
    print(f"  策略损失 (policy_loss): {result.policy_loss.item():.6f}")
    print(f"  价值损失 (value_loss): {result.value_loss.item():.6f}")
    print(f"  熵 (entropy): {result.entropy.item():.6f}")
    print(f"  近似KL散度 (approx_kl): {result.approx_kl.item():.6f}")
    print(f"  总损失 (total_loss): {result.total_loss.item():.6f}")
    
    print("\n测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_ppo_losses()