"""
评估PPO/GRPO策略的脚本
使用奖励模型对策略生成的响应进行评分
"""
from __future__ import annotations
import argparse, torch
from pathlib import Path

from policy import PolicyWithValue
from rollout import RLHFTokenizer, sample_prompts, format_prompt_only

# 导入奖励模型（来自Part 7）
import sys
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_7'))
from model_reward import RewardModel  # noqa: E402


def score_policy(policy_ckpt: str, rm_ckpt: str, bpe_dir: str | None, n: int = 16):
    """
    评估策略模型：使用奖励模型对策略生成的响应进行评分
    
    Args:
        policy_ckpt: 策略模型检查点路径
        rm_ckpt: 奖励模型检查点路径
        bpe_dir: BPE分词器目录（可选）
        n: 评估的提示数量
    
    Returns:
        平均奖励分数
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tok = RLHFTokenizer(block_size=256, bpe_dir=bpe_dir)

    # 加载策略模型
    ckpt = torch.load(policy_ckpt, map_location=device)
    cfg = ckpt.get('config', {})
    pol = PolicyWithValue(cfg.get('vocab_size', tok.vocab_size), cfg.get('block_size', tok.block_size),
                          cfg.get('n_layer', 2), cfg.get('n_head', 2), cfg.get('n_embd', 128)).to(device)
    pol.load_state_dict(ckpt['model'])
    pol.eval()

    # 加载参考策略（SFT模型）用于对比
    ref = PolicyWithValue(cfg.get('vocab_size', tok.vocab_size), cfg.get('block_size', tok.block_size),
                          cfg.get('n_layer', 2), cfg.get('n_head', 2), cfg.get('n_embd', 128)).to(device)
    ckpt_ref = torch.load("../part_6/runs/sft-demo/model_last.pt", map_location=device) # 硬编码的SFT检查点路径
    ref.lm.load_state_dict(ckpt_ref['model']) 
    # 冻结参考策略的参数
    for p_ in ref.parameters():
        p_.requires_grad_(False)
    ref.eval()

    # 加载奖励模型
    rckpt = torch.load(rm_ckpt, map_location=device)
    rm = RewardModel(vocab_size=rckpt['config'].get('vocab_size', tok.vocab_size), block_size=rckpt['config'].get('block_size', tok.block_size),
                     n_layer=rckpt['config'].get('n_layer', 4), n_head=rckpt['config'].get('n_head', 4), n_embd=rckpt['config'].get('n_embd', 256)).to(device)
    rm.load_state_dict(rckpt['model'])
    rm.eval()

    # 采样提示并生成响应
    prompts = sample_prompts(n)
    rewards = []
    for p in prompts:
        # 格式化提示并编码
        prefix = format_prompt_only(p).replace('</s>', '')
        ids = tok.encode(prefix)
        x = torch.tensor([ids[-tok.block_size:]], dtype=torch.long, device=device)
        
        # 使用策略模型和参考模型生成响应
        with torch.no_grad():
            y = pol.generate(x, max_new_tokens=128, temperature=0.2, top_k=50)
            y_old = ref.generate(x, max_new_tokens=128, temperature=0.2, top_k=50)
        
        # 解码响应（只取新生成的部分）
        resp = tok.decode(y[0].tolist()[len(ids[-tok.block_size:]):])
        resp_old = tok.decode(y_old[0].tolist()[len(ids[-tok.block_size:]):])

        # 使用奖励模型计算格式化完整文本的奖励
        from part_6.formatters import Example, format_example
        text = format_example(Example(p, resp))
        z = torch.tensor([tok.encode(text)[:tok.block_size]], dtype=torch.long, device=device)
        with torch.no_grad():
            r = rm(z)[0].item()
        rewards.append(r)
    
    # 返回平均奖励
    return sum(rewards)/max(1,len(rewards))


if __name__ == '__main__':
    # 解析命令行参数
    p = argparse.ArgumentParser()
    p.add_argument('--policy_ckpt', type=str, required=True, help='策略模型检查点路径')
    p.add_argument('--reward_ckpt', type=str, required=True, help='奖励模型检查点路径')
    p.add_argument('--split', type=str, default='val[:32]', help='数据集分割（此脚本中未使用）')
    p.add_argument('--bpe_dir', type=str, default=None, help='BPE分词器目录')
    args = p.parse_args()

    # 评估策略并输出平均奖励
    avg_r = score_policy(args.policy_ckpt, args.reward_ckpt, args.bpe_dir, n=16)
    print(f"Avg RM reward: {avg_r:.4f}")