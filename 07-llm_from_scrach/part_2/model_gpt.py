"""
GPT 模型实现
包含因果自注意力机制、前馈网络、Transformer Block 和完整的 GPT 模型
"""
from __future__ import annotations
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# ---- Blocks (self-contained for isolation) ----

class CausalSelfAttention(nn.Module):
    """
    因果自注意力机制（Causal Self-Attention）
    实现带掩码的自注意力，确保每个位置只能看到之前的位置（用于生成任务）
    """
    def __init__(self, n_embd: int, n_head: int, dropout: float = 0.0):
        """
        初始化因果自注意力层
        
        Args:
            n_embd: 嵌入维度（embedding dimension）
            n_head: 注意力头数（number of attention heads）
            dropout: Dropout 概率
        """
        super().__init__()
        assert n_embd % n_head == 0  # 确保嵌入维度能被头数整除
        self.n_head = n_head  # 注意力头数
        self.d_head = n_embd // n_head  # 每个头的维度
        # 将输入投影为 Q、K、V 三个矩阵（合并计算以提高效率）
        self.qkv = nn.Linear(n_embd, 3 * n_embd, bias=False)
        # 输出投影层
        self.proj = nn.Linear(n_embd, n_embd, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor):  # (B,T,C)
        """
        前向传播
        
        Args:
            x: 输入张量，形状为 (B, T, C)
                B: batch size（批次大小）
                T: sequence length（序列长度）
                C: embedding dimension（嵌入维度）
        
        Returns:
            输出张量，形状为 (B, T, C)
        """
        B, T, C = x.shape
        # 计算 Q、K、V：将输入投影并重塑为多头形式
        qkv = self.qkv(x).view(B, T, 3, self.n_head, self.d_head)
        q, k, v = qkv.unbind(dim=2)  # 分离 Q、K、V
        # 转置为 (B, n_head, T, d_head) 以便进行注意力计算
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        scale = 1.0 / math.sqrt(self.d_head)  # 缩放因子（虽然 SDPA 内部已处理）
        # 使用 PyTorch 的缩放点积注意力（自动使用 Flash Attention 如果可用）
        # is_causal=True 确保因果掩码（只能看到之前的位置）
        y = F.scaled_dot_product_attention(q, k, v, attn_mask=None, dropout_p=self.dropout.p if self.training else 0.0, is_causal=True)
        # 重塑回原始形状 (B, T, C)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        y = self.proj(y)  # 输出投影
        return y

