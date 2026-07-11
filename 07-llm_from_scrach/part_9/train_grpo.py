"""
GRPO训练脚本
实现Group Relative Policy Optimization (GRPO)训练流程
GRPO是PPO的变体，使用轨迹级别的优势估计，无需价值函数头
"""
# train_grpo.py
from __future__ import annotations
import argparse, torch
from pathlib import Path

from policy import PolicyWithValue  # 我们将忽略价值头
from rollout import RLHFTokenizer, format_prompt_only, sample_prompts, model_logprobs

# 从Part 7导入奖励模型
import sys
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_7'))
from model_reward import RewardModel  # noqa: E402

from grpo_loss import ppo_policy_only_losses


@torch.no_grad()
def compute_reward(reward_model: RewardModel, tok: RLHFTokenizer, prompt_text: str, response_ids: list[int], device) -> float:
    """
    计算奖励：使用奖励模型对完整格式化的文本进行评分
    
    Args:
        reward_model: 奖励模型
        tok: 分词器
        prompt_text: 提示文本
        response_ids: 响应的token ID列表
        device: 计算设备
    
    Returns:
        奖励分数（标量）
    """
    # 构建完整格式化的文本（与PPO中相同）
    from part_6.formatters import Example, format_example
    resp_text = tok.decode(response_ids)
    text = format_example(Example(prompt_text, resp_text))
    ids = tok.encode(text)
    x = torch.tensor([ids[:tok.block_size]], dtype=torch.long, device=device)
    r = reward_model(x)
    return float(r[0].item())


