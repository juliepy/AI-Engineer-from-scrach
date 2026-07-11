"""
现代 GPT 模型实现
支持多种现代 Transformer 技术，包括 RMSNorm、SwiGLU、RoPE 等
"""
from __future__ import annotations
import torch
import torch.nn as nn
from block_modern import TransformerBlockModern
from tokenizer import ByteTokenizer

# 获取包含 part_2 和 part_3 的父目录的绝对路径
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

class GPTModern(nn.Module):
    """
    现代 GPT 模型类
    
    实现了基于 Transformer 架构的语言模型，支持多种现代优化技术：
    - RMSNorm 归一化
    - SwiGLU 激活函数
    - RoPE 位置编码
    - KV Cache 缓存机制
    - 滑动窗口注意力
    - 注意力下沉（Attention Sink）
    - 分组查询注意力（GQA）
    """
    def __init__(self, vocab_size: int = 256, block_size: int = 256,
                 n_layer: int=4, n_head: int=4, n_embd: int=256, dropout: float=0.0,
                 use_rmsnorm: bool = True, use_swiglu: bool = True, rope: bool = True,
                 max_pos: int = 4096, sliding_window: int | None = None, attention_sink: int = 0, n_kv_head: int | None = None):
        """
        初始化 GPT 模型
        
        Args:
            vocab_size: 词汇表大小，默认为 256（字节级 tokenizer）
            block_size: 最大序列长度（上下文窗口大小）
            n_layer: Transformer 层数
            n_head: 注意力头数
            n_embd: 嵌入维度
            dropout: Dropout 比率
            use_rmsnorm: 是否使用 RMSNorm（否则使用 LayerNorm）
            use_swiglu: 是否使用 SwiGLU 激活函数（否则使用 ReLU）
            rope: 是否使用 RoPE 位置编码（否则不使用位置编码）
            max_pos: 最大位置编码长度（用于 RoPE）
            sliding_window: 滑动窗口大小，None 表示使用全局注意力
            attention_sink: 注意力下沉的 token 数量（用于流式推理）
            n_kv_head: KV 头的数量，None 表示与 n_head 相同（用于分组查询注意力 GQA）
        """
        super().__init__()
        self.block_size = block_size  # 保存块大小供后续使用
        
        # Token 嵌入层：将 token ID 转换为向量表示
        self.tok_emb = nn.Embedding(vocab_size, n_embd)
        # 位置嵌入层（已注释，因为使用 RoPE 位置编码）
        # self.pos_emb = nn.Embedding(block_size, n_embd)
        
        # Dropout 层：防止过拟合
        self.drop = nn.Dropout(dropout)
        
        # Transformer 块列表：堆叠多个 Transformer 层
        self.blocks = nn.ModuleList([
            TransformerBlockModern(n_embd, n_head, dropout, use_rmsnorm, use_swiglu, rope, max_pos, sliding_window, attention_sink, n_kv_head)
            for _ in range(n_layer)
        ])
        
        # 最终归一化层：如果使用 RMSNorm，则在前面的块中已经处理，这里使用 Identity
        self.ln_f = nn.Identity() if use_rmsnorm else nn.LayerNorm(n_embd)
        
        # 输出头：将隐藏状态映射到词汇表大小的 logits
        self.head = nn.Linear(n_embd, vocab_size, bias=False)

    def forward(self, idx: torch.Tensor, targets: torch.Tensor | None = None, kv_cache_list=None, start_pos: int = 0):
        """
        前向传播
        
        Args:
            idx: 输入 token ID 张量，形状为 (batch_size, seq_len)
            targets: 目标 token ID 张量，用于计算损失，形状为 (batch_size, seq_len)
            kv_cache_list: KV Cache 列表，用于增量生成，每个元素对应一个 Transformer 块的缓存
            start_pos: 当前序列的起始位置（用于 RoPE 位置编码）
        
        Returns:
            logits: 输出 logits，形状为 (batch_size, seq_len, vocab_size)
            loss: 交叉熵损失（如果提供了 targets），否则为 None
            new_caches: 更新后的 KV Cache 列表
        """
        B, T = idx.shape  # B: batch_size, T: sequence_length
        assert T <= self.block_size, f"序列长度 {T} 超过了 block_size {self.block_size}"
        
        # 生成位置索引（虽然不使用位置嵌入，但保留以备后用）
        pos = torch.arange(0, T, device=idx.device).unsqueeze(0)
        
        # Token 嵌入：将 token ID 转换为向量
        x = self.tok_emb(idx) 
        # 位置嵌入（已注释，因为使用 RoPE）
        # + self.pos_emb(pos)
        
        # 应用 Dropout
        x = self.drop(x)

        # 遍历所有 Transformer 块，更新 KV Cache
        new_caches = []
        for i, blk in enumerate(self.blocks):
            # 获取当前块的 KV Cache（如果存在）
            cache = None if kv_cache_list is None else kv_cache_list[i]
            # 前向传播，返回更新后的隐藏状态和缓存
            x, cache = blk(x, kv_cache=cache, start_pos=start_pos)
            new_caches.append(cache)
        
        # 最终归一化
        x = self.ln_f(x)
        
        # 输出层：将隐藏状态映射到词汇表
        logits = self.head(x)

        # 计算损失（如果提供了目标）
        loss = None
        if targets is not None:
            import torch.nn.functional as F
            # 将 logits 和 targets 展平后计算交叉熵损失
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        
        return logits, loss, new_caches

    @torch.no_grad()
    def generate(self, 
                 prompt: torch.Tensor, 
                 max_new_tokens=200, 
                 temperature=1.0, 
                 top_k=50, 
                 top_p=None,
                 eos_id=1,  # 结束符 ID，用于提前停止生成
                 sliding_window: int | None = None, 
                 attention_sink: int = 0):
        """
        使用 KV Cache 进行文本生成（高效版本）
        
        使用 KV Cache 机制，在生成过程中只处理新 token，大幅提升生成速度。
        
        Args:
            prompt: 输入提示词，形状为 (batch_size, prompt_len)
            max_new_tokens: 最大生成 token 数量
            temperature: 温度参数，控制生成的随机性（0.0 表示贪婪解码）
            top_k: Top-K 采样，只考虑概率最高的 k 个 token
            top_p: Top-P（核采样），只考虑累积概率达到 p 的 token
            eos_id: 结束符 ID，生成到该 token 时提前停止
            sliding_window: 滑动窗口大小（已弃用，保留以兼容接口）
            attention_sink: 注意力下沉 token 数量（已弃用，保留以兼容接口）
        
        Returns:
            生成的完整序列，包括原始 prompt 和新生成的 token
        """
        # 尝试导入 top_k_top_p_filtering 工具函数
        try:
            from utils import top_k_top_p_filtering as _tk
        except Exception:
            # 如果导入失败，使用恒等函数（不进行过滤）
            _tk = lambda x, **_: x
        
        # print("generate start")
        # 设置为评估模式
        self.eval()
        idx = prompt  # 当前生成的序列
        #  print(f"idx: {idx.shape}")
        # print(f"idx: {idx}")
        kvs = [None] * len(self.blocks)  # 为每个 Transformer 块初始化 KV Cache
        # print(f"kvs: {kvs}")
        # print(f"len(self.blocks): {len(self.blocks)}")
        i = 0
        # 生成循环
        for _ in range(max_new_tokens):
            # 第一次迭代：处理完整 prompt；后续迭代：只处理最后一个 token（利用 KV Cache）
            idx_cond = idx[:, -self.block_size:] if kvs[0] is None else idx[:, -1:]
            # if i < 5:
            #     print(f"idx_cond: {idx_cond.shape}")

            # 计算绝对起始位置：首次为 0，后续从缓存长度获取
            start_pos = 0 if kvs[0] is None else kvs[0].k.size(2)
            # if i < 5:
            #     print(f"start_pos: {start_pos}")

            # 前向传播，更新 KV Cache
            logits, _, kvs = self(idx_cond, kv_cache_list=kvs, start_pos=start_pos)
            # if i < 5:
            #     print(f"logits: {logits.shape}")
            #     print(f"kvs: {kvs}")

            # 获取最后一个位置的 logits 并应用温度缩放
            next_logits = logits[:, -1, :] / max(temperature, 1e-6)
            # 应用 Top-K 和 Top-P 过滤
            next_logits = _tk(next_logits, top_k=top_k, top_p=top_p)
            # 计算概率分布
            probs = torch.softmax(next_logits, dim=-1)
            # if i < 5:
            #     print(f"probs: {probs.shape}")
            #     # 采样下一个 token：temperature=0 时使用贪婪解码，否则使用多项式采样
            #     print(f"temperature: {temperature}")
            next_id = torch.argmax(probs, dim=-1, keepdim=True) if temperature == 0.0 else torch.multinomial(probs, 1)
            # if i < 5:
            #     print(f"next_id: {next_id.shape}")
            # 将新 token 添加到序列中
            idx = torch.cat([idx, next_id], dim=1)
            # if i < 5:
            #     print(f"idx: {idx.shape}")
            # 提前停止：如果生成结束符，则停止生成
            if eos_id is not None:
                if (next_id == eos_id).all():
                    break
        
        # print(f"idx: {idx}")
        # print(f"idx shape: {idx.shape}")
        # print("generate exit")

        return idx


    @torch.no_grad()
    def generate_nocache(self, prompt: torch.Tensor, max_new_tokens=200, temperature=1.0, top_k=50, top_p=None,
                sliding_window: int | None = None, attention_sink: int = 0):
        """
        不使用 KV Cache 进行文本生成（调试版本）
        
        每次生成都重新计算整个窗口，不使用缓存机制。速度较慢但便于调试，
        会打印每个步骤的 top-10 候选 token 及其概率。
        
        Args:
            prompt: 输入提示词，形状为 (batch_size, prompt_len)
            max_new_tokens: 最大生成 token 数量
            temperature: 温度参数，控制生成的随机性（0.0 表示贪婪解码）
            top_k: Top-K 采样，只考虑概率最高的 k 个 token
            top_p: Top-P（核采样），只考虑累积概率达到 p 的 token
            sliding_window: 滑动窗口大小（已弃用，保留以兼容接口）
            attention_sink: 注意力下沉 token 数量（已弃用，保留以兼容接口）
        
        Returns:
            生成的完整序列，包括原始 prompt 和新生成的 token
        """
        # 尝试导入 top_k_top_p_filtering 工具函数
        try:
            from utils import top_k_top_p_filtering as _tk
        except Exception:
            # 如果导入失败，使用恒等函数（不进行过滤）
            _tk = lambda x, **_: x

        # 设置为评估模式
        self.eval()
        idx = prompt  # 当前生成的序列

        # 生成循环
        for _ in range(max_new_tokens):
            # 每次都对裁剪后的窗口进行完整前向传播，不使用缓存
            idx_cond = idx[:, -self.block_size:]
            # 计算窗口内第一个 token 的绝对位置（与使用缓存的方式保持一致）
            start_pos = idx.size(1) - idx_cond.size(1)

            # 前向传播，不使用 KV Cache
            logits, _, _ = self(idx_cond, kv_cache_list=None, start_pos=start_pos)

            # 获取最后一个位置的 logits 并应用温度缩放
            next_logits = logits[:, -1, :] / max(temperature, 1e-6)
            # 应用 Top-K 和 Top-P 过滤
            next_logits = _tk(next_logits, top_k=top_k, top_p=top_p)
            # 计算概率分布
            probs = torch.softmax(next_logits, dim=-1)
            
            # 获取 top-10 候选 token 用于调试
            topv, topi = torch.topk(probs, 10)
            print("top ids:", topi.tolist())
            print("top vs:", topv.tolist())
            
            # 采样下一个 token：temperature=0 时使用贪婪解码，否则使用多项式采样
            next_id = torch.argmax(probs, dim=-1, keepdim=True) if temperature == 0.0 else torch.multinomial(probs, 1)
            # 将新 token 添加到序列中
            idx = torch.cat([idx, next_id], dim=1)

        return idx

