"""
Rollout工具函数模块
提供用于RLHF训练的分词器、对数概率计算、KL散度计算和提示采样等功能
"""
from __future__ import annotations
import torch
from typing import List, Tuple

# 分词器优先级：Part 4的BPE → 回退到Part 3的ByteTokenizer
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

# 可选导入 part_6 的格式化工具
try:
    sys.path.append(str(_P(__file__).resolve().parents[1]/'part_6'))
    from formatters import Example, format_example, format_prompt_only
except Exception:
    Example = None
    format_example = None
    format_prompt_only = None

# ---------- 分词器辅助函数 ----------
class RLHFTokenizer:
    """
    RLHF分词器包装类
    支持BPE和字节级分词器，自动选择可用的分词器
    """
    def __init__(self, block_size: int, bpe_dir: str | None = None, vocab_size: int = 8000):
        """
        初始化RLHF分词器
        
        Args:
            block_size: 上下文长度
            bpe_dir: BPE分词器目录（可选）
            vocab_size: 词汇表大小（用于BPE）
        """
        self.block_size = block_size
        self.tok = None
        # 优先尝试使用BPE分词器
        if _HAS_BPE:
            try:
                self.tok = BPETokenizer(vocab_size=vocab_size)
                if bpe_dir:
                    self.tok.load(bpe_dir)
            except Exception:
                self.tok = None
        # 回退到字节级分词器
        if self.tok is None and ByteTokenizer is not None:
            self.tok = ByteTokenizer()
        if self.tok is None:
            raise RuntimeError("No tokenizer available for RLHF.")

    @property
    def vocab_size(self) -> int:
        """返回词汇表大小"""
        return getattr(self.tok, 'vocab_size', 256)

    def encode(self, text: str) -> List[int]:
        """将文本编码为token ID列表"""
        ids = self.tok.encode(text)
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        return ids

    def decode(self, ids: List[int]) -> str:
        """将token ID列表解码为文本"""
        if hasattr(self.tok, 'decode'):
            return self.tok.decode(ids)
        return bytes(ids).decode('utf-8', errors='ignore')

# ---------- 对数概率工具函数 ----------

def shift_labels(x: torch.Tensor) -> torch.Tensor:
    """
    为因果语言模型移动标签
    预测x[t+1]基于x[:t]，所以标签需要右移一位
    """
    return x[:, 1:].contiguous()

