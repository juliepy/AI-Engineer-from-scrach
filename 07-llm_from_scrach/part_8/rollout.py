"""
RLHF (Reinforcement Learning from Human Feedback) 的 Rollout 模块
提供用于强化学习训练的 tokenizer、logprob 计算和提示词采样功能
"""
from __future__ import annotations
import torch
from typing import List, Tuple

# tokenizer 优先级: 优先使用 Part 4 的 BPE tokenizer，否则回退到 Part 3 的 ByteTokenizer
import sys
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_4'))
try:
    from tokenizer_bpe import BPETokenizer
    _HAS_BPE = True
except Exception:
    _HAS_BPE = False
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
try:
    from tokenizer import ByteTokenizer
except Exception:
    ByteTokenizer = None

# 尝试导入 part_6 的 formatters（可选依赖）
sys.path.append(str(_P(__file__).resolve().parents[1]))
try:
    from part_6.formatters import Example, format_example, format_prompt_only
    _HAS_FORMATTERS = True
except Exception:
    _HAS_FORMATTERS = False
    # 定义占位符以避免导入错误
    Example = None
    format_example = None
    format_prompt_only = None

# ---------- tokenizer helpers ----------
class RLHFTokenizer:
    """
    RLHF 专用的 Tokenizer 封装类
    自动选择可用的 tokenizer（优先 BPE，回退到 ByteTokenizer）
    """
    def __init__(self, block_size: int, bpe_dir: str | None = None, vocab_size: int = 8000):
        """
        初始化 RLHF Tokenizer
        
        Args:
            block_size: 序列的最大长度
            bpe_dir: BPE tokenizer 的模型目录路径（可选）
            vocab_size: BPE tokenizer 的词汇表大小（默认 8000）
        """
        self.block_size = block_size
        self.tok = None
        # 优先尝试使用 BPE tokenizer
        if _HAS_BPE:
            try:
                self.tok = BPETokenizer(vocab_size=vocab_size)
                if bpe_dir:
                    self.tok.load(bpe_dir)
            except Exception:
                self.tok = None
        # 如果 BPE 不可用，回退到 ByteTokenizer
        if self.tok is None and ByteTokenizer is not None:
            self.tok = ByteTokenizer()
        if self.tok is None:
            raise RuntimeError("No tokenizer available for RLHF.")

    @property
    def vocab_size(self) -> int:
        """返回词汇表大小"""
        return getattr(self.tok, 'vocab_size', 256)

    def encode(self, text: str) -> List[int]:
        """
        将文本编码为 token ID 列表
        
        Args:
            text: 输入文本
            
        Returns:
            token ID 列表
        """
        ids = self.tok.encode(text)
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        return ids

    def decode(self, ids: List[int]) -> str:
        """
        将 token ID 列表解码为文本
        
        Args:
            ids: token ID 列表
            
        Returns:
            解码后的文本
        """
        if hasattr(self.tok, 'decode'):
            return self.tok.decode(ids)
        return bytes(ids).decode('utf-8', errors='ignore')

# ---------- logprob utilities ----------

def shift_labels(x: torch.Tensor) -> torch.Tensor:
    """
    为因果语言模型移动标签
    因果 LM 需要预测 x[t+1]，所以标签需要从 x[1:] 开始
    
    Args:
        x: 输入序列张量，形状为 (B, T)
        
    Returns:
        移动后的标签，形状为 (B, T-1)
    """
    return x[:, 1:].contiguous()

