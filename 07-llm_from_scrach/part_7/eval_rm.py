"""
奖励模型评估脚本
用于评估训练好的奖励模型在偏好数据上的准确率
准确率定义为：模型对 chosen 回复的奖励分数 > 对 rejected 回复的奖励分数的比例
"""
from __future__ import annotations
import argparse, torch
from data_prefs import load_preferences
from collator_rm import PairCollator
from model_reward import RewardModel


def main():
    """
    主函数：加载模型和数据进行评估
    """
    # 解析命令行参数
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt', type=str, required=True, help='模型检查点文件路径')
    p.add_argument('--split', type=str, default='val[:200]', help='数据集划分，默认使用验证集前200条')
    p.add_argument('--cpu', action='store_true', help='强制使用CPU（即使有GPU可用）')
    p.add_argument('--bpe_dir', type=str, default=None, help='BPE分词器目录路径')
    args = p.parse_args()

    # 确定计算设备（GPU或CPU）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # 加载偏好数据，每个item包含prompt、chosen和rejected三个字段
    items = load_preferences(split=args.split)
    # 将数据转换为三元组列表：(prompt, chosen, rejected)
    triples = [(it.prompt, it.chosen, it.rejected) for it in items]

    # 创建数据整理器，用于将文本转换为模型输入
    col = PairCollator(block_size=256, bpe_dir=args.bpe_dir)
    # 加载模型检查点
    ckpt = torch.load(args.ckpt, map_location=device)
    # 获取模型配置，如果检查点中没有配置则使用空字典
    cfg = ckpt.get('config', {})

    # 创建奖励模型，使用检查点中的配置或默认值
    model = RewardModel(vocab_size=cfg.get('vocab_size', col.vocab_size), block_size=cfg.get('block_size', 256),
                        n_layer=cfg.get('n_layer', 4), n_head=cfg.get('n_head', 4), n_embd=cfg.get('n_embd', 256))
    # 加载模型权重
    model.load_state_dict(ckpt['model'])
    # 将模型移到指定设备并设置为评估模式
    model.to(device).eval()

    # 评估准确率：计算 r_pos > r_neg 的比例
    import math
    B = 16  # 批次大小
    correct = 0  # 正确预测的数量（chosen的奖励 > rejected的奖励）
    total = 0     # 总样本数
    # 按批次处理数据
    for i in range(0, len(triples), B):
        batch = triples[i:i+B]
        # 将批次数据整理为模型输入格式，pos是chosen回复，neg是rejected回复
        pos, neg = col.collate(batch)
        pos, neg = pos.to(device), neg.to(device)
        # 在评估模式下，不需要计算梯度
        with torch.no_grad():
            r_pos = model(pos)  # 计算chosen回复的奖励分数
            r_neg = model(neg)  # 计算rejected回复的奖励分数
        # 统计正确预测的数量（r_pos > r_neg）
        correct += (r_pos > r_neg).sum().item()
        total += pos.size(0)
    # 计算准确率
    acc = correct / max(1, total)
    print(f"pairs={total}  accuracy (r_pos>r_neg) = {acc:.3f}")

if __name__ == '__main__':
    main()