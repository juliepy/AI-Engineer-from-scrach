from __future__ import annotations
import argparse, torch
import statistics
from dataset import ByteDataset
from model_gpt import GPT


def main():
    """
    评估GPT模型在验证集上的损失
    加载训练好的模型检查点，在验证集上计算平均损失
    """
    # 解析命令行参数
    p = argparse.ArgumentParser(description='评估GPT模型在验证集上的损失')
    p.add_argument('--data', type=str, required=True, help='训练数据文件路径')
    p.add_argument('--ckpt', type=str, required=True, help='模型检查点文件路径')
    p.add_argument('--block_size', type=int, default=256, help='上下文窗口大小（默认：256）')
    p.add_argument('--batch_size', type=int, default=32, help='评估批次大小（默认：32）')
    p.add_argument('--iters', type=int, default=300, help='评估迭代次数（默认：300）')
    p.add_argument('--cpu', action='store_true', help='即使CUDA可用也强制使用CPU')
    args = p.parse_args()

    # 打印评估配置信息
    print("=" * 60)
    print("评估配置:")
    print(f"  数据文件: {args.data}")
    print(f"  检查点: {args.ckpt}")
    print(f"  块大小: {args.block_size}")
    print(f"  批次大小: {args.batch_size}")
    print(f"  迭代次数: {args.iters}")
    print("=" * 60)

    # 确定使用的设备（GPU或CPU）
    device = torch.device('cuda' if torch.cuda.is_available() and not args.cpu else 'cpu')
    print(f"\n使用设备: {device}")
    if device.type == 'cuda':
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA版本: {torch.version.cuda}")

    # 加载数据集
    print(f"\n从以下路径加载数据集: {args.data}")
    ds = ByteDataset(args.data, block_size=args.block_size)
    print(f"  数据集加载成功")
    # 字节级数据集的词汇表大小固定为256（字节值范围0-255）
    vocab_size = 256
    print(f"  词汇表大小: {vocab_size} (字节级数据集固定值)")

    # 加载模型检查点
    print(f"\n从以下路径加载检查点: {args.ckpt}")
    ckpt = torch.load(args.ckpt, map_location=device)
    print(f"  检查点加载成功")
    
    # 获取模型配置，如果检查点中没有配置则使用默认值
    cfg = ckpt.get('config', {
        'vocab_size': vocab_size,
        'block_size': args.block_size,
        'n_layer': 4,
        'n_head': 4,
        'n_embd': 256,
        'dropout': 0.0,
    })
    print(f"\n模型配置:")
    print(f"  词汇表大小: {cfg['vocab_size']}")
    print(f"  块大小: {cfg['block_size']}")
    print(f"  层数: {cfg['n_layer']}")
    print(f"  注意力头数: {cfg['n_head']}")
    print(f"  嵌入维度: {cfg['n_embd']}")
    print(f"  Dropout: {cfg['dropout']}")

    # 创建模型并加载权重
    print(f"\n初始化模型...")
    model = GPT(**cfg).to(device)
    model.load_state_dict(ckpt['model'])
    print(f"  模型初始化完成，权重已加载")
    
    # 计算模型参数数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  总参数量: {total_params:,}")
    print(f"  可训练参数量: {trainable_params:,}")

    # 设置为评估模式（禁用dropout等）
    model.eval()
    print(f"\n模型已设置为评估模式")

    # 开始评估
    print(f"\n开始评估...")
    print(f"  在验证集上运行 {args.iters} 次迭代")
    losses = []
    
    with torch.no_grad():  # 禁用梯度计算以节省内存和加速
        for i in range(args.iters):
            # 获取一个batch的验证数据
            xb, yb = ds.get_batch('val', args.batch_size, device)
            
            # 前向传播计算损失
            _, loss = model(xb, yb)
            loss_value = loss.item()
            losses.append(loss_value)
            
            # 每10个iteration打印一次进度
            if (i + 1) % 10 == 0 or (i + 1) == args.iters:
                current_avg = sum(losses) / len(losses)
                print(f"  迭代 {i+1}/{args.iters}: 当前损失={loss_value:.4f}, 平均损失={current_avg:.4f}")

    # 计算并打印统计信息
    avg_loss = sum(losses) / len(losses)
    min_loss = min(losses)
    max_loss = max(losses)
    median_loss = statistics.median(losses)
    std_loss = statistics.stdev(losses) if len(losses) > 1 else 0.0

    print("\n" + "=" * 60)
    print("评估结果:")
    print(f"  平均损失: {avg_loss:.4f}")
    print(f"  最小损失: {min_loss:.4f}")
    print(f"  最大损失: {max_loss:.4f}")
    print(f"  中位数损失: {median_loss:.4f}")
    print(f"  标准差: {std_loss:.4f}")
    print(f"  总批次数: {len(losses)}")
    print("=" * 60)


if __name__ == '__main__':
    main()