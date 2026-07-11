"""
监督微调（SFT）数据整理器模块

该模块提供了 SFTCollator 类，用于将指令-响应对转换为适合因果语言模型训练的格式。
主要功能包括：
- 将文本编码为 token IDs
- 创建标签掩码（prompt 部分的标签设为 -100，不参与损失计算）
- 批处理数据并填充到固定长度
"""

from __future__ import annotations
from typing import List, Tuple
import torch
import traceback

# 复用 tokenizer：优先使用 Part 4 的 BPE tokenizer，否则使用 Part 3 的字节级 tokenizer
import sys
from pathlib import Path as _P

# 尝试从 Part 4 导入 BPE tokenizer
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_4'))
try:
    from tokenizer_bpe import BPETokenizer
    _HAS_BPE = True
except Exception:
    _HAS_BPE = False

# 尝试从 Part 3 导入字节级 tokenizer
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
try:
    from tokenizer import ByteTokenizer
except Exception:
    ByteTokenizer = None

from formatters import Example, format_example, format_prompt_only


class SFTCollator:
    """
    监督微调数据整理器
    
    将 (instruction, response) 对转换为因果语言模型训练所需的 token IDs 和掩码标签。
    在监督微调中，我们只计算 response 部分的损失，prompt 部分的标签被设置为 -100，
    这样在计算损失时这些位置会被忽略。
    
    Attributes:
        block_size (int): 序列的最大长度（块大小）
        tok: tokenizer 实例，用于文本编码
    """
    
    def __init__(self, block_size: int = 256, bpe_dir: str | None = None):
        """
        初始化 SFTCollator
        
        Args:
            block_size (int): 序列的最大长度，默认为 256
            bpe_dir (str | None): BPE tokenizer 的保存目录路径，如果提供则加载已训练的 tokenizer
        
        Raises:
            RuntimeError: 如果没有任何可用的 tokenizer
        """
        self.block_size = block_size
        self.tok = None
        
        # 优先尝试使用 BPE tokenizer（Part 4）
        if _HAS_BPE:
            try:
                self.tok = BPETokenizer(vocab_size=8000)
                # 如果提供了 BPE 目录，则加载已训练的 tokenizer
                if bpe_dir:
                    self.tok.load(bpe_dir)
                    print(f"Loaded BPE tokenizer from {bpe_dir}")
                else:
                    # 如果没有提供目录，使用默认的 BPE tokenizer
                    # 注意：这里假设 Part 4 的 tokenizer 已经存在
                    pass
            except Exception:
                # 如果 BPE tokenizer 初始化失败，打印错误并继续尝试其他 tokenizer
                print(traceback.format_exc())
                self.tok = None
        
        # 如果 BPE tokenizer 不可用，尝试使用字节级 tokenizer（Part 3）
        if self.tok is None and ByteTokenizer is not None:
            self.tok = ByteTokenizer()
        
        # 如果所有 tokenizer 都不可用，抛出错误
        if self.tok is None:
            raise RuntimeError("No tokenizer available. Install tokenizers or ensure Part 3 ByteTokenizer exists.")

    @property
    def vocab_size(self) -> int:
        """
        获取词汇表大小
        
        Returns:
            int: tokenizer 的词汇表大小，如果 tokenizer 没有 vocab_size 属性则返回 256（字节级）
        """
        return getattr(self.tok, 'vocab_size', 256)

    def encode(self, text: str) -> List[int]:
        """
        将文本编码为 token IDs
        
        Args:
            text (str): 要编码的文本
        
        Returns:
            List[int]: token IDs 列表
        
        Raises:
            RuntimeError: 如果 tokenizer 未正确初始化（如 BPE tokenizer 未训练/加载）
        """
        # 如果 tokenizer 有 encode 方法，使用它
        if hasattr(self.tok, 'encode'):
            # 检查 BPE tokenizer 是否已训练/加载
            if hasattr(self.tok, '_tok') and self.tok._tok is None:
                raise RuntimeError(
                    "BPE tokenizer 未训练或加载。请先调用 tokenizer.train() 或 "
                    "tokenizer.load()，或者在初始化 SFTCollator 时提供 bpe_dir 参数。"
                )
            try:
                ids = self.tok.encode(text)
                # 如果返回的是 torch.Tensor，转换为列表
                if isinstance(ids, torch.Tensor):
                    ids = ids.tolist()
                return ids
            except AttributeError as e:
                if "'NoneType' object has no attribute" in str(e):
                    raise RuntimeError(
                        "BPE tokenizer 未训练或加载。请先调用 tokenizer.train() 或 "
                        "tokenizer.load()，或者在初始化 SFTCollator 时提供 bpe_dir 参数。"
                    ) from e
                raise
        
        # 对于 ByteTokenizer 类型，直接使用 UTF-8 编码
        return list(text.encode('utf-8'))

    def collate(self, batch: List[Tuple[str, str]]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        批处理函数：将一批 (prompt, response) 对转换为模型输入格式
        
        该函数执行以下操作：
        1. 将 prompt 和 response 组合成完整文本
        2. 编码为 token IDs
        3. 创建标签：response 部分使用下一个 token 作为标签，prompt 部分设为 -100
        4. 填充到 block_size 长度
        5. 转换为 PyTorch 张量
        
        Args:
            batch (List[Tuple[str, str]]): 一批 (prompt, response) 对
        
        Returns:
            Tuple[torch.Tensor, torch.Tensor]: 
                - input_ids: 输入 token IDs，形状为 (batch_size, block_size)
                - labels: 标签，形状为 (batch_size, block_size)，prompt 部分为 -100
        """
        input_ids = []
        labels = []
        
        # 处理批次中的每个样本
        for prompt, response in batch:
            # 格式化 prompt（移除结束标记）
            prefix_text = format_prompt_only(prompt).replace('</s>', '')
            # 格式化完整的示例（prompt + response）
            text = format_example(Example(prompt, response))
            
            # 编码文本并截断到 block_size
            ids = self.encode(text)[:self.block_size]
            prompt_ids = self.encode(prefix_text)[:self.block_size]
            
            # 计算 prompt 部分的长度（取较小值以确保不越界）
            n_prompt = min(len(prompt_ids), len(ids))
            
            # 输入就是完整的 token IDs
            x = ids
            
            # 标签是下一个 token（用于因果语言模型的训练）
            # 即：给定前 t 个 token，预测第 t+1 个 token
            y = ids.copy()
            for t in range(len(y) - 1):
                y[t] = ids[t + 1]  # 当前位置的标签是下一个 token
            y[-1] = -100  # 最后一个位置没有下一个 token，设为 -100
            
            # 将 prompt 部分的标签设为 -100，这样在计算损失时会被忽略
            # 我们只计算 response 部分的损失
            for i in range(n_prompt - 1):
                y[i] = -100
            
            input_ids.append(x)
            labels.append(y)
        
        # 填充函数：将序列填充到 block_size 长度
        def pad_to(ids, val):
            """将序列填充到 block_size 长度，使用指定值填充"""
            if len(ids) < self.block_size:
                ids = ids + [val] * (self.block_size - len(ids))
            return ids[:self.block_size]
        
        # 将输入填充为 2（通常是 pad token），标签填充为 -100（忽略标记）
        x = torch.tensor([pad_to(s, 2) for s in input_ids], dtype=torch.long)
        y = torch.tensor([pad_to(s, -100) for s in labels], dtype=torch.long)
        
        return x, y


if __name__ == "__main__":
    print("=" * 70)
    print("SFTCollator 测试")
    print("=" * 70)
    
    # 创建 SFTCollator 实例
    print("\n1. 初始化 SFTCollator...")
    collator = None
    
    # 首先尝试使用 BPE tokenizer（如果可用）
    try:
        collator = SFTCollator(block_size=256)
        print(f"   [OK] SFTCollator 初始化成功")
        print(f"   - block_size: {collator.block_size}")
        print(f"   - vocab_size: {collator.vocab_size}")
        print(f"   - tokenizer 类型: {type(collator.tok).__name__}")
        
        # 检查 BPE tokenizer 是否已训练/加载
        if hasattr(collator.tok, '_tok') and collator.tok._tok is None:
            print(f"   [WARNING] BPE tokenizer 未训练或加载")
            print(f"   尝试回退到 ByteTokenizer...")
            # 强制使用 ByteTokenizer
            if ByteTokenizer is not None:
                collator.tok = ByteTokenizer()
                print(f"   [OK] 已切换到 ByteTokenizer")
                print(f"   - tokenizer 类型: {type(collator.tok).__name__}")
                print(f"   - vocab_size: {collator.vocab_size}")
            else:
                print(f"   [ERROR] ByteTokenizer 也不可用")
                raise RuntimeError("没有可用的 tokenizer")
    except Exception as e:
        print(f"   [ERROR] 初始化失败: {e}")
        print(traceback.format_exc())
        exit(1)
    
    # 测试 encode 方法
    print("\n2. 测试 encode 方法...")
    test_text = "Hello, world! 你好，世界！"
    try:
        encoded = collator.encode(test_text)
        print(f"   原始文本: {test_text}")
        print(f"   编码后 token IDs (前20个): {encoded[:20]}")
        print(f"   总 token 数: {len(encoded)}")
    except Exception as e:
        print(f"   [ERROR] encode 失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        if "BPETokenizer" in str(type(collator.tok).__name__):
            print(f"   提示: BPE tokenizer 需要先训练或加载才能使用。")
            print(f"   请使用 collator = SFTCollator(block_size=128, bpe_dir='path/to/tokenizer')")
            print(f"   或者回退到使用 ByteTokenizer")
        print(traceback.format_exc())
        exit(1)
    
    # 测试单个示例的格式化
    print("\n3. 测试单个示例格式化...")
    example = Example(
        instruction="请解释什么是机器学习",
        response="机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出预测。"
    )
    formatted_text = format_example(example)
    formatted_prompt = format_prompt_only(example.instruction)
    print(f"   完整格式化文本长度: {len(formatted_text)} 字符")
    print(f"   Prompt 格式化文本长度: {len(formatted_prompt)} 字符")
    
    # 编码示例
    try:
        full_ids = collator.encode(formatted_text)
        prompt_ids = collator.encode(formatted_prompt.replace('</s>', ''))
        print(f"   完整文本 token 数: {len(full_ids)}")
        print(f"   Prompt token 数: {len(prompt_ids)}")
        print(f"   Response token 数 (估算): {len(full_ids) - len(prompt_ids)}")
    except Exception as e:
        print(f"   [ERROR] 编码失败: {e}")
        raise
    
    # 测试 collate 方法
    print("\n4. 测试 collate 方法（批处理）...")
    batch = [
        ("请解释什么是机器学习", "机器学习是人工智能的一个分支。"),
        ("什么是深度学习？", "深度学习是机器学习的一个子领域，使用多层神经网络。"),
        ("请介绍一下自然语言处理", "自然语言处理是计算机科学和人工智能的一个分支。")
    ]
    
    print(f"   批次大小: {len(batch)}")
    print(f"   批次内容:")
    for i, (prompt, response) in enumerate(batch, 1):
        print(f"     样本 {i}: prompt={prompt[:30]}..., response={response[:30]}...")
    
    try:
        input_ids, labels = collator.collate(batch)
        print(f"\n   输出形状:")
        print(f"   - input_ids: {input_ids.shape}")
        print(f"   - labels: {labels.shape}")
    except Exception as e:
        print(f"   [ERROR] collate 失败: {e}")
        print(traceback.format_exc())
        exit(1)
    
    # 打印第一个样本的详细信息
    print("\n5. 第一个样本的详细信息...")
    sample_idx = 0
    sample_input = input_ids[sample_idx]
    sample_labels = labels[sample_idx]
    
    print(f"sample_input: {sample_input}")
    print(f"sample_labels: {sample_labels}")
    
    # 找到非填充的位置
    non_pad_mask = sample_input != 2
    non_ignore_mask = sample_labels != -100
    
    print(f"   非填充 token 数: {non_pad_mask.sum().item()}")
    print(f"   参与损失计算的 token 数: {non_ignore_mask.sum().item()}")
    print(f"   被忽略的 token 数 (prompt部分): {(~non_ignore_mask & non_pad_mask).sum().item()}")
    
    
    
    print(f"\n   前30个位置的 input_ids 和 labels:")
    print(f"   {'位置':<6} {'input_id':<10} {'label':<10} {'说明':<20}")
    print(f"   {'-'*50}")
    for i in range(min(30, len(sample_input))):
        input_id = sample_input[i].item()
        label = sample_labels[i].item()
        if input_id == 2:
            desc = "填充"
        elif label == -100:
            desc = "prompt(忽略)"
        else:
            desc = "response(计算)"
        print(f"   {i:<6} {input_id:<10} {label:<10} {desc:<20}")
    
    # 统计信息
    print("\n6. 批次统计信息...")
    total_tokens = (input_ids != 2).sum().item()
    total_labels = (labels != -100).sum().item()
    print(f"   批次总 token 数 (非填充): {total_tokens}")
    print(f"   批次总标签数 (参与损失计算): {total_labels}")
    print(f"   平均每个样本的 token 数: {total_tokens / len(batch):.2f}")
    print(f"   平均每个样本的标签数: {total_labels / len(batch):.2f}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)