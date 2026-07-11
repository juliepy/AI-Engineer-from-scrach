"""
PPO (Proximal Policy Optimization) 训练脚本

本脚本实现了基于PPO算法的强化学习训练流程，用于优化语言模型策略。
主要步骤：
1. 加载SFT（监督微调）后的策略模型作为初始策略和参考模型
2. 加载奖励模型用于评估生成文本的质量
3. 收集rollout数据：使用当前策略生成响应
4. 计算奖励：使用奖励模型评估生成的响应
5. 计算PPO损失并更新策略参数

PPO是一种策略优化算法，通过限制策略更新幅度来稳定训练过程。
"""
from __future__ import annotations
import argparse, torch
from pathlib import Path

# import torch
# torch.manual_seed(0)

from policy import PolicyWithValue
from rollout import RLHFTokenizer, format_prompt_only, format_example, sample_prompts, gather_logprobs, shift_labels
from rollout import model_logprobs

# 从 Part 7 导入奖励模型
import sys
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_7'))
from model_reward import RewardModel  # noqa: E402

from ppo_loss import ppo_losses


def compute_reward(reward_model: RewardModel, tok: RLHFTokenizer, prompt: str, response: str, device) -> float:
    """
    使用奖励模型计算给定提示和响应的奖励分数
    
    参数:
        reward_model: 奖励模型，用于评估文本质量
        tok: Tokenizer，用于文本编码
        prompt: 输入提示文本
        response: 模型生成的响应文本
        device: 计算设备（CPU或GPU）
        
    返回:
        奖励分数（标量浮点数）
    """
    # 将提示和响应格式化为完整的对话文本
    text = format_example(__import__('part_6.formatters', fromlist=['Example']).Example(prompt, response))
    # 编码为token ID序列
    ids = tok.encode(text)
    # 转换为张量，并截断到block_size长度
    x = torch.tensor([ids[:tok.block_size]], dtype=torch.long, device=device)
    # 使用奖励模型计算奖励（不计算梯度）
    with torch.no_grad():
        r = reward_model(x)
    return float(r[0].item())


