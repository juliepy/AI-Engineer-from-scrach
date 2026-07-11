"""
训练脚本 - 用于训练 GPT 模型
支持从检查点恢复训练、混合精度训练、梯度累积等功能
"""
from __future__ import annotations
import argparse, time, signal
from pathlib import Path
import sys

import torch
import torch.nn as nn

# 添加 part_3 目录到路径，以便导入模型
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1] / 'part_3'))
from model_modern import GPTModern

# 导入自定义模块
from tokenizer_bpe import BPETokenizer  # BPE 分词器
from dataset_bpe import make_loader  # 数据加载器
from lr_scheduler import WarmupCosineLR  # 学习率调度器（预热+余弦退火）
from amp_accum import AmpGrad  # 混合精度训练和梯度累积
from checkpointing import (
    load_checkpoint,  # 加载检查点
    _log_hparams_tb,  # 记录超参数到 TensorBoard
    _maybe_log_graph_tb,  # 可能记录计算图到 TensorBoard
    _is_tb,  # 判断是否为 TensorBoard 日志
    _log_model_stats,  # 记录模型统计信息
    _maybe_log_attention,  # 可能记录注意力权重
    _log_samples_tb,  # 记录生成样本到 TensorBoard
    _log_runtime,  # 记录运行时统计
    atomic_save_all,  # 原子性保存所有检查点
)
from logger import init_logger  # 初始化日志记录器


def run_cfg_from_args(args, vocab_size: int) -> dict:
    """
    从命令行参数构建模型配置字典
    
    Args:
        args: 命令行参数对象
        vocab_size: 词汇表大小
        
    Returns:
        包含模型配置的字典，包括：
        - vocab_size: 词汇表大小
        - block_size: 序列长度（上下文窗口）
        - n_layer: Transformer 层数
        - n_head: 注意力头数
        - n_embd: 嵌入维度
        - dropout: Dropout 比率
        - use_rmsnorm: 使用 RMSNorm 归一化
        - use_swiglu: 使用 SwiGLU 激活函数
        - rope: 使用 RoPE 位置编码
        - max_pos: 最大位置编码长度
        - sliding_window: 滑动窗口（None 表示不使用）
        - attention_sink: 注意力 sink tokens 数量
    """
    return dict(
        vocab_size=vocab_size,
        block_size=args.block_size,
        n_layer=args.n_layer,
        n_head=args.n_head,
        n_embd=args.n_embd,
        dropout=args.dropout,
        use_rmsnorm=True,  # 使用 RMSNorm 替代 LayerNorm
        use_swiglu=True,  # 使用 SwiGLU 激活函数
        rope=True,  # 使用旋转位置编码（RoPE）
        max_pos=4096,  # 最大位置编码长度
        sliding_window=None,  # 不使用滑动窗口注意力
        attention_sink=0,  # 不使用注意力 sink tokens
    )


