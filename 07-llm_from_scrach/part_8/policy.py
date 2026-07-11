"""
策略网络模块 (Policy Network Module)

本模块实现了带价值头的策略网络，用于强化学习中的策略优化。
策略网络 = 监督微调的语言模型 (SFT LM) + 价值头 (Value Head)
"""
from __future__ import annotations
import torch, torch.nn as nn
import sys
from pathlib import Path as _P

# 尝试使用用户自定义的目录结构
# 首先尝试从 part_3 目录导入模型
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
try:
    from model_utils.model_modern import GPTModern  # 用户自定义路径
except Exception:
    from model_modern import GPTModern  # 回退到默认路径


class PolicyWithValue(nn.Module):
    """策略网络 = 监督微调的语言模型 (SFT LM) + 小型价值头 (Value Head)
    
    注意：为了简化实现，我们将价值头放置在语言模型的 logits 输出之上 (vocab_size → 1)。
    这样可以避免依赖隐藏状态的内部结构，同时保持教程的可运行性。
    
    在强化学习中，策略网络用于：
    - 生成动作（文本序列）
    - 估计状态价值（用于优势函数计算）
    """
    def __init__(self, vocab_size: int, block_size: int, n_layer=4, n_head=4, n_embd=256,
                 use_rmsnorm=True, use_swiglu=True, rope=True, dropout=0.0):
        """
        初始化策略网络
        
        参数:
            vocab_size: 词汇表大小
            block_size: 序列最大长度（上下文窗口大小）
            n_layer: Transformer 层数，默认 4
            n_head: 注意力头数，默认 4
            n_embd: 嵌入维度，默认 256
            use_rmsnorm: 是否使用 RMSNorm，默认 True
            use_swiglu: 是否使用 SwiGLU 激活函数，默认 True
            rope: 是否使用旋转位置编码 (RoPE)，默认 True
            dropout: Dropout 比率，默认 0.0
        """
        super().__init__()
        # 初始化语言模型（监督微调后的 GPT 模型）
        self.lm = GPTModern(vocab_size=vocab_size, block_size=block_size, n_layer=n_layer,
                            n_head=n_head, n_embd=n_embd, use_rmsnorm=use_rmsnorm,
                            use_swiglu=use_swiglu, rope=rope, dropout=dropout)
        # 价值头：将 logits 映射到标量价值
        # 形状变换: (B, T, V) -> (B, T, 1) -> (B, T)
        # B: batch size, T: sequence length, V: vocab size
        self.val_head = nn.Linear(vocab_size, 1, bias=False)

    def forward(self, x: torch.Tensor, y: torch.Tensor | None = None):
        """
        前向传播
        
        参数:
            x: 输入序列，形状为 (B, T)
            y: 目标序列（可选），形状为 (B, T)，用于计算损失
            
        返回:
            logits: 语言模型的输出 logits，形状为 (B, T, V)
            values: 价值估计，形状为 (B, T)
            loss: 交叉熵损失（如果提供了 y），否则为 None
        """
        # 委托给语言模型的前向传播；返回 logits (B,T,V), loss, _
        logits, loss, _ = self.lm(x, y)
        # 通过价值头计算状态价值，并移除最后一个维度
        values = self.val_head(logits).squeeze(-1)  # (B, T)
        return logits, values, loss

    def generate(self, *args, **kwargs):
        """
        生成文本序列
        
        将生成任务委托给底层语言模型的 generate 方法
        
        参数:
            *args, **kwargs: 传递给语言模型 generate 方法的参数
            
        返回:
            生成的文本序列
        """
        return self.lm.generate(*args, **kwargs)


# ---------- 测试代码 ----------
if __name__ == "__main__":
    print("=" * 60)
    print("Policy Network 模块测试")
    print("=" * 60)
    
    # 测试 1: 模型初始化
    print("\n[1] 模型初始化", end=" ... ")
    try:
        vocab_size, block_size = 256, 32
        model = PolicyWithValue(
            vocab_size=vocab_size,
            block_size=block_size,
            n_layer=2,
            n_head=2,
            n_embd=64
        )
        param_count = sum(p.numel() for p in model.parameters())
        print(f"✓ (params={param_count:,}, vocab={vocab_size}, block={block_size})")
    except Exception as e:
        print(f"✗ {e}")
        model = None
    
    # 测试 2: 前向传播（无目标）
    if model is not None:
        print("[2] 前向传播 (无目标)", end=" ... ")
        try:
            model.eval()
            batch_size, seq_len = 2, 10
            x = torch.randint(0, vocab_size, (batch_size, seq_len))
            
            with torch.no_grad():
                logits, values, loss = model(x, None)
            
            assert logits.shape == (batch_size, seq_len, vocab_size)
            assert values.shape == (batch_size, seq_len)
            assert loss is None
            print(f"✓ (logits={logits.shape}, values={values.shape}, loss=None)")
        except Exception as e:
            print(f"✗ {e}")
    
    # 测试 3: 前向传播（有目标）
    if model is not None:
        print("[3] 前向传播 (有目标)", end=" ... ")
        try:
            y = torch.randint(0, vocab_size, (batch_size, seq_len))
            with torch.no_grad():
                logits, values, loss = model(x, y)
            
            assert logits.shape == (batch_size, seq_len, vocab_size)
            assert values.shape == (batch_size, seq_len)
            assert loss is not None and loss.item() >= 0
            print(f"✓ (loss={loss.item():.4f}, values_mean={values.mean().item():.3f})")
        except Exception as e:
            print(f"✗ {e}")
    
    # 测试 4: 价值头输出范围
    if model is not None:
        print("[4] 价值头输出", end=" ... ")
        try:
            with torch.no_grad():
                _, values, _ = model(x, None)
            print(f"✓ (shape={values.shape}, range=[{values.min().item():.3f}, {values.max().item():.3f}])")
        except Exception as e:
            print(f"✗ {e}")
    
    # 测试 5: 生成功能（如果可用）
    if model is not None:
        print("[5] 生成功能", end=" ... ")
        try:
            idx = torch.randint(0, vocab_size, (1, 5))
            with torch.no_grad():
                generated = model.generate(idx, max_new_tokens=5, temperature=1.0)
            assert generated.shape[1] >= idx.shape[1]
            print(f"✓ (input_len={idx.shape[1]}, output_len={generated.shape[1]})")
        except Exception as e:
            print(f"⚠ 跳过 ({str(e)[:40]}...)")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)