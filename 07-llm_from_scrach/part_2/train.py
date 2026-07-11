"""
GPT 模型训练脚本
支持训练、评估、检查点保存和文本生成采样
"""
from __future__ import annotations
import argparse
import os
import time
import torch
from tokenizer import ByteTokenizer
from dataset import ByteDataset
from model_gpt import GPT


def estimate_loss(model: GPT, ds: ByteDataset, args) -> dict:
    """
    评估模型在训练集和验证集上的平均损失
    
    Args:
        model: GPT 模型实例
        ds: 数据集实例
        args: 命令行参数对象
    
    Returns:
        包含 'train' 和 'val' 键的字典，值为对应的平均损失
    """
    model.eval()  # 设置为评估模式（禁用 dropout 等）
    out = {}
    with torch.no_grad():  # 禁用梯度计算以节省内存和加速
        for split in ['train', 'val']:
            losses = []
            # 多次采样取平均，以获得更稳定的损失估计
            for _ in range(args.eval_iters):
                xb, yb = ds.get_batch(split, args.batch_size, args.device)
                _, loss = model(xb, yb)
                losses.append(loss.item())
            out[split] = sum(losses) / len(losses)  # 计算平均损失
    model.train()  # 恢复训练模式
    return out


def main():
    """
    主训练函数
    解析命令行参数，初始化模型和优化器，执行训练循环
    """
    # ========== 参数解析 ==========
    p = argparse.ArgumentParser()
    
    # 数据相关参数
    p.add_argument('--data', type=str, required=True, help='训练数据文件路径')
    p.add_argument('--out_dir', type=str, default='runs/min-gpt', help='输出目录（检查点保存路径）')
    
    # 模型架构参数
    p.add_argument('--block_size', type=int, default=256, help='最大序列长度（上下文窗口大小）')
    p.add_argument('--batch_size', type=int, default=32, help='批次大小')
    p.add_argument('--n_layer', type=int, default=4, help='Transformer 层数')
    p.add_argument('--n_head', type=int, default=4, help='注意力头数')
    p.add_argument('--n_embd', type=int, default=256, help='嵌入维度')
    p.add_argument('--dropout', type=float, default=0.0, help='Dropout 概率')
    
    # 训练超参数
    p.add_argument('--steps', type=int, default=2000, help='训练步数')
    p.add_argument('--lr', type=float, default=3e-4, help='学习率')
    p.add_argument('--weight_decay', type=float, default=0.1, help='权重衰减（L2 正则化）')
    p.add_argument('--grad_clip', type=float, default=1.0, help='梯度裁剪阈值（0 表示不裁剪）')
    
    # 评估相关参数
    p.add_argument('--eval_interval', type=int, default=200, help='评估间隔（每 N 步评估一次）')
    p.add_argument('--eval_iters', type=int, default=50, help='评估时采样的批次数量')
    
    # 生成采样参数
    p.add_argument('--sample_every', type=int, default=200, help='生成样本的间隔（0 表示不生成）')
    p.add_argument('--sample_tokens', type=int, default=256, help='每次生成的 token 数量')
    p.add_argument('--temperature', type=float, default=1.0, help='生成温度（控制随机性）')
    p.add_argument('--top_k', type=int, default=50, help='Top-K 采样参数')
    p.add_argument('--top_p', type=float, default=None, help='Top-P（核采样）参数')
    
    # 设备相关参数
    p.add_argument('--cpu', action='store_true', help='强制使用 CPU（即使有 GPU）')
    p.add_argument('--compile', action='store_true', help='使用 torch.compile 加速（需要 PyTorch 2.0+）')
    p.add_argument('--amp', action='store_true', help='使用混合精度训练（自动混合精度）')
    
    args = p.parse_args()

    # ========== 打印训练配置 ==========
    print("=" * 60)
    print("开始训练 GPT 模型")
    print("=" * 60)
    print("训练配置:")
    print(f"  数据文件: {args.data}")
    print(f"  输出目录: {args.out_dir}")
    print(f"  模型架构: n_layer={args.n_layer}, n_head={args.n_head}, n_embd={args.n_embd}")
    print(f"  训练参数: steps={args.steps}, lr={args.lr}, batch_size={args.batch_size}")
    print(f"  其他设置: dropout={args.dropout}, grad_clip={args.grad_clip}, amp={args.amp}")

    # ========== 设备设置 ==========
    args.device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')
    print(f"使用设备: {args.device}")
    if args.device.type == 'cuda':
        print(f"GPU 名称: {torch.cuda.get_device_name(0)}")
        print(f"GPU 内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

    # ========== 初始化组件 ==========
    print("初始化组件...")
    # 初始化分词器（字节级分词器）
    tok = ByteTokenizer()
    print(f"分词器初始化完成，词汇表大小: {tok.vocab_size}")
    
    # 初始化数据集
    ds = ByteDataset(args.data, block_size=args.block_size)
    print(f"数据集加载完成，训练集大小: {len(ds.train):,}, 验证集大小: {len(ds.val):,}")
    
    # 创建 GPT 模型并移动到指定设备
    model = GPT(tok.vocab_size, args.block_size, args.n_layer, args.n_head, args.n_embd, args.dropout).to(args.device)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"模型创建完成，总参数量: {total_params:,}, 可训练参数量: {trainable_params:,}")

    # 可选：使用 torch.compile 加速（PyTorch 2.0+）
    if args.compile and hasattr(torch, 'compile'):
        model = torch.compile(model)
        print("已启用 torch.compile 加速")

    # ========== 优化器和混合精度 ==========
    print("初始化优化器...")
    # 使用 AdamW 优化器（带权重衰减）
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=args.weight_decay)
    print(f"优化器: AdamW, lr={args.lr}, weight_decay={args.weight_decay}")
    
    # 混合精度训练的梯度缩放器（仅在 CUDA 且启用 AMP 时使用）
    scaler = torch.cuda.amp.GradScaler(enabled=(args.amp and args.device.type == 'cuda'))
    if args.amp and args.device.type == 'cuda':
        print("已启用混合精度训练 (AMP)")

    # ========== 训练循环 ==========
    print("=" * 60)
    print("开始训练循环")
    print("=" * 60)
    
    best_val = float('inf')  # 记录最佳验证损失
    t0 = time.time()  # 用于计算时间
    start_time = time.time()  # 训练开始时间
    model.train()  # 设置为训练模式
    
    for step in range(1, args.steps + 1):
        # 获取训练批次
        xb, yb = ds.get_batch('train', args.batch_size, args.device)
        
        # 前向传播（使用混合精度如果启用）
        with torch.cuda.amp.autocast(enabled=(args.amp and args.device.type == 'cuda')):
            _, loss = model(xb, yb)
        
        # 反向传播
        opt.zero_grad(set_to_none=True)  # 清零梯度（set_to_none=True 可节省内存）
        scaler.scale(loss).backward()  # 缩放损失并反向传播
        
        # 梯度裁剪（防止梯度爆炸）
        if args.grad_clip > 0:
            scaler.unscale_(opt)  # 取消缩放以便裁剪
            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        
        # 更新参数
        scaler.step(opt)  # 执行优化器步骤
        scaler.update()  # 更新缩放器

        # 定期打印训练进度
        if step % 50 == 0:
            elapsed = time.time() - t0
            print(f"step {step:5d}/{args.steps} | loss {loss.item():.4f} | time {elapsed:.2f}s | "
                  f"ETA {(args.steps - step) * elapsed / 50 / 60:.1f}min")
            t0 = time.time()

        # 定期评估模型
        if step % args.eval_interval == 0:
            print(f"评估模型 (Step {step})...")
            losses = estimate_loss(model, ds, args)
            print(f"eval | train {losses['train']:.4f} | val {losses['val']:.4f}")
            
            # 如果验证损失更好，保存最佳模型
            if losses['val'] < best_val:
                improvement = best_val - losses['val']
                best_val = losses['val']
                ckpt_path = f"{args.out_dir}/model_best.pt"
                os.makedirs(args.out_dir, exist_ok=True)
                # 保存模型状态和配置
                torch.save({
                    'model': model.state_dict(),
                    'config': {
                        'vocab_size': tok.vocab_size,
                        'block_size': args.block_size,
                        'n_layer': args.n_layer,
                        'n_head': args.n_head,
                        'n_embd': args.n_embd,
                        'dropout': args.dropout,
                    },
                    'step': step,
                    'train_loss': losses['train'],
                    'val_loss': losses['val'],
                }, ckpt_path)
                print(f"✓ 保存最佳模型检查点: {ckpt_path} (验证损失改善: {improvement:.4f})")

        # 定期生成文本样本（用于监控训练进度）
        if args.sample_every > 0 and step % args.sample_every == 0:
            print(f"生成文本样本 (Step {step})...")
            # 从训练数据中随机选择一个起始位置
            start = torch.randint(low=0, high=len(ds.train) - args.block_size - 1, size=(1,)).item()
            # 提取种子序列
            seed = ds.train[start:start + args.block_size].unsqueeze(0).to(args.device)
            # 生成文本
            out = model.generate(
                seed,
                max_new_tokens=args.sample_tokens,
                temperature=args.temperature,
                top_k=args.top_k,
                top_p=args.top_p
            )
            # 解码并打印生成的文本
            txt = tok.decode(out[0].cpu())
            sample_text = txt[-(args.block_size + args.sample_tokens):]
            print("\n" + "=" * 60)
            print("生成的文本样本:")
            print("=" * 60)
            print(sample_text)
            print("=" * 60 + "\n")

    # ========== 最终保存 ==========
    # 训练结束后保存最终模型
    total_time = time.time() - start_time
    print("=" * 60)
    print("训练完成！")
    print(f"总训练时间: {total_time / 60:.2f} 分钟 ({total_time:.2f} 秒)")
    print(f"最佳验证损失: {best_val:.4f}")
    
    os.makedirs(args.out_dir, exist_ok=True)
    final_path = f"{args.out_dir}/model_final.pt"
    torch.save({
        'model': model.state_dict(),
        'config': {
            'vocab_size': tok.vocab_size,
            'block_size': args.block_size,
            'n_layer': args.n_layer,
            'n_head': args.n_head,
            'n_embd': args.n_embd,
            'dropout': args.dropout,
        },
        'step': args.steps,
        'best_val_loss': best_val,
    }, final_path)
    print(f"最终模型已保存到: {final_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()