class FeedForward(nn.Module):
    """
    前馈神经网络（Feed-Forward Network）
    标准的 Transformer 前馈层：线性 -> 激活 -> 线性
    """
    def __init__(self, n_embd: int, mult: int = 4, dropout: float = 0.0):
        """
        初始化前馈网络
        
        Args:
            n_embd: 嵌入维度
            mult: 中间层维度倍数（默认 4 倍）
            dropout: Dropout 概率
        """
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, mult * n_embd),  # 扩展维度
            nn.GELU(),  # GELU 激活函数
            nn.Linear(mult * n_embd, n_embd),  # 压缩回原始维度
            nn.Dropout(dropout),
        )

    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入张量，形状为 (B, T, C)
        
        Returns:
            输出张量，形状为 (B, T, C)
        """
        return self.net(x)

class Block(nn.Module):
    """
    Transformer Block（Transformer 块）
    包含一个自注意力层和一个前馈网络，使用残差连接和层归一化
    """
    def __init__(self, n_embd: int, n_head: int, dropout: float):
        """
        初始化 Transformer Block
        
        Args:
            n_embd: 嵌入维度
            n_head: 注意力头数
            dropout: Dropout 概率
        """
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)  # 第一个层归一化（注意力前）
        self.attn = CausalSelfAttention(n_embd, n_head, dropout)
        self.ln2 = nn.LayerNorm(n_embd)  # 第二个层归一化（前馈网络前）
        self.ffn = FeedForward(n_embd, mult=4, dropout=dropout)

    def forward(self, x):
        """
        前向传播（使用残差连接）
        
        Args:
            x: 输入张量，形状为 (B, T, C)
        
        Returns:
            输出张量，形状为 (B, T, C)
        """
        # 残差连接 + 自注意力（Pre-LN 架构）
        x = x + self.attn(self.ln1(x))
        # 残差连接 + 前馈网络
        x = x + self.ffn(self.ln2(x))
        return x

# ---- Tiny GPT ----

class GPT(nn.Module):
    """
    GPT 模型（Generative Pre-trained Transformer）
    一个简化版的 GPT 模型，用于文本生成任务
    """
    def __init__(self, vocab_size: int, block_size: int, n_layer: int = 4, n_head: int = 4, n_embd: int = 256, dropout: float = 0.0):
        """
        初始化 GPT 模型
        
        Args:
            vocab_size: 词汇表大小
            block_size: 最大序列长度（上下文窗口大小）
            n_layer: Transformer 层数（默认 4）
            n_head: 注意力头数（默认 4）
            n_embd: 嵌入维度（默认 256）
            dropout: Dropout 概率
        """
        super().__init__()
        self.block_size = block_size
        # 词嵌入层：将 token ID 转换为向量
        self.tok_emb = nn.Embedding(vocab_size, n_embd)
        # 位置嵌入层：为每个位置添加位置信息
        self.pos_emb = nn.Embedding(block_size, n_embd)
        self.drop = nn.Dropout(dropout)
        # 堆叠多个 Transformer Block
        self.blocks = nn.ModuleList([Block(n_embd, n_head, dropout) for _ in range(n_layer)])
        # 最终层归一化
        self.ln_f = nn.LayerNorm(n_embd)
        # 输出头：将嵌入向量映射回词汇表大小
        self.head = nn.Linear(n_embd, vocab_size, bias=False)

        # 初始化权重
        self.apply(self._init_weights)

    def _init_weights(self, m):
        """
        权重初始化函数
        对线性层和嵌入层使用正态分布初始化
        
        Args:
            m: 模块对象
        """
        if isinstance(m, nn.Linear):
            # 线性层：使用均值为 0、标准差为 0.02 的正态分布
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            # 嵌入层：使用均值为 0、标准差为 0.02 的正态分布
            nn.init.normal_(m.weight, mean=0.0, std=0.02)

    def forward(self, idx: torch.Tensor, targets: torch.Tensor | None = None):
        """
        前向传播
        
        Args:
            idx: 输入 token ID 序列，形状为 (B, T)
            targets: 目标 token ID 序列（用于训练），形状为 (B, T)，可选
        
        Returns:
            logits: 输出 logits，形状为 (B, T, vocab_size)
            loss: 交叉熵损失（如果提供了 targets），否则为 None
        """
        B, T = idx.shape
        assert T <= self.block_size  # 确保序列长度不超过最大长度
        # 生成位置索引
        pos = torch.arange(0, T, device=idx.device).unsqueeze(0)
        # 词嵌入 + 位置嵌入
        x = self.tok_emb(idx) + self.pos_emb(pos)
        x = self.drop(x)
        # 通过所有 Transformer Block
        for blk in self.blocks:
            x = blk(x)
        x = self.ln_f(x)  # 最终层归一化
        logits = self.head(x)  # 输出 logits
        loss = None
        if targets is not None:
            # 计算交叉熵损失
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int = 200, temperature: float = 1.0,
                top_k: int | None = 50, top_p: float | None = None):
        """
        生成文本（自回归生成）
        
        Args:
            idx: 初始 token ID 序列（prompt），形状为 (B, T)
            max_new_tokens: 最大生成 token 数（默认 200）
            temperature: 温度参数，控制生成的随机性（>1 更随机，<1 更确定）
            top_k: Top-K 采样参数，只从概率最高的 k 个 token 中采样（默认 50）
            top_p: Top-P（核采样）参数，从累积概率达到 p 的 token 中采样（可选）
        
        Returns:
            生成的完整序列（包含原始 prompt），形状为 (B, T + max_new_tokens)
        """
        from utils import top_k_top_p_filtering
        self.eval()  # 设置为评估模式
        # 保护：如果 prompt 为空，使用换行符（ASCII 10）作为起始
        if idx.size(1) == 0:
            idx = torch.full((idx.size(0), 1), 10, dtype=torch.long, device=idx.device)
        # 自回归生成循环
        for _ in range(max_new_tokens):
            # 只使用最后 block_size 个 token（滑动窗口）
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)  # 前向传播
            # 只取最后一个位置的 logits，并应用温度缩放
            logits = logits[:, -1, :] / max(temperature, 1e-6)
            # Top-K 和 Top-P 过滤
            logits = top_k_top_p_filtering(logits, top_k=top_k, top_p=top_p)
            # 转换为概率分布
            probs = torch.softmax(logits, dim=-1)
            # 从概率分布中采样下一个 token
            next_id = torch.multinomial(probs, num_samples=1)
            # 将新生成的 token 追加到序列中
            idx = torch.cat([idx, next_id], dim=1)
        return idx


# ---- 测试代码 ----

if __name__ == "__main__":
    print("=" * 60)
    print("开始测试 GPT 模型组件...")
    print("=" * 60)
    
    # 设置随机种子以便结果可复现
    torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}\n")
    
    # 测试参数
    batch_size = 2
    seq_len = 10
    vocab_size = 1000
    block_size = 32
    n_embd = 128
    n_head = 4
    n_layer = 2
    
    # 创建随机输入
    idx = torch.randint(0, vocab_size, (batch_size, seq_len), device=device)
    targets = torch.randint(0, vocab_size, (batch_size, seq_len), device=device)
    
    print("1. 测试 CausalSelfAttention...")
    try:
        attn = CausalSelfAttention(n_embd, n_head, dropout=0.1).to(device)
        x = torch.randn(batch_size, seq_len, n_embd, device=device)
        y = attn(x)
        assert y.shape == (batch_size, seq_len, n_embd), f"注意力输出形状错误: {y.shape}"
        print(f"   ✓ 通过！输出形状: {y.shape}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
    
    print("\n2. 测试 FeedForward...")
    try:
        ffn = FeedForward(n_embd, mult=4, dropout=0.1).to(device)
        x = torch.randn(batch_size, seq_len, n_embd, device=device)
        y = ffn(x)
        assert y.shape == (batch_size, seq_len, n_embd), f"前馈网络输出形状错误: {y.shape}"
        print(f"   ✓ 通过！输出形状: {y.shape}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
    
    print("\n3. 测试 Block...")
    try:
        block = Block(n_embd, n_head, dropout=0.1).to(device)
        x = torch.randn(batch_size, seq_len, n_embd, device=device)
        y = block(x)
        assert y.shape == (batch_size, seq_len, n_embd), f"Block 输出形状错误: {y.shape}"
        print(f"   ✓ 通过！输出形状: {y.shape}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
    
    print("\n4. 测试 GPT 模型初始化...")
    try:
        model = GPT(
            vocab_size=vocab_size,
            block_size=block_size,
            n_layer=n_layer,
            n_head=n_head,
            n_embd=n_embd,
            dropout=0.1
        ).to(device)
        # 计算参数量
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"   ✓ 通过！模型创建成功")
        print(f"   总参数量: {total_params:,}")
        print(f"   可训练参数量: {trainable_params:,}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        model = None
    
    if model is not None:
        print("\n5. 测试 GPT 前向传播（无目标）...")
        try:
            model.eval()
            logits, loss = model(idx)
            assert logits.shape == (batch_size, seq_len, vocab_size), f"Logits 形状错误: {logits.shape}"
            assert loss is None, "无目标时不应有损失"
            print(f"   ✓ 通过！Logits 形状: {logits.shape}, Loss: {loss}")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n6. 测试 GPT 前向传播（有目标）...")
        try:
            model.train()
            logits, loss = model(idx, targets=targets)
            assert logits.shape == (batch_size, seq_len, vocab_size), f"Logits 形状错误: {logits.shape}"
            assert loss is not None and loss.item() > 0, f"损失值异常: {loss}"
            print(f"   ✓ 通过！Logits 形状: {logits.shape}, Loss: {loss.item():.4f}")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
        
        print("\n7. 测试 GPT 生成功能...")
        try:
            # 创建简单的 prompt
            prompt = torch.randint(0, vocab_size, (1, 5), device=device)
            print(f"   Prompt 形状: {prompt.shape}")
            
            # 生成（使用较小的 max_new_tokens 以加快测试）
            generated = model.generate(
                prompt,
                max_new_tokens=10,
                temperature=1.0,
                top_k=10
            )
            assert generated.shape[0] == prompt.shape[0], "批次大小不匹配"
            assert generated.shape[1] == prompt.shape[1] + 10, f"生成序列长度错误: {generated.shape[1]}"
            print(f"   ✓ 通过！生成序列形状: {generated.shape}")
            print(f"   原始 prompt: {prompt[0].tolist()}")
            print(f"   生成序列: {generated[0].tolist()}")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n8. 测试反向传播...")
        try:
            model.train()
            logits, loss = model(idx, targets=targets)
            loss.backward()
            # 检查梯度是否存在
            has_grad = any(p.grad is not None for p in model.parameters() if p.requires_grad)
            assert has_grad, "没有计算梯度"
            print(f"   ✓ 通过！反向传播成功，梯度已计算")
        except Exception as e:
            print(f"   ✗ 失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
