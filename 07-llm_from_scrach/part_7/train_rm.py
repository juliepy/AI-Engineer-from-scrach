"""
奖励模型训练脚本
用于训练一个奖励模型（Reward Model），该模型可以评估生成文本的质量
通过对比学习的方式，学习区分更好的回复（chosen）和更差的回复（rejected）
"""
from __future__ import annotations
import argparse, torch
from pathlib import Path

from data_prefs import load_preferences  # 加载偏好数据
from collator_rm import PairCollator  # 数据整理器，用于处理成对的文本
from model_reward import RewardModel  # 奖励模型
from loss_reward import bradley_terry_loss, margin_ranking_loss  # 损失函数


def main():
    """主训练函数"""
    # 解析命令行参数
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=str, default='runs/rm-demo', help='模型输出目录')
    p.add_argument('--steps', type=int, default=500, help='训练步数')
    p.add_argument('--batch_size', type=int, default=8, help='批次大小')
    p.add_argument('--block_size', type=int, default=256, help='序列最大长度')
    p.add_argument('--n_layer', type=int, default=4, help='Transformer层数')
    p.add_argument('--n_head', type=int, default=4, help='注意力头数')
    p.add_argument('--n_embd', type=int, default=256, help='嵌入维度')
    p.add_argument('--lr', type=float, default=1e-4, help='学习率')
    p.add_argument('--loss', choices=['bt','margin'], default='bt', 
                   help='损失函数类型：bt=Bradley-Terry, margin=Margin Ranking')
    p.add_argument('--cpu', action='store_true', help='强制使用CPU（即使有GPU）')
    p.add_argument('--bpe_dir', type=str, default=None, help='BPE分词器目录路径')
    args = p.parse_args()

    # 设置计算设备（优先使用GPU）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # 加载训练数据
    # 使用前80%的训练数据
    items = load_preferences(split='train[:80]')
    # 将数据转换为三元组格式：(prompt, chosen, rejected)
    triples = [(it.prompt, it.chosen, it.rejected) for it in items]

    # 初始化数据整理器和模型
    col = PairCollator(block_size=args.block_size, bpe_dir=args.bpe_dir)
    model = RewardModel(vocab_size=col.vocab_size, block_size=args.block_size,
                        n_layer=args.n_layer, n_head=args.n_head, n_embd=args.n_embd).to(device)
    # 使用AdamW优化器
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.999))

    # 训练循环
    step = 0  # 当前训练步数
    i = 0  # 数据索引
    while step < args.steps:
        # 获取一个批次的数据
        batch = triples[i:i+args.batch_size]
        if not batch:  # 如果数据用完了，从头开始
            i = 0
            continue
        # 将批次数据整理成模型输入格式（正样本和负样本）
        pos, neg = col.collate(batch)
        pos, neg = pos.to(device), neg.to(device)
        
        # 前向传播：计算正样本和负样本的奖励分数
        r_pos = model(pos)  # chosen回复的奖励分数
        r_neg = model(neg)  # rejected回复的奖励分数
        
        # 根据选择的损失函数类型计算损失
        if args.loss == 'bt':
            # Bradley-Terry损失：基于成对比较的概率模型
            loss = bradley_terry_loss(r_pos, r_neg)
        else:
            # Margin Ranking损失：确保正样本分数比负样本高出一个margin
            loss = margin_ranking_loss(r_pos, r_neg, margin=1.0)
        
        # 反向传播和参数更新
        opt.zero_grad(set_to_none=True)  # 清零梯度
        loss.backward()  # 反向传播
        opt.step()  # 更新参数
        
        step += 1
        i += args.batch_size
        
        # 每25步打印一次训练进度
        if step % 25 == 0:
            # 计算准确率：正样本分数大于负样本分数的比例
            acc = (r_pos > r_neg).float().mean().item()
            print(f"step {step}: loss={loss.item():.4f} acc={acc:.2f}")

    # 保存模型
    Path(args.out).mkdir(parents=True, exist_ok=True)
    torch.save({'model': model.state_dict(), 'config': {
        'vocab_size': col.vocab_size,
        'block_size': args.block_size,
        'n_layer': args.n_layer,
        'n_head': args.n_head,
        'n_embd': args.n_embd,
    }}, str(Path(args.out)/'model_last.pt'))
    print(f"Saved reward model to {args.out}/model_last.pt")

if __name__ == '__main__':
    main()