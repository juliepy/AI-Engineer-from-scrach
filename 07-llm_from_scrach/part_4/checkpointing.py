"""
检查点保存和加载模块

本模块提供了模型训练过程中的检查点（checkpoint）保存和加载功能，包括：
- TensorBoard 日志记录辅助函数
- 模型配置提取和验证
- 检查点保存和加载
- 原子保存工具函数
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]/'part_3'))
import time
import torch
import shutil
import torch.nn as nn

# 默认检查点文件名
DEF_NAME = "model_last.pt"

# ----------------------------- TensorBoard 日志辅助函数（如果不是 TB logger 则安全地不执行） ----------------------------- #

def _is_tb(logger) -> bool:
    """
    检查 logger 是否是 TensorBoard logger
    
    Args:
        logger: 日志记录器对象
        
    Returns:
        bool: 如果是 TensorBoard logger 返回 True，否则返回 False
    """
    return getattr(logger, "w", None) is not None


def _log_hparams_tb(logger, args, total_steps):
    """
    将超参数记录到 TensorBoard
    
    Args:
        logger: TensorBoard 日志记录器
        args: 包含训练超参数的对象
        total_steps: 总训练步数
    """
    if not _is_tb(logger): return
    try:
        # 构建超参数字典
        h = dict(
            vocab_size=args.vocab_size, block_size=args.block_size, n_layer=args.n_layer,
            n_head=args.n_head, n_embd=args.n_embd, dropout=args.dropout, lr=args.lr,
            warmup_steps=args.warmup_steps, batch_size=args.batch_size, grad_accum=args.grad_accum_steps,
            mixed_precision=args.mixed_precision, steps=args.steps, epochs=args.epochs,
        )
        # 记录超参数和元数据
        logger.hparams(h, {"meta/total_steps": float(total_steps)})
    except Exception:
        pass

def _maybe_log_graph_tb(logger, model, xb, yb):
    """
    如果 logger 支持，则记录模型计算图到 TensorBoard
    
    Args:
        logger: TensorBoard 日志记录器
        model: 要记录计算图的模型
        xb: 输入批次张量
        yb: 目标批次张量（可选）
    """
    if not hasattr(logger, "graph"): 
        return
    try:
        # 创建一个包装器，只返回张量输出（TensorBoard 需要）
        class _TensorOnly(nn.Module):
            def __init__(self, m): 
                super().__init__(); self.m = m.eval()
            def forward(self, x, y=None):
                out = self.m(x, y) if y is not None else self.m(x)
                # 如果输出是列表或元组，找到第一个张量并返回
                if isinstance(out, (list, tuple)):
                    for o in out:
                        if torch.is_tensor(o):
                            return o
                    return out[0]
                return out
        wrapped = _TensorOnly(model).to(xb.device)
        logger.graph(wrapped, (xb, yb))
    except Exception:
        pass

def _log_model_stats(logger, model, step: int, do_hists: bool = False):
    """
    记录模型统计信息到 TensorBoard，包括参数和梯度的 L2 范数
    
    Args:
        logger: TensorBoard 日志记录器
        model: 要记录统计信息的模型
        step: 当前训练步数
        do_hists: 是否记录每个参数的直方图（默认 False，因为可能很耗时）
    """
    if not _is_tb(logger): return
    try:
        # 获取所有需要梯度的参数
        params = [p for p in model.parameters() if p.requires_grad]
        # 计算所有参数的全局 L2 范数
        total_param_norm = torch.norm(torch.stack([p.detach().norm(2) for p in params]), 2).item()
        # 获取所有非空梯度
        grads = [p.grad for p in params if p.grad is not None]
        total_grad_norm = float('nan')
        if grads:
            # 计算所有梯度的全局 L2 范数
            total_grad_norm = torch.norm(torch.stack([g.detach().norm(2) for g in grads]), 2).item()
        # 记录标量值
        logger.log(step=step, **{
            "train/param_global_l2": total_param_norm,
            "train/grad_global_l2": total_grad_norm,
        })
        # 可选：记录每个参数的直方图
        if do_hists:
            for name, p in model.named_parameters():
                logger.hist(f"params/{name}", p, step)
                if p.grad is not None:
                    logger.hist(f"grads/{name}", p.grad, step)
    except Exception:
        pass

def _maybe_log_attention(logger, model, xb, step: int, every: int = 100):
    """
    记录每个 Transformer 块的 Q/K/V 直方图到 TensorBoard
    
    使用当前小批次 xb 记录注意力机制的 Q/K/V 值。不修改模型，不使用钩子。
    运行轻量级的无梯度前向传播来重新计算注意力路径。
    - 只取第一个批次和第一个头，以保持日志文件小
    - 使用 RoPE 之前的值（更简单且对直方图更稳定）
    
    Args:
        logger: TensorBoard 日志记录器
        model: Transformer 模型
        xb: 输入批次张量
        step: 当前训练步数
        every: 每隔多少步记录一次（默认 100）
    """
    if not _is_tb(logger) or step == 0 or (step % every):
        return
    try:
        import torch
        with torch.no_grad(), torch.cuda.amp.autocast(enabled=False):
            # 重新创建块看到的输入
            x = model.tok_emb(xb)           # (B,T,C) 词嵌入
            x = model.drop(x)                # Dropout

            B, T, _ = x.shape
            for li, blk in enumerate(getattr(model, "blocks", [])):
                h = blk.ln1(x)              # 注意力前的归一化隐藏状态

                attn = blk.attn
                # 像模块一样投影到 Q/K/V（为简单起见使用 RoPE 之前的值）
                q = attn.wq(h).view(B, T, attn.n_head,   attn.d_head).transpose(1, 2)      # (B,H,T,D)
                k = attn.wk(h).view(B, T, attn.n_kv_head, attn.d_head).transpose(1, 2)     # (B,Hk,T,D)
                v = attn.wv(h).view(B, T, attn.n_kv_head, attn.d_head).transpose(1, 2)     # (B,Hk,T,D)

                # 取一小片数据以保持日志轻量
                q1 = q[:1, :1].contiguous().view(-1).float().cpu()
                k1 = k[:1, :1].contiguous().view(-1).float().cpu()
                v1 = v[:1, :1].contiguous().view(-1).float().cpu()

                # 丢弃非有限值（防御性编程）
                q1 = q1[torch.isfinite(q1)]
                k1 = k1[torch.isfinite(k1)]
                v1 = v1[torch.isfinite(v1)]

                # 记录直方图
                if q1.numel() > 0: logger.hist(f"qkv/block{li}/q_hist", q1, step)
                if k1.numel() > 0: logger.hist(f"qkv/block{li}/k_hist", k1, step)
                if v1.numel() > 0: logger.hist(f"qkv/block{li}/v_hist", v1, step)

                # 可选的标量值（范数）显示在时间序列中
                if q1.numel(): logger.log(step=step, **{f"qkv/block{li}/q_l2_mean": float(q1.square().mean().sqrt())})
                if k1.numel(): logger.log(step=step, **{f"qkv/block{li}/k_l2_mean": float(k1.square().mean().sqrt())})
                if v1.numel(): logger.log(step=step, **{f"qkv/block{li}/v_l2_mean": float(v1.square().mean().sqrt())})

                # 使用廉价近似推进到下一个块，避免重复完整计算：
                # 只使用模型自己的 FFN 路径；跳过重新运行注意力（我们只记录注意力前的统计信息）
                x = x + blk.ffn(blk.ln2(x))

    except Exception as e:
        print(f"[qkv] logging failed: {e}")


def _log_runtime(logger, step: int, it_t0: float, xb, device):
    """
    记录运行时统计信息到 TensorBoard，包括吞吐量、步时间和 GPU 内存使用
    
    Args:
        logger: TensorBoard 日志记录器
        step: 当前训练步数
        it_t0: 迭代开始时间
        xb: 输入批次张量（用于计算 token 数量）
        device: 设备（用于检查 CUDA 是否可用）
    """
    try:
        dt = time.time() - it_t0  # 计算迭代耗时
        toks = int(xb.numel())    # 计算 token 总数
        toks_per_s = toks / max(dt, 1e-6)  # 计算吞吐量（tokens/秒）
        mem = torch.cuda.memory_allocated()/(1024**2) if torch.cuda.is_available() else 0.0  # GPU 内存使用（MB）
        logger.log(step=step, **{
            "sys/throughput_tokens_per_s": toks_per_s,
            "sys/step_time_s": dt,
            "sys/gpu_mem_alloc_mb": mem
        })
    except Exception:
        pass

def _log_samples_tb(logger, model, tok, xb, device, step: int, max_new_tokens: int = 64):
    """
    记录模型生成的文本样本到 TensorBoard
    
    Args:
        logger: TensorBoard 日志记录器
        model: 生成模型
        tok: 分词器
        xb: 输入批次张量
        device: 设备
        step: 当前训练步数
        max_new_tokens: 最大生成 token 数（默认 64）
    """
    if not _is_tb(logger): return
    if tok is None: return
    try:
        model.eval()
        with torch.no_grad():
            # 使用第一个样本生成文本
            out = model.generate(xb[:1].to(device), max_new_tokens=max_new_tokens, temperature=1.0, top_k=50)
        model.train()
        text = tok.decode(out[0].tolist())
        logger.text("samples/generation", text, step)
    except Exception:
        pass
# ---------------------------------------------------------------------- #

def _extract_config_from_model(model) -> dict:
    """
    从模型中尽力提取 GPTModern 风格的配置，包括 GQA（分组查询注意力）字段
    
    Args:
        model: 要提取配置的模型
        
    Returns:
        dict: 包含模型配置的字典，如果提取失败则返回空字典
    """
    cfg = {}
    try:
        tok_emb = getattr(model, "tok_emb", None)
        blocks = getattr(model, "blocks", None)
        if tok_emb is None or not blocks:
            return cfg

        # 尝试导入 SwiGLU（可选依赖）
        try:
            from swiglu import SwiGLU  # optional
        except Exception:
            class SwiGLU: pass

        # 基础配置
        cfg["vocab_size"] = int(tok_emb.num_embeddings)  # 词汇表大小
        cfg["block_size"]  = int(getattr(model, "block_size", 0) or 0)  # 序列长度
        cfg["n_layer"]     = int(len(blocks))  # Transformer 层数

        first_blk = blocks[0]
        attn = getattr(first_blk, "attn", None)
        if attn is None:
            return cfg

        # 注意力头数和维度
        cfg["n_head"]   = int(getattr(attn, "n_head"))  # 查询头数
        d_head          = int(getattr(attn, "d_head"))  # 每个头的维度
        cfg["n_embd"]   = int(cfg["n_head"] * d_head)  # 嵌入维度
        cfg["n_kv_head"]= int(getattr(attn, "n_kv_head", cfg["n_head"]))  # K/V 头数（默认等于查询头数，即 MHA）

        # Dropout（如果存在）
        drop = getattr(attn, "dropout", None)
        cfg["dropout"] = float(getattr(drop, "p", 0.0)) if drop is not None else 0.0

        # 归一化和 FFN 风格
        cfg["use_rmsnorm"] = isinstance(getattr(model, "ln_f", None), nn.Identity)  # 是否使用 RMSNorm
        cfg["use_swiglu"]  = isinstance(getattr(first_blk, "ffn", None), SwiGLU)  # 是否使用 SwiGLU

        # 位置编码/注意力技巧
        for k in ("rope", "max_pos", "sliding_window", "attention_sink"):
            if hasattr(attn, k):
                val = getattr(attn, k)
                cfg[k] = int(val) if isinstance(val, bool) else val
    except Exception:
        return {}
    return cfg

def _verify_model_matches(model, cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """
    验证模型架构是否与配置匹配
    
    Args:
        model: 要验证的模型
        cfg: 配置字典
        
    Returns:
        Tuple[bool, str]: (是否匹配, 消息)
    """
    # 从配置中获取期望的架构参数
    expected = {
        "block_size": cfg.get("block_size"),
        "n_layer":    cfg.get("n_layer"),
        "n_head":     cfg.get("n_head"),
        "n_embd":     cfg.get("n_embd"),
        "vocab_size": cfg.get("vocab_size"),
        "n_kv_head":  cfg.get("n_kv_head", cfg.get("n_head")),
    }
    # 从模型中获取实际的架构参数
    got = {
        "block_size": int(getattr(model, "block_size", -1)),
        "n_layer":    int(len(model.blocks)),
        "vocab_size": int(model.tok_emb.num_embeddings),
    }
    first_blk = model.blocks[0]
    got.update({
        "n_head":     int(first_blk.attn.n_head),
        "n_embd":     int(first_blk.attn.n_head * first_blk.attn.d_head),
        "n_kv_head":  int(getattr(first_blk.attn, "n_kv_head", first_blk.attn.n_head)),
    })
    # 找出不匹配的参数
    diffs = [f"{k}: ckpt={expected[k]} vs model={got[k]}" for k in expected if expected[k] != got[k]]
    if diffs:
        return False, "Architecture mismatch:\n  " + "\n  ".join(diffs)
    return True, "ok"


def save_checkpoint(model, optimizer, scheduler, amp, step: int, out_dir: str,
                    tokenizer_dir: str | None = None, config: dict | None = None):
    """
    保存训练检查点到磁盘
    
    保存模型状态、优化器状态、学习率调度器状态、混合精度缩放器状态和配置信息。
    
    Args:
        model: 要保存的模型
        optimizer: 优化器（可为 None）
        scheduler: 学习率调度器（可为 None）
        amp: 混合精度管理器（可为 None）
        step: 当前训练步数
        out_dir: 输出目录路径
        tokenizer_dir: 分词器目录路径（可选）
        config: 模型配置字典（可选，如果模型没有 config 属性则使用此参数）
    """
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)

    # 优先使用模型自己的配置（例如，字典或带有 __dict__/asdict 的数据类）
    if hasattr(model, "config"):
        cfg_obj = model.config
        cfg = dict(cfg_obj) if isinstance(cfg_obj, dict) else getattr(cfg_obj, "__dict__", None) or _extract_config_from_model(model)
    else:
        cfg = config if config is not None else _extract_config_from_model(model)

    # 保存检查点
    torch.save({
        "model": model.state_dict(),  # 模型参数
        "optimizer": optimizer.state_dict() if optimizer is not None else None,  # 优化器状态
        "scheduler": scheduler.state_dict() if hasattr(scheduler, "state_dict") else None,  # 调度器状态
        "amp_scaler": amp.scaler.state_dict() if amp and getattr(amp, "scaler", None) else None,  # 混合精度缩放器状态
        "step": int(step),  # 训练步数
        "config": cfg,   # 模型配置（始终写入）
        "version": "part4-v2",  # 检查点版本
    }, out / DEF_NAME)

    # 如果提供了分词器目录，保存其路径
    if tokenizer_dir is not None:
        (out / "tokenizer_dir.txt").write_text(tokenizer_dir)



def load_checkpoint(model, path: str, optimizer=None, scheduler=None, amp=None, strict: bool = True):
    """
    从磁盘加载训练检查点
    
    加载模型状态、优化器状态、学习率调度器状态和混合精度缩放器状态。
    如果检查点包含配置，会验证模型架构是否匹配。
    
    Args:
        model: 要加载状态的模型
        path: 检查点文件路径
        optimizer: 优化器（可选，如果提供则加载其状态）
        scheduler: 学习率调度器（可选，如果提供则加载其状态）
        amp: 混合精度管理器（可选，如果提供则加载其状态）
        strict: 是否严格匹配状态字典（默认 True）
        
    Returns:
        int: 检查点中保存的训练步数
        
    Raises:
        RuntimeError: 如果架构不匹配或状态字典不匹配（且 strict=True）
    """
    ckpt = torch.load(path, map_location="cpu")

    # 验证模型架构是否与检查点配置匹配
    cfg = ckpt.get("config")
    if cfg:
        ok, msg = _verify_model_matches(model, cfg)
        if not ok:
            raise RuntimeError(msg + "\nRebuild the model with this config, or load with strict=False.")
    else:
        # 旧版检查点没有配置：强烈建议在其他地方重建步骤
        print("[compat] Warning: checkpoint has no config; cannot verify architecture.")

    # 加载模型状态
    missing, unexpected = model.load_state_dict(ckpt["model"], strict=strict)
    if strict and (missing or unexpected):
        raise RuntimeError(f"State dict mismatch:\n  missing: {missing}\n  unexpected: {unexpected}")

    # 加载优化器状态
    if optimizer is not None and ckpt.get("optimizer") is not None:
        optimizer.load_state_dict(ckpt["optimizer"])
    # 加载调度器状态
    if scheduler is not None and ckpt.get("scheduler") is not None and hasattr(scheduler, "load_state_dict"):
        scheduler.load_state_dict(ckpt["scheduler"])
    # 加载混合精度缩放器状态
    if amp is not None and ckpt.get("amp_scaler") is not None and getattr(amp, "scaler", None):
        amp.scaler.load_state_dict(ckpt["amp_scaler"])

    return ckpt.get("step", 0)


# ----------------------------- 检查点/保存工具函数 ----------------------------- #

def checkpoint_paths(out_dir: Path, step: int):
    """
    生成检查点文件路径
    
    Args:
        out_dir: 输出目录
        step: 训练步数
        
    Returns:
        Tuple[Path, Path]: (按步数命名的检查点路径, 最新检查点路径)
    """
    return out_dir / f"model_step{step:07d}.pt", out_dir / "model_last.pt"

def atomic_save_all(model, optim, sched, amp, step: int, out_dir: Path,
                    tok_dir: str | None, keep_last_k: int, config: dict):
    """
    原子保存所有检查点：写入 model_last.pt（带配置）+ 按步数滚动的副本
    
    保存检查点后，会创建一个按步数命名的副本，并清理旧的检查点文件，
    只保留最近的 keep_last_k 个按步数命名的检查点。
    
    Args:
        model: 要保存的模型
        optim: 优化器
        sched: 学习率调度器
        amp: 混合精度管理器
        step: 当前训练步数
        out_dir: 输出目录
        tok_dir: 分词器目录路径（可选）
        keep_last_k: 保留最近多少个按步数命名的检查点
        config: 模型配置字典
    """
    save_checkpoint(model, optim, sched, amp, step, str(out_dir), tok_dir, config=config)  # 写入 model_last.pt
    per_step, last = checkpoint_paths(out_dir, step)
    try:
        # 复制最新检查点到按步数命名的文件
        shutil.copy2(last, per_step)
    except Exception:
        pass
    # 清理旧的按步数命名的检查点
    try:
        ckpts = sorted(out_dir.glob("model_step*.pt"))
        # 删除除了最近 keep_last_k 个之外的所有检查点
        for old in ckpts[:-keep_last_k]:
            old.unlink(missing_ok=True)
    except Exception:
        pass