def main():
    """
    PPO训练主函数
    
    执行完整的PPO训练流程：
    1. 解析命令行参数
    2. 初始化模型（策略模型、参考模型、奖励模型）
    3. 训练循环：收集数据 -> 计算奖励 -> 更新策略
    """
    # 解析命令行参数
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=str, default='runs/ppo-demo', help='输出目录路径')
    p.add_argument('--policy_ckpt', type=str, required=True, help='SFT检查点路径（Part 6）')
    p.add_argument('--reward_ckpt', type=str, required=True, help='奖励模型检查点路径（Part 7）')
    p.add_argument('--steps', type=int, default=100, help='训练步数')
    p.add_argument('--batch_size', type=int, default=4, help='批次大小')
    p.add_argument('--block_size', type=int, default=256, help='序列最大长度（上下文窗口）')
    p.add_argument('--resp_len', type=int, default=64, help='生成响应的最大长度')
    p.add_argument('--kl_coef', type=float, default=0.01, help='KL散度惩罚系数，用于防止策略偏离参考模型太远')
    p.add_argument('--gamma', type=float, default=1.0, help='折扣因子（GAE参数，本实现中未使用）')
    p.add_argument('--lam', type=float, default=0.95, help='GAE lambda参数（本实现中未使用）')
    p.add_argument('--lr', type=float, default=1e-5, help='学习率')
    p.add_argument('--bpe_dir', type=str, default=None, help='BPE tokenizer模型目录（可选）')
    p.add_argument('--cpu', action='store_true', help='强制使用CPU（即使有GPU可用）')
    args = p.parse_args()

    # 确定计算设备（优先使用GPU）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # 初始化tokenizer
    tok = RLHFTokenizer(block_size=args.block_size, bpe_dir=args.bpe_dir)

    # 加载SFT策略模型作为初始策略和参考模型
    # 参考模型在训练过程中保持冻结，用于计算KL散度惩罚
    ckpt = torch.load(args.policy_ckpt, map_location=device)
    cfg = ckpt.get('config', {})
    vocab_size = cfg.get('vocab_size', tok.vocab_size)
    block_size = cfg.get('block_size', tok.block_size)
    n_layer = cfg.get('n_layer', 2)
    n_head  = cfg.get('n_head', 2)
    n_embd  = cfg.get('n_embd', 128)

    # 初始化当前策略模型（将被优化）
    policy = PolicyWithValue(vocab_size, block_size, n_layer, n_head, n_embd).to(device)
    policy.lm.load_state_dict(ckpt['model'])  # 从SFT检查点加载语言模型权重

    # 初始化参考模型（冻结，用于KL散度计算）
    ref = PolicyWithValue(vocab_size, block_size, n_layer, n_head, n_embd).to(device)
    ref.lm.load_state_dict(ckpt['model'])  # 使用相同的SFT权重初始化
    for p_ in ref.parameters():
        p_.requires_grad_(False)  # 冻结所有参数
    ref.eval()  # 设置为评估模式

    # 加载奖励模型（用于评估生成文本的质量）
    rckpt = torch.load(args.reward_ckpt, map_location=device)
    rm = RewardModel(vocab_size=rckpt['config'].get('vocab_size', tok.vocab_size), 
                     block_size=rckpt['config'].get('block_size', tok.block_size),
                     n_layer=rckpt['config'].get('n_layer', 4), 
                     n_head=rckpt['config'].get('n_head', 4), 
                     n_embd=rckpt['config'].get('n_embd', 256)).to(device)
    rm.load_state_dict(rckpt['model'])
    rm.eval()  # 奖励模型在训练过程中保持冻结

    # 初始化优化器（只优化策略模型的参数）
    opt = torch.optim.AdamW(policy.parameters(), lr=args.lr, betas=(0.9, 0.999))

    # 准备提示词池（用于生成训练数据）
    prompts = sample_prompts(16)

    # 开始训练循环
    step = 0
    while step < args.steps:
        # ========== 收集Rollout批次数据 ==========
        # 从提示词池中采样一个批次
        batch_prompts = prompts[ (step*args.batch_size) % len(prompts) : ((step+1)*args.batch_size) % len(prompts) ]
        # 如果采样不足，循环补充
        if len(batch_prompts) < args.batch_size:
            batch_prompts += prompts[:args.batch_size-len(batch_prompts)]
        # 格式化提示词并编码
        texts = [format_prompt_only(p).replace("</s>", "") for p in batch_prompts]
        in_ids = [tok.encode(t) for t in texts]

        # 使用当前策略生成响应（不计算梯度）
        with torch.no_grad():
            out_ids = []
            for i, x in enumerate(in_ids):
                idx = torch.tensor([x], dtype=torch.long, device=device)
                # 生成响应：使用较低的温度和top_k采样以获得更稳定的输出
                out = policy.generate(idx, max_new_tokens=args.resp_len, temperature=0.2, top_k=3)
                out_ids.append(out[0].tolist())

        # 分离提示和响应，并计算奖励
        data = []
        for i, prompt in enumerate(batch_prompts):
            full = out_ids[i]  # 完整的token序列（提示+响应）
            # 找到边界：提示结束的位置
            # 使用原始提示的tokenization长度（截断到block_size）
            p_ids = in_ids[i][-block_size:]
            boundary = len(p_ids)  # 提示结束的位置
            resp_ids = full[boundary:]  # 提取响应部分
            # 使用奖励模型计算奖励（基于格式化的提示+响应文本）
            resp_text = tok.decode(resp_ids)
            r_scalar = compute_reward(rm, tok, prompt, resp_text, device)
            # 存储：完整序列、边界位置、奖励分数
            data.append((torch.tensor(full, dtype=torch.long), boundary, r_scalar))

        # 将批次数据填充到相同长度
        policy_ctx = getattr(policy, "block_size", block_size)
        max_len = min(policy_ctx, max(t[0].numel() for t in data))  # 最大序列长度（不超过block_size）
        B = len(data)  # 批次大小
        seq = torch.zeros(B, max_len, dtype=torch.long, device=device)  # 序列张量
        mask = torch.zeros(B, max_len, dtype=torch.bool, device=device)  # 动作掩码（标记哪些位置是响应部分）
        last_idx = torch.zeros(B, dtype=torch.long, device=device)  # 每个样本的最后一个有效位置
        rewards = torch.zeros(B, max_len, dtype=torch.float, device=device)  # 奖励张量

        for i, (ids, boundary, r_scalar) in enumerate(data):
            L_full = ids.numel()  # 完整序列长度
            L = min(L_full, max_len)  # 实际使用的长度
            drop = L_full - L  # 从左侧丢弃的token数量（如果序列太长）
            b = max(0, boundary - drop)  # 边界位置在左截断后的新位置
            # 如果序列太长，保留右侧的L个token（右对齐）
            seq[i, :L] = ids[-L:]
            # 如果序列不够长，用padding token（ID=2）填充
            if L < max_len:
                seq[i, L:] = 2  # 填充剩余位置
            # 设置动作掩码：只有响应部分（边界之后）的位置为True
            mask[i, b:L] = True
            # 奖励只在最后一个响应token位置设置（稀疏奖励）
            rewards[i, L-1] = r_scalar
            last_idx[i] = L-1  # 记录最后一个有效位置


        # 计算策略模型和参考模型的对数概率和价值
        # model_logprobs返回(B, T-1)，因为因果LM预测下一个token，对齐到seq[:,1:]
        pol_lp = model_logprobs(policy, seq)  # 当前策略的对数概率
        ref_lp = model_logprobs(ref, seq)  # 参考模型的对数概率
        # 计算价值估计（用于优势函数计算）
        with torch.no_grad():
            logits, values, _ = policy(seq, None)
        values = values[:, :-1]  # 对齐到pol_lp的形状(B, T-1)

        # 只选择动作位置（响应部分）的数据
        act_mask = mask[:,1:]  # 因为logprobs是预测token t基于<=t-1，所以mask也要右移
        old_logp = pol_lp[act_mask].detach()  # 旧策略的对数概率（用于重要性采样）
        ref_logp = ref_lp[act_mask].detach()  # 参考模型的对数概率（用于KL散度）
        old_values = values[act_mask].detach()  # 旧价值估计

        # 计算每个动作token的KL散度和整形奖励
        kl = (old_logp - ref_logp)  # KL散度：KL(策略||参考) ≈ E[log π_policy - log π_ref]
        # 整形奖励 = 原始奖励 - KL惩罚（防止策略偏离参考模型太远）
        shaped_r = rewards[:,1:][act_mask] - args.kl_coef * kl

        # 计算优势函数和回报
        # 注意：本实现简化了GAE（Generalized Advantage Estimation），直接使用即时奖励
        # 对于只在最后一步有奖励的情况，这种简化是合理的
        returns = shaped_r  # 目标价值 = 即时整形奖励
        adv = returns - old_values  # 优势 = 回报 - 价值估计
        # 标准化优势（有助于稳定训练）
        adv = (adv - adv.mean()) / (adv.std().clamp_min(1e-6))

        # ========== 更新策略（单次PPO更新，实际应用中可以对同一批次进行多次更新） ==========
        policy.train()  # 设置为训练模式
        # 使用更新后的策略重新计算logits和价值
        logits_new, values_new_full, _ = policy(seq, None)
        # 计算新策略的对数概率
        logp_full = torch.log_softmax(logits_new[:, :-1, :], dim=-1)
        labels = seq[:,1:]  # 目标标签（下一个token）
        new_logp_all = logp_full.gather(-1, labels.unsqueeze(-1)).squeeze(-1)  # 提取对应标签的对数概率
        new_logp = new_logp_all[act_mask]  # 只保留动作位置的对数概率
        new_values = values_new_full[:, :-1][act_mask]  # 新价值估计（动作位置）

        # 计算PPO损失
        from ppo_loss import ppo_losses
        out_loss = ppo_losses(new_logp, old_logp, adv, new_values, old_values, returns,
                              clip_ratio=0.2,  # PPO裁剪比例
                              vf_coef=0.5,     # 价值损失系数
                              ent_coef=0.0)    # 熵系数（本实现中未使用）
        loss = out_loss.total_loss

        # 反向传播和参数更新
        opt.zero_grad(set_to_none=True)  # 清零梯度
        loss.backward()  # 反向传播
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)  # 梯度裁剪（防止梯度爆炸）
        opt.step()  # 更新参数
        policy.eval()  # 切换回评估模式

        # 计算监控指标（不计算梯度）
        with torch.no_grad():
            # KL(old || new): 更新后的策略相对于收集数据时的策略快照的变化
            # 用于监控单次更新中策略的变化幅度
            lp_post = model_logprobs(policy, seq)  # (B, T-1)
            lp_post = lp_post[act_mask]  # 只保留动作位置
            kl_post = (old_logp - lp_post).mean()  # ≈ E[log π_old - log π_new]

            # KL(now || ref): 当前策略距离冻结参考模型的距离
            # 用于监控策略是否偏离参考模型太远
            lp_now = lp_post  # 已经在相同位置计算过
            kl_ref_now = (lp_now - ref_logp).mean()  # ≈ E[log π_now - log π_ref]

        step += 1
        # 定期打印训练进度
        if step % 10 == 0:
            print(
                f"step {step} | loss {loss.item():.4f}"
                f"| value loss {out_loss.value_loss.item():.4f} | KL_move {kl_post.item():.6f} | KL_ref {kl_ref_now.item():.6f}"
            )


    # 保存训练后的策略模型
    Path(args.out).mkdir(parents=True, exist_ok=True)
    torch.save({'model': policy.state_dict(), 'config': {
        'vocab_size': vocab_size,
        'block_size': block_size,
        'n_layer': n_layer,
        'n_head': n_head,
        'n_embd': n_embd,
    }}, str(Path(args.out)/'model_last.pt'))
    print(f"Saved PPO policy to {args.out}/model_last.pt")

if __name__ == '__main__':
    main()