def main():
    """
    主训练函数
    负责解析参数、初始化模型、加载数据、执行训练循环
    """
    # ========== 参数解析 ==========
    p = argparse.ArgumentParser()
    # 数据路径和输出目录
    p.add_argument('--data', type=str, required=True, help='训练数据文件路径')
    p.add_argument('--out', type=str, default='runs/part4', help='输出目录，用于保存检查点和日志')

    # tokenizer / model dims - 分词器和模型维度参数
    p.add_argument('--bpe', action='store_true', help='训练并使用 BPE 分词器（推荐）')
    p.add_argument('--vocab_size', type=int, default=32000, help='词汇表大小')
    p.add_argument('--block_size', type=int, default=256, help='序列长度（上下文窗口大小）')
    p.add_argument('--n_layer', type=int, default=6, help='Transformer 层数')
    p.add_argument('--n_head', type=int, default=8, help='注意力头数')
    p.add_argument('--n_embd', type=int, default=512, help='嵌入维度')
    p.add_argument('--dropout', type=float, default=0.0, help='Dropout 比率')

    # train - 训练超参数
    p.add_argument('--batch_size', type=int, default=32, help='批次大小')
    p.add_argument('--epochs', type=int, default=1, help='训练轮数')
    p.add_argument('--steps', type=int, default=300, help='最大优化器步数（本次运行）')
    p.add_argument('--lr', type=float, default=3e-4, help='学习率')
    p.add_argument('--warmup_steps', type=int, default=20, help='预热步数')
    p.add_argument('--mixed_precision', action='store_true', help='启用混合精度训练（FP16）')
    p.add_argument('--grad_accum_steps', type=int, default=4, help='梯度累积步数')

    # misc - 其他配置
    p.add_argument('--log', choices=['wandb', 'tensorboard', 'none'], default='tensorboard', 
                   help='日志记录方式：wandb、tensorboard 或 none')
    p.add_argument('--save_every', type=int, default=50, help='每 N 个优化器步保存一次检查点')
    p.add_argument('--keep_last_k', type=int, default=2, 
                   help='保留最后 K 个步数检查点（加上 model_last.pt）')
    args = p.parse_args()

    # ========== 设备设置 ==========
    # 自动检测并使用 CUDA（如果可用），否则使用 CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # ========== 输出目录和检查点处理 ==========
    # 创建输出目录
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    # 检查是否存在检查点文件
    ckpt_path = out_dir / "model_last.pt"
    have_ckpt = ckpt_path.exists()

    # ---- 如果存在检查点，加载元数据 ----
    ckpt = None
    saved_tok_dir = None
    if have_ckpt:
        # 加载检查点文件
        ckpt = torch.load(str(ckpt_path), map_location=device)
        # 验证检查点包含必要的配置信息
        if "config" not in ckpt:
            raise RuntimeError(
                "Checkpoint is missing 'config'."
                "Please re-save a checkpoint that includes the model config."
            )
        # 尝试读取保存的分词器目录路径
        tok_file = ckpt_path.with_name("tokenizer_dir.txt")
        saved_tok_dir = tok_file.read_text().strip() if tok_file.exists() else None

    # ========== 分词器初始化 ==========
    tok = None
    tok_dir = None
    if have_ckpt:
        # 从检查点恢复：加载之前保存的分词器
        if not saved_tok_dir:
            raise RuntimeError(
                "Checkpoint was found but tokenizer_dir.txt is missing. "
                "Resume requires the original tokenizer."
            )
        tok = BPETokenizer()
        tok.load(saved_tok_dir)  # 加载保存的分词器
        tok_dir = saved_tok_dir
        vocab_size = tok.vocab_size
        print(f"[resume] Loaded tokenizer from {tok_dir} (vocab={vocab_size})")
    else:
        # 首次训练：创建新的分词器
        if args.bpe:
            # 训练 BPE 分词器
            tok = BPETokenizer(vocab_size=args.vocab_size)
            tok.train(args.data)  # 在训练数据上训练分词器
            tok_dir = str(out_dir / 'tokenizer')
            Path(tok_dir).mkdir(parents=True, exist_ok=True)
            tok.save(tok_dir)  # 保存分词器以便后续使用
            vocab_size = tok.vocab_size
            print(f"[init] Trained tokenizer to {tok_dir} (vocab={vocab_size})")
        else:
            # 不使用 BPE，使用字节级回退（不推荐用于 Part 4）
            tok = None
            vocab_size = 256  # 字节级回退（不推荐用于 Part 4）

    # ========== 数据集加载 ==========
    # 创建训练数据加载器，支持打乱顺序
    train_loader = make_loader(args.data, tok, args.block_size, args.batch_size, shuffle=True)

    # ========== 构建模型配置 ==========
    if have_ckpt:
        # 从检查点恢复：使用检查点中的配置
        cfg_build = ckpt["config"]
        # 验证词汇表大小一致性（恢复训练时不允许改变词汇表大小）
        if cfg_build.get("vocab_size") != vocab_size:
            raise RuntimeError(
                f"Tokenizer vocab ({vocab_size}) != checkpoint config vocab ({cfg_build.get('vocab_size')}). "
                "This deterministic script forbids vocab changes on resume."
            )
    else:
        # 首次训练：从命令行参数构建配置
        cfg_build = run_cfg_from_args(args, vocab_size)

    # ========== 初始化模型/优化器/调度器/混合精度 ==========
    # 创建 GPT 模型并移动到指定设备
    model = GPTModern(**cfg_build).to(device)
    # 使用 AdamW 优化器，设置学习率、beta 参数和权重衰减
    optim = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=0.1)

    # 计算总步数（取命令行指定步数和按轮数计算的步数中的较小值）
    total_steps = min(args.steps, args.epochs * len(train_loader))
    # 计算预热步数（至少为总步数的 10%，但不超过指定的预热步数）
    warmup = min(args.warmup_steps, max(total_steps // 10, 1))
    # 创建学习率调度器（预热 + 余弦退火）
    sched = WarmupCosineLR(optim, warmup_steps=warmup, total_steps=total_steps, base_lr=args.lr)

    # 创建混合精度训练和梯度累积管理器
    amp = AmpGrad(optim, accum=args.grad_accum_steps, amp=args.mixed_precision)

    # ========== 严格恢复检查点 ==========
    step = 0
    if have_ckpt:
        # 从检查点恢复模型、优化器、调度器和混合精度状态
        # strict=True 确保所有状态都完全匹配
        step = load_checkpoint(model, str(ckpt_path), optimizer=optim, scheduler=sched, amp=amp, strict=True)
        print(f"[resume] Loaded checkpoint at step {step}")

    # ========== 日志初始化 ==========
    # 初始化日志记录器（支持 wandb、tensorboard 或 none）
    logger = init_logger(args.log, out_dir=str(out_dir))
    # 记录超参数到 TensorBoard
    _log_hparams_tb(logger, args, total_steps)
    # 如果是 TensorBoard，尝试记录计算图
    if _is_tb(logger):
        try:
            ex_x, ex_y = next(iter(train_loader))
            _maybe_log_graph_tb(logger, model, ex_x.to(device), ex_y.to(device))
        except Exception:
            # 如果记录计算图失败，忽略错误继续执行
            pass

    # ========== 优雅保存：处理 SIGINT/SIGTERM 信号 ==========
    # 设置信号处理器，在收到中断信号时保存检查点
    
    = {"flag": False}  # 使用字典以便在嵌套函数中修改
    
    def _on_term(sig, frame):
        """信号处理函数：设置保存标志"""
        save_requested["flag"] = True
    
    # 注册信号处理器（SIGTERM: 终止信号, SIGINT: Ctrl+C）
    signal.signal(signal.SIGTERM, _on_term)
    signal.signal(signal.SIGINT,  _on_term)

    # ========== 训练循环 ==========
    model.train()  # 设置模型为训练模式
    while step < args.steps:
        # 遍历训练数据
        for xb, yb in train_loader:
            # 检查是否达到最大步数
            if step >= args.steps:
                break
            # 检查是否收到中断信号，如果是则保存并退出
            if save_requested["flag"]:
                atomic_save_all(model, optim, sched, amp, step, out_dir, tok_dir, args.keep_last_k, cfg_build)
                print(f"[signal] Saved checkpoint at step {step} to {out_dir}. Exiting.")
                return

            # 记录迭代开始时间（用于计算吞吐量）
            it_t0 = time.time()
            # 将数据移动到指定设备（GPU 或 CPU）
            xb, yb = xb.to(device), yb.to(device)
            
            # 前向传播（使用混合精度自动转换）
            with torch.cuda.amp.autocast(enabled=amp.amp):
                logits, loss, _ = model(xb, yb)  # 计算 logits 和损失
            
            # 反向传播（支持梯度累积）
            amp.backward(loss)

            # 检查是否应该执行优化器步骤（考虑梯度累积）
            if amp.should_step():
                # 执行优化器步骤并清零梯度
                amp.step()
                amp.zero_grad()
                # 更新学习率（调度器步进）
                lr = sched.step()
                step += 1

                # 定期保存检查点
                if step % args.save_every == 0:
                    atomic_save_all(model, optim, sched, amp, step, out_dir, tok_dir, args.keep_last_k, cfg_build)
                    if _is_tb(logger):
                        logger.text("meta/checkpoint", f"Saved at step {step}", step)

                # 定期记录日志（每 50 步）
                if step % 50 == 0:
                    # 记录基本指标（步数、损失、学习率）
                    logger.log(step=step, loss=float(loss.item()), lr=float(lr))
                    # 记录运行时统计（吞吐量等）
                    _log_runtime(logger, step, it_t0, xb, device)
                    # 记录模型统计信息（参数分布等）
                    _log_model_stats(logger, model, step, do_hists=False)
                    # 可能记录注意力权重（每 100 步）
                    _maybe_log_attention(logger, model, xb, step, every=100)
                    # 记录生成样本到 TensorBoard
                    _log_samples_tb(logger, model, tok, xb, device, step, max_new_tokens=64)

    # ========== 最终保存 ==========
    # 训练完成后保存最终检查点
    atomic_save_all(model, optim, sched, amp, step, out_dir, tok_dir, args.keep_last_k, cfg_build)
    print(f"Saved checkpoint to {out_dir}/model_last.pt")


if __name__ == '__main__':
    # 当脚本直接运行时，执行主函数
    main()