def gather_logprobs(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """
    计算给定标签的对数概率
    
    Args:
        logits: 模型输出的 logits，形状为 (B, T, V)，其中 V 是词汇表大小
        labels: 标签序列，形状为 (B, T)
        
    Returns:
        每个 token 的对数概率，形状为 (B, T)
    """
    logp = torch.log_softmax(logits, dim=-1)
    return logp.gather(-1, labels.unsqueeze(-1)).squeeze(-1)

@torch.no_grad()
def model_logprobs(model, x: torch.Tensor) -> torch.Tensor:
    """
    计算模型对输入序列的对数概率
    对于每个位置 t，计算 log p(x[t+1] | x[:t])
    
    Args:
        model: 语言模型（需要有 lm 方法或可直接调用）
        x: 输入序列，形状为 (B, T)
        
    Returns:
        每个位置的对数概率，形状为 (B, T-1)
    """
    logits, _, _ = model.lm(x, None) if hasattr(model, 'lm') else model(x, None)
    labels = shift_labels(x)
    lp = gather_logprobs(logits[:, :-1, :], labels)
    return lp  # (B, T-1)

# ---------- KL divergence ----------

def approx_kl(policy_logp: torch.Tensor, ref_logp: torch.Tensor) -> torch.Tensor:
    """
    计算策略模型和参考模型之间的近似 KL 散度
    KL(策略||参考) ≈ (logp_policy - logp_ref).mean()
    
    Args:
        policy_logp: 策略模型的对数概率
        ref_logp: 参考模型的对数概率
        
    Returns:
        近似的 KL 散度值（标量）
    """
    return (policy_logp - ref_logp).mean()

# ---------- prompt source ----------
try:
    from datasets import load_dataset as _load_ds
except Exception:
    _load_ds = None

def sample_prompts(n: int) -> List[str]:
    """
    采样 n 个提示词用于训练
    
    优先从 Alpaca 数据集加载，如果不可用则使用内置的默认提示词
    
    Args:
        n: 需要采样的提示词数量
        
    Returns:
        提示词列表
    """
    if _load_ds is not None:
        try:
            # 尝试从 Alpaca 数据集加载
            ds = _load_ds("tatsu-lab/alpaca", split="train[:24]")
            arr = []
            for r in ds:
                inst = (r.get('instruction') or '').strip()
                inp = (r.get('input') or '').strip()
                if inp:
                    inst = inst + "\n" + inp
                if inst:
                    arr.append(inst)
                if len(arr) >= n:
                    break
            if arr:
                return arr
        except Exception:
            pass
    # 回退到默认提示词
    base = [
        "Explain the purpose of attention in transformers.",
        "Give two pros and cons of BPE tokenization.",
        "Summarize why PPO is used in RLHF.",
        "Write a tiny Python function that reverses a list.",
    ]
    return (base * ((n+len(base)-1)//len(base)))[:n]


# ---------- 测试代码 ----------
if __name__ == "__main__":
    print("=" * 60)
    print("RLHF Rollout 模块测试")
    print("=" * 60)
    
    # 测试 1: Tokenizer 初始化
    print("\n[1] Tokenizer 初始化", end=" ... ")
    try:
        tokenizer = RLHFTokenizer(block_size=128, vocab_size=8000)
        print(f"✓ (vocab_size={tokenizer.vocab_size}, type={type(tokenizer.tok).__name__})")
    except Exception as e:
        print(f"✗ {e}")
        tokenizer = None
    
    # 测试 2: 编码/解码
    if tokenizer is not None:
        print("[2] 文本编码/解码", end=" ... ")
        try:
            test_text = "Hello, world! 测试中文"
            ids = tokenizer.encode(test_text)
            decoded = tokenizer.decode(ids)
            match = "✓" if decoded == test_text else "⚠"
            print(f"{match} (tokens={len(ids)}, match={decoded==test_text})")
        except Exception as e:
            print(f"✗ {e}")
    
    # 测试 3: shift_labels
    print("[3] shift_labels", end=" ... ")
    try:
        x = torch.tensor([[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]])
        shifted = shift_labels(x)
        assert shifted.shape[1] == x.shape[1] - 1
        print(f"✓ ({x.shape} -> {shifted.shape})")
    except Exception as e:
        print(f"✗ {e}")
    
    # 测试 4: gather_logprobs
    print("[4] gather_logprobs", end=" ... ")
    try:
        logits = torch.randn(2, 5, 10)
        labels = torch.randint(0, 10, (2, 5))
        logprobs = gather_logprobs(logits, labels)
        assert (logprobs <= 0).all()
        print(f"✓ (shape={logprobs.shape}, mean={logprobs.mean().item():.3f})")
    except Exception as e:
        print(f"✗ {e}")
    
    # 测试 5: approx_kl
    print("[5] approx_kl", end=" ... ")
    try:
        policy_logp = torch.tensor([[-2.0, -1.5, -2.5], [-1.8, -2.2, -1.9]])
        ref_logp = torch.tensor([[-2.1, -1.6, -2.6], [-1.9, -2.3, -2.0]])
        kl = approx_kl(policy_logp, ref_logp)
        assert kl.item() >= -1e-6
        print(f"✓ (KL={kl.item():.4f})")
    except Exception as e:
        print(f"✗ {e}")
    
    # 测试 6: model_logprobs (可选)
    print("[6] model_logprobs", end=" ... ")
    try:
        sys.path.append(str(_P(__file__).resolve().parent))
        from policy import PolicyWithValue
        vocab_size = 256 if tokenizer is None else tokenizer.vocab_size
        model = PolicyWithValue(vocab_size=vocab_size, block_size=32, n_layer=2, n_head=2, n_embd=64)
        model.eval()
        x = torch.randint(0, vocab_size, (2, 10))
        logprobs = model_logprobs(model, x)
        print(f"✓ (shape={logprobs.shape}, params={sum(p.numel() for p in model.parameters()):,})")
    except Exception as e:
        print(f"⚠ 跳过 ({str(e)[:40]}...)")
    
    # 测试 7: sample_prompts
    print("[7] sample_prompts", end=" ... ")
    try:
        prompts = sample_prompts(3)
        assert len(prompts) == 3
        avg_len = sum(len(p) for p in prompts) / len(prompts)
        print(f"✓ (count={len(prompts)}, avg_len={avg_len:.0f})")
    except Exception as e:
        print(f"✗ {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)