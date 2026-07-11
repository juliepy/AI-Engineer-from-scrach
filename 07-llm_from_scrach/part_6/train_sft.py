"""
监督微调（SFT, Supervised Fine-Tuning）训练脚本

该脚本用于对预训练的GPT模型进行监督微调，使其能够根据提示（prompt）生成相应的回复（response）。
主要功能包括：
- 加载SFT数据集（prompt-response对）
- 使用课程学习（curriculum learning）策略，按长度排序训练样本
- 使用SFTCollator进行数据批处理
- 训练模型并保存检查点
"""
from __future__ import annotations
import argparse, torch
import torch.nn as nn
from pathlib import Path

# 设置随机种子，确保结果可复现
torch.manual_seed(0)

# 复用 Part 3 中的 GPTModern 模型
import sys
from pathlib import Path as _P
# 将 part_3 目录添加到系统路径，以便导入模型
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
from model_modern import GPTModern  # noqa: E402

# 导入SFT相关的数据加载、批处理和课程学习模块
from dataset_sft import load_tiny_hf  # 加载SFT数据集
from collator_sft import SFTCollator  # SFT数据批处理器
from curriculum import LengthCurriculum  # 按长度排序的课程学习策略


def main():
    """
    主训练函数
    
    执行监督微调训练流程：
    1. 解析命令行参数
    2. 加载数据集
    3. 初始化模型和优化器
    4. 执行训练循环
    5. 保存模型检查点
    """
    # ========== 解析命令行参数 ==========
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=str, default='huggingface', help='huggingface or path to local jsonl (unused in demo)')
    p.add_argument('--ckpt', type=str, required=False, help='预训练模型检查点路径（可选）')
    p.add_argument('--out', type=str, default='runs/sft', help='模型输出目录')
    p.add_argument('--steps', type=int, default=200, help='训练步数')
    p.add_argument('--batch_size', type=int, default=8, help='批次大小')
    p.add_argument('--block_size', type=int, default=256, help='序列最大长度（上下文窗口）')
    p.add_argument('--n_layer', type=int, default=4, help='Transformer层数')
    p.add_argument('--n_head', type=int, default=4, help='注意力头数')
    p.add_argument('--n_embd', type=int, default=256, help='嵌入维度')
    p.add_argument('--lr', type=float, default=3e-4, help='学习率')
    p.add_argument('--cpu', action='store_true', help='强制使用CPU（即使有GPU）')
    p.add_argument('--bpe_dir', type=str, default='../part_4/runs/part4-demo/tokenizer', 
                   help='BPE分词器目录路径（假设从Part 4训练得到）')
    args = p.parse_args()

    # 确定训练设备（优先使用GPU）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')

    # ========== 加载数据集 ==========
    # 从HuggingFace加载小规模数据集切片（前24个样本）或使用回退示例
    items = load_tiny_hf(split='train[:24]', sample_dataset=False)

    # 打印前几个样本，用于检查数据格式
    print(f"Loaded {len(items)} SFT items. Few samples:")
    for it in items[:3]:
        print(f"PROMPT: {it.prompt}\nRESPONSE: {it.response}\n{'-'*40}")

    # ========== 课程学习策略 ==========
    # 将数据转换为(prompt, response)元组列表
    tuples = [(it.prompt, it.response) for it in items]
    # 使用长度课程学习：按长度排序，从短到长训练，有助于模型逐步学习
    cur = list(LengthCurriculum(tuples))
    print(cur)

    # ========== 初始化数据批处理器和模型 ==========
    # SFTCollator负责将文本对转换为模型输入（tokenization + padding）
    col = SFTCollator(block_size=args.block_size, bpe_dir=args.bpe_dir)
    # 创建GPT模型，使用现代架构特性（RMSNorm, SwiGLU, RoPE）
    model = GPTModern(vocab_size=col.vocab_size, block_size=args.block_size,
                      n_layer=args.n_layer, n_head=args.n_head, n_embd=args.n_embd,
                      use_rmsnorm=True, use_swiglu=True, rope=True).to(device)

    # ========== 加载预训练检查点（如果提供） ==========
    if args.ckpt:
        print(f"Using model config from checkpoint {args.ckpt}")
        ckpt = torch.load(args.ckpt, map_location=device)
        cfg = ckpt.get('config', {})
        # 加载预训练权重
        model.load_state_dict(ckpt['model'])

    # ========== 初始化优化器 ==========
    # 使用AdamW优化器，设置学习率、beta参数和权重衰减
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=0.1)
    model.train()  # 设置为训练模式

    # ========== 训练循环 ==========
    # 简单的单机训练循环：循环使用课程学习的数据来填充批次
    step = 0
    i = 0  # 课程学习数据的索引
    while step < args.steps:
        # 从课程学习序列中获取一个批次
        batch = cur[i:i+args.batch_size]
        if not batch:
            # 如果批次为空，重新开始课程学习（从头开始）
            # cur = list(LengthCurriculum(tuples)); 
            i = 0
            continue
        
        # 使用collator将文本对转换为模型输入（tokenization + padding）
        xb, yb = col.collate(batch)
        xb, yb = xb.to(device), yb.to(device)
        
        # 前向传播：计算logits和损失
        logits, loss, _ = model(xb, yb)
        
        # 反向传播和优化
        opt.zero_grad(set_to_none=True)  # 清零梯度（使用set_to_none优化内存）
        loss.backward()  # 计算梯度
        opt.step()  # 更新参数
        
        step += 1
        i += args.batch_size
        
        # 每20步打印一次损失
        if step % 20 == 0:
            print(f"step {step}: loss={loss.item():.4f}")

    # ========== 保存模型检查点 ==========
    # 创建输出目录
    Path(args.out).mkdir(parents=True, exist_ok=True)
    
    # 构建模型配置字典
    cfg = {
        "vocab_size": col.vocab_size,  # 词汇表大小
        "block_size": args.block_size,  # 序列最大长度
        "n_layer": args.n_layer,  # Transformer层数
        "n_head": args.n_head,  # 注意力头数
        "n_embd": args.n_embd,  # 嵌入维度
        "dropout": 0.0,  # Dropout率（训练时未使用）
        "use_rmsnorm": True,  # 使用RMSNorm归一化
        "use_swiglu": True,  # 使用SwiGLU激活函数
        "rope": True,  # 使用RoPE位置编码
        # 分词器信息（尽力而为）
        "tokenizer_type": "byte" if col.vocab_size == 256 else "bpe",  # 判断分词器类型
        "tokenizer_dir": None,  # 如果有训练好的BPE目录，可以设置真实路径
    }
    
    # 保存模型状态字典和配置
    torch.save({'model': model.state_dict(), 'config': cfg},
               str(Path(args.out)/'model_last.pt'))
    print(f"Saved SFT checkpoint to {args.out}/model_last.pt")

if __name__ == '__main__':
    main()