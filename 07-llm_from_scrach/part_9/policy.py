"""
策略网络定义
策略网络 = SFT语言模型 + 小型价值头
注意：为了简化，我们将价值头放在LM的logits之上（vocab→1），
这样可以避免依赖隐藏状态的内部结构，同时保持教程的可运行性
"""
from __future__ import annotations
import torch, torch.nn as nn
import sys
from pathlib import Path as _P
# 首先尝试用户自定义的结构
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
try:
    from model_utils.model_modern import GPTModern  # 用户自定义路径
except Exception:
    from model_modern import GPTModern  # 回退路径

class PolicyWithValue(nn.Module):
    """
    策略网络 = SFT语言模型 + 小型价值头
    
    注意：为了简化，我们将价值头放在LM的logits之上（vocab→1）。
    这样可以避免依赖隐藏状态的内部结构，同时保持教程的可运行性。
    在GRPO中，价值头实际上不会被使用。
    """
    def __init__(self, vocab_size: int, block_size: int, n_layer=4, n_head=4, n_embd=256,
                 use_rmsnorm=True, use_swiglu=True, rope=True, dropout=0.0):
        """
        初始化策略网络
        
        Args:
            vocab_size: 词汇表大小
            block_size: 上下文长度
            n_layer: Transformer层数
            n_head: 注意力头数
            n_embd: 嵌入维度
            use_rmsnorm: 是否使用RMSNorm
            use_swiglu: 是否使用SwiGLU激活
            rope: 是否使用RoPE位置编码
            dropout: Dropout比率
        """
        super().__init__()
        # 基础语言模型（来自Part 3的现代GPT实现）
        self.lm = GPTModern(vocab_size=vocab_size, block_size=block_size, n_layer=n_layer,
                            n_head=n_head, n_embd=n_embd, use_rmsnorm=use_rmsnorm,
                            use_swiglu=use_swiglu, rope=rope, dropout=dropout)
        # 价值头：在logits之上（玩具实现）
        # 形状变换：(B,T,V) -> (B,T,1) -> (B,T)
        self.val_head = nn.Linear(vocab_size, 1, bias=False)

    def forward(self, x: torch.Tensor, y: torch.Tensor | None = None):
        """
        前向传播
        
        Args:
            x: 输入token序列，形状为(B, T)
            y: 目标token序列（可选），形状为(B, T)
        
        Returns:
            logits: 语言模型的logits，形状为(B, T, V)
            values: 价值估计，形状为(B, T)
            loss: 语言模型损失（如果提供了y）
        """
        # 委托给LM的前向传播；返回logits (B,T,V), loss, _
        logits, loss, _ = self.lm(x, y)
        # 计算价值估计
        values = self.val_head(logits).squeeze(-1)  # (B,T)
        return logits, values, loss

    def generate(self, *args, **kwargs):
        """生成文本，直接调用语言模型的generate方法"""
        return self.lm.generate(*args, **kwargs)