def gather_logprobs(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """
    计算给定标签的每token对数概率
    
    Args:
        logits: 模型输出的logits，形状为(B,T,V)
        labels: 目标标签，形状为(B,T)，与logits的T相同
    
    Returns:
        每token的对数概率，形状为(B,T)，即log p(labels)
    """
    logp = torch.log_softmax(logits, dim=-1)
    return logp.gather(-1, labels.unsqueeze(-1)).squeeze(-1)

@torch.no_grad()
def model_logprobs(model, x: torch.Tensor) -> torch.Tensor:
    """
    计算模型的对数概率
    计算log p(x[t+1] | x[:t])，对于t=1..T-1
    
    Args:
        model: 策略模型或语言模型
        x: 输入序列，形状为(B, T)
    
    Returns:
        对数概率，形状为(B, T-1)
    """
    logits, _, _ = model.lm(x, None) if hasattr(model, 'lm') else model(x, None)
    labels = shift_labels(x)
    lp = gather_logprobs(logits[:, :-1, :], labels)
    return lp  # (B, T-1)

# ---------- KL散度计算 ----------

def approx_kl(policy_logp: torch.Tensor, ref_logp: torch.Tensor) -> torch.Tensor:
    """
    计算近似KL散度
    在token上的均值：KL(pi||ref) ≈ (logp_pi - logp_ref).mean()
    
    Args:
        policy_logp: 策略的对数概率
        ref_logp: 参考策略的对数概率
    
    Returns:
        近似的KL散度值
    """
    return (policy_logp - ref_logp).mean()

# ---------- 提示采样 ----------
try:
    from datasets import load_dataset as _load_ds
except Exception:
    _load_ds = None

def sample_prompts(n: int) -> List[str]:
    """
    采样提示文本
    
    Args:
        n: 需要采样的提示数量
    
    Returns:
        提示文本列表
    """
    # 尝试从Alpaca数据集加载
    if _load_ds is not None:
        try:
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
    # 回退到硬编码的基础提示
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
    print("Rollout 模块测试")
    print("=" * 60)
    
    # 测试1: RLHFTokenizer
    print("\n[测试1] RLHFTokenizer 初始化和编码/解码")
    try:
        tokenizer = RLHFTokenizer(block_size=128)
        print(f"✓ 分词器初始化成功")
        print(f"  - 词汇表大小: {tokenizer.vocab_size}")
        print(f"  - 上下文长度: {tokenizer.block_size}")
        
        test_text = "Hello, world!"
        encoded = tokenizer.encode(test_text)
        decoded = tokenizer.decode(encoded)
        print(f"  - 测试文本: '{test_text}'")
        print(f"  - 编码结果: {encoded[:10]}..." if len(encoded) > 10 else f"  - 编码结果: {encoded}")
        print(f"  - 解码结果: '{decoded}'")
        print(f"  - 编码/解码一致性: {'✓' if decoded == test_text else '✗'}")
    except Exception as e:
        print(f"✗ 分词器测试失败: {e}")
    
    # 测试2: shift_labels
    print("\n[测试2] shift_labels 函数")
    try:
        x = torch.tensor([[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]])
        shifted = shift_labels(x)
        print(f"  - 输入形状: {x.shape}")
        print(f"  - 输出形状: {shifted.shape}")
        print(f"  - 输入: {x.tolist()}")
        print(f"  - 输出: {shifted.tolist()}")
        print(f"  - 验证: 输出应为输入右移一位 {'✓' if shifted.shape == (2, 4) else '✗'}")
    except Exception as e:
        print(f"✗ shift_labels 测试失败: {e}")
    
    # 测试3: gather_logprobs
    print("\n[测试3] gather_logprobs 函数")
    try:
        batch_size, seq_len, vocab_size = 2, 5, 10
        logits = torch.randn(batch_size, seq_len, vocab_size)
        labels = torch.randint(0, vocab_size, (batch_size, seq_len))
        logprobs = gather_logprobs(logits, labels)
        print(f"  - Logits形状: {logits.shape}")
        print(f"  - Labels形状: {labels.shape}")
        print(f"  - 输出形状: {logprobs.shape}")
        print(f"  - 输出范围: [{logprobs.min().item():.4f}, {logprobs.max().item():.4f}]")
        print(f"  - 平均值: {logprobs.mean().item():.4f}")
        print(f"  - 验证: 输出形状正确 {'✓' if logprobs.shape == (batch_size, seq_len) else '✗'}")
    except Exception as e:
        print(f"✗ gather_logprobs 测试失败: {e}")
    
    # 测试4: approx_kl
    print("\n[测试4] approx_kl 函数")
    try:
        policy_logp = torch.randn(2, 10) * 0.1 - 5.0  # 模拟对数概率
        ref_logp = torch.randn(2, 10) * 0.1 - 5.0
        kl = approx_kl(policy_logp, ref_logp)
        print(f"  - Policy logp形状: {policy_logp.shape}")
        print(f"  - Ref logp形状: {ref_logp.shape}")
        print(f"  - KL散度值: {kl.item():.6f}")
        print(f"  - Policy平均logp: {policy_logp.mean().item():.4f}")
        print(f"  - Ref平均logp: {ref_logp.mean().item():.4f}")
        print(f"  - 验证: KL = (policy - ref).mean() {'✓' if abs(kl.item() - (policy_logp - ref_logp).mean().item()) < 1e-6 else '✗'}")
    except Exception as e:
        print(f"✗ approx_kl 测试失败: {e}")
    
    # 测试5: sample_prompts
    print("\n[测试5] sample_prompts 函数")
    try:
        prompts = sample_prompts(3)
        print(f"  - 请求数量: 3")
        print(f"  - 实际返回数量: {len(prompts)}")
        print(f"  - 提示列表:")
        for i, p in enumerate(prompts, 1):
            preview = p[:50] + "..." if len(p) > 50 else p
            print(f"    {i}. {preview}")
        print(f"  - 验证: 返回数量正确 {'✓' if len(prompts) == 3 else '✗'}")
    except Exception as e:
        print(f"✗ sample_prompts 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)