def main():
    """GRPO训练主函数"""
    # 解析命令行参数
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=str, default='runs/grpo-demo', help='输出目录')
    p.add_argument('--policy_ckpt', type=str, required=True, help='SFT检查点路径（Part 6）')
    p.add_argument('--reward_ckpt', type=str, required=True, help='奖励模型检查点路径（Part 7）')
    p.add_argument('--steps', type=int, default=100, help='训练步数')
    p.add_argument('--batch_prompts', type=int, default=32, help='每步的提示数量（分组前）')
    p.add_argument('--group_size', type=int, default=4, help='每个提示的完成数量')
    p.add_argument('--block_size', type=int, default=256, help='上下文长度')
    p.add_argument('--resp_len', type=int, default=64, help='响应长度')
    p.add_argument('--kl_coef', type=float, default=0.01, help='KL散度系数')
    p.add_argument('--lr', type=float, default=1e-5, help='学习率')
    p.add_argument('--bpe_dir', type=str, default=None, help='BPE分词器目录')
    p.add_argument('--cpu', action='store_true', help='强制使用CPU')
    args = p.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # 初始化分词器
    tok = RLHFTokenizer(block_size=args.block_size, bpe_dir=args.bpe_dir)

    # 加载SFT策略（以及冻结的参考策略）
    ckpt = torch.load(args.policy_ckpt, map_location=device)
    cfg = ckpt.get('config', {})
    vocab_size = cfg.get('vocab_size', tok.vocab_size)
    block_size = cfg.get('block_size', tok.block_size)
    n_layer = cfg.get('n_layer', 2)
    n_head  = cfg.get('n_head', 2)
    n_embd  = cfg.get('n_embd', 128)

    # 初始化可训练的策略模型
    policy = PolicyWithValue(vocab_size, block_size, n_layer, n_head, n_embd).to(device)
    policy.lm.load_state_dict(ckpt['model'])
    policy.eval()

    # 初始化冻结的参考策略（用于KL散度计算）
    ref = PolicyWithValue(vocab_size, block_size, n_layer, n_head, n_embd).to(device)
    ref.lm.load_state_dict(ckpt['model'])
    # 冻结参考策略的所有参数
    for p_ in ref.parameters():
        p_.requires_grad_(False)
    ref.eval()

    # 加载奖励模型
    rckpt = torch.load(args.reward_ckpt, map_location=device)
    rm = RewardModel(vocab_size=rckpt['config'].get('vocab_size', tok.vocab_size),
                     block_size=rckpt['config'].get('block_size', tok.block_size),
                     n_layer=rckpt['config'].get('n_layer', 4),
                     n_head=rckpt['config'].get('n_head', 4),
                     n_embd=rckpt['config'].get('n_embd', 256)).to(device)
    rm.load_state_dict(rckpt['model'])
    rm.eval()

    # 初始化优化器
    opt = torch.optim.AdamW(policy.parameters(), lr=args.lr, betas=(0.9, 0.999))

    # 创建小的提示池（重用辅助函数）
    prompts_pool = sample_prompts(16)

    step = 0
    pool_idx = 0
    G = args.group_size  # 每个提示的完成数量

    while step < args.steps:
        # ----- 选择提示 -----
        # 选择P个提示，每个提示生成G个完成 → B = P*G 个轨迹
        P = max(1, args.batch_prompts)
        if pool_idx + P > len(prompts_pool):
            pool_idx = 0  # 循环使用提示池
        batch_prompts = prompts_pool[pool_idx: pool_idx + P]
        pool_idx += P

        # 对仅提示文本进行分词
        prompt_texts = [format_prompt_only(p).replace("</s>", "") for p in batch_prompts]
        prompt_in_ids = [tok.encode(t) for t in prompt_texts]

        # ----- 为每个提示生成G个完成 -----
        # 我们将所有轨迹展平收集，但跟踪它们的组/提示ID
        seq_list = []        # token ID的Tensor列表
        boundary_list = []   # 响应在（可能被裁剪的）序列中开始的索引
        prompt_id_of = []    # 该轨迹属于哪个提示 (0..P-1)
        raw_rewards = []     # 每个轨迹的标量奖励（KL shaping之前）
        last_idx_list = []   # 用于填充记录

        with torch.no_grad():
            for pid, p_ids in enumerate(prompt_in_ids):
                for g in range(G):
                    # 生成响应
                    idx = torch.tensor([p_ids], dtype=torch.long, device=device)
                    out = policy.generate(idx, max_new_tokens=args.resp_len, temperature=2, top_k=3)
                    full_ids = out[0].tolist()

                    # 分离提示/响应
                    boundary = len(p_ids[-block_size:])  # 裁剪到上下文后的提示长度
                    resp_ids = full_ids[boundary:]
                    # 计算奖励
                    r_scalar = compute_reward(rm, tok, batch_prompts[pid], resp_ids, device)

                    # 保存轨迹信息
                    seq_list.append(torch.tensor(full_ids, dtype=torch.long))
                    boundary_list.append(boundary)
                    prompt_id_of.append(pid)
                    raw_rewards.append(r_scalar)

        # ----- 填充为批次 -----
        B = len(seq_list)  # B = P*G
        policy_ctx = getattr(policy, "block_size", block_size)
        max_len = min(policy_ctx, max(s.numel() for s in seq_list))
        seq = torch.zeros(B, max_len, dtype=torch.long, device=device)
        mask = torch.zeros(B, max_len, dtype=torch.bool, device=device)
        last_idx = torch.zeros(B, dtype=torch.long, device=device)

        # 保持每个轨迹的"动作位置"掩码和仅响应的边界
        for i, (ids, bnd) in enumerate(zip(seq_list, boundary_list)):
            L_full = ids.numel()
            L = min(L_full, max_len)
            drop = L_full - L
            b = max(0, bnd - drop)  # 左裁剪后的边界偏移
            seq[i, :L] = ids[-L:]  # 右对齐（保留最后L个token）
            if L < max_len:
                seq[i, L:] = 2  # 填充token
            # 动作是从 <=t-1 预测token t → 位置 [1..L-1]
            # 但我们只关心响应token：掩码 [b..L-1] → 动作 [b+1..L-1]
            mask[i, b:L] = True
            last_idx[i] = L - 1

        # ----- 对数概率和与参考策略的KL散度（token级别） -----
        # model_logprobs返回log p(x[t] | x[:t-1])，对于t=1..T-1，基于labels=seq[:,1:]
        with torch.no_grad():
            pol_lp_full = model_logprobs(policy, seq)  # (B, T-1)
            ref_lp_full = model_logprobs(ref, seq)     # (B, T-1)

        # 动作位置（预测位置 [1..T-1]）；我们只关心响应token：
        act_mask = mask[:, 1:]  # 对齐到 (B, T-1)
        old_logp = pol_lp_full[act_mask].detach()  # 旧策略的对数概率
        ref_logp = ref_lp_full[act_mask].detach()  # 参考策略的对数概率

        # 动作token上的每token KL散度
        kl_tok = (old_logp - ref_logp)  # (N_act,)

        # ----- 形状化的轨迹奖励和组基线 -----
        # 对于GRPO，优势是轨迹级别的，并广播到其token
        # 我们使用每个轨迹的平均token KL在轨迹级别进行KL shaping
        # 首先，计算每个轨迹在其动作token上的平均KL
        # 构建从展平的动作token回到轨迹ID的索引映射
        # 我们可以通过迭代行来重建计数
        traj_id_for_token = []
        counts = torch.zeros(B, dtype=torch.long, device=device)
        offset = 0
        for i in range(B):
            mrow = act_mask[i]
            n_i = int(mrow.sum().item())
            if n_i > 0:
                traj_id_for_token.extend([i] * n_i)
            counts[i] = n_i
            offset += n_i
        traj_id_for_token = torch.tensor(traj_id_for_token, dtype=torch.long, device=device)
        raw_rewards_t = torch.tensor(raw_rewards, dtype=torch.float, device=device)

        # 计算每个提示组的形状化奖励的平均值
        # GRPO的核心：使用组内平均作为基线
        group_mean = torch.zeros(B, dtype=torch.float, device=device)
        for pid in range(P):
            idxs = [i for i in range(B) if prompt_id_of[i] == pid]
            if not idxs:
                continue
            idxs_t = torch.tensor(idxs, dtype=torch.long, device=device)
            mean_val = raw_rewards_t[idxs_t].mean()  # 组内平均奖励
            group_mean[idxs_t] = mean_val

        # 每个轨迹的优势，广播到其动作token
        traj_adv = raw_rewards_t - group_mean  # (B,) GRPO的优势计算

        # 构建与old_logp/new_logp在动作token上对齐的展平优势张量
        if kl_tok.numel() > 0:
            adv_flat = traj_adv[traj_id_for_token]
        else:
            adv_flat = torch.zeros(0, dtype=torch.float, device=device)

        # 归一化优势（可选但通常有帮助）
        if adv_flat.numel() > 1:
            adv_flat = (adv_flat - adv_flat.mean()) / (adv_flat.std().clamp_min(1e-6))

        # ----- 更新（仅策略的PPO裁剪目标） -----
        policy.train()
        logits_new, _, _ = policy(seq, None)  # 忽略价值头
        logp_full = torch.log_softmax(logits_new[:, :-1, :], dim=-1)
        labels = seq[:, 1:]
        new_logp_all = logp_full.gather(-1, labels.unsqueeze(-1)).squeeze(-1)  # (B, T-1)
        new_logp = new_logp_all[act_mask]  # 新策略的对数概率

        # 动作token上的平均KL散度
        kl_now_ref_mean = (new_logp - ref_logp).mean() if new_logp.numel() > 0 else torch.tensor(0.0, device=device)

        # 计算GRPO损失
        out_loss = ppo_policy_only_losses(
            new_logp=new_logp, # 新策略的对数概率
            old_logp=old_logp, # 旧策略的对数概率
            adv=adv_flat, # 优势值
            clip_ratio=0.2, # PPO裁剪比例
            ent_coef=0.0,  # 如果希望从-new_logp均值获得熵奖励，设置为>0
            kl_coef=args.kl_coef, # KL散度系数
            kl_mean=kl_now_ref_mean, # 动作token上的平均KL散度
        )
        loss = out_loss.total_loss

        # 反向传播和优化
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)  # 梯度裁剪
        opt.step()
        policy.eval()

        # 一些快速诊断（与旧策略的移动，以及与参考策略的对比）
        with torch.no_grad():
            lp_post = model_logprobs(policy, seq)[act_mask]
            kl_move = (old_logp - lp_post).mean() if lp_post.numel() > 0 else torch.tensor(0.0, device=device)
            # KL(当前策略 || 参考策略)
            kl_ref_now = (lp_post - ref_logp).mean() if lp_post.numel() > 0 else torch.tensor(0.0, device=device)

        step += 1
        if step % 10 == 0:
            print(
                f"step {step} | loss {loss.item():.4f}"
                f"| KL_move {kl_move.item():.6f} | KL_ref {kl_ref_now.item():.6f}"
            )

    # 保存模型
    Path(args.out).mkdir(parents=True, exist_ok=True)
    torch.save({'model': policy.state_dict(), 'config': {
        'vocab_size': vocab_size,
        'block_size': block_size,
        'n_layer': n_layer,
        'n_head': n_head,
        'n_embd': n_embd,
    }}, str(Path(args.out)/'model_last.pt'))
    print(f"Saved GRPO policy to {args.out}/model_last.pt")


if __name__ == '__main__':
    main()
