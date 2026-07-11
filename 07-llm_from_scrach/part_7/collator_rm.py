"""
奖励模型（Reward Model）的数据整理器（Collator）模块

该模块用于处理偏好对（preference pairs）数据，将（提示、选中回复、拒绝回复）三元组
转换为可用于训练奖励模型的tokenized输入对（正样本、负样本）。
使用SFT模板格式化文本，确保与监督微调阶段的数据格式一致。
"""
from __future__ import annotations
from typing import List, Tuple
import torch

# 优先使用Part 4的BPE分词器，否则使用Part 3的字节级分词器
import sys
from pathlib import Path as _P
# 添加Part 4路径以导入BPE分词器
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_4'))
try:
    from tokenizer_bpe import BPETokenizer
    _HAS_BPE = True
except Exception:
    _HAS_BPE = False

# 添加Part 3路径以导入字节级分词器作为备选
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_3'))
try:
    from tokenizer import ByteTokenizer
except Exception:
    ByteTokenizer = None

# 添加Part 6路径以导入格式化工具（复用SFT阶段的格式化逻辑）
sys.path.append(str(_P(__file__).resolve().parents[1]/'part_6'))
try:
    from formatters import Example, format_example  # 复用格式化函数
except Exception:
    pass


class PairCollator:
    """偏好对数据整理器
    
    将偏好对（prompt, chosen, rejected）转换为tokenized的输入ID对（正样本、负样本）。
    使用SFT模板格式化文本，将'chosen'或'rejected'文本作为Response部分。
    
    用于奖励模型训练，通过对比学习的方式学习区分更好的回复和更差的回复。
    """
    
    def __init__(self, block_size: int = 256, bpe_dir: str | None = None, vocab_size: int | None = None):
        """
        初始化偏好对整理器
        
        Args:
            block_size: 序列的最大长度（token数量），默认256
            bpe_dir: BPE分词器的保存目录路径，如果提供则加载预训练的分词器
            vocab_size: 词汇表大小，仅在创建新BPE分词器时使用，默认8000
        """
        self.block_size = block_size  # 序列块大小
        self.tok = None  # 分词器实例
        
        # 优先尝试使用BPE分词器
        if _HAS_BPE:
            try:
                self.tok = BPETokenizer(vocab_size=vocab_size or 8000)
                if bpe_dir:
                    self.tok.load(bpe_dir)  # 如果提供了目录，加载预训练的分词器
            except Exception:
                self.tok = None
        
        # 如果BPE不可用，尝试使用字节级分词器作为备选
        if self.tok is None and ByteTokenizer is not None:
            self.tok = ByteTokenizer()
        
        # 如果所有分词器都不可用，抛出错误
        if self.tok is None:
            raise RuntimeError("No tokenizer available.")

    @property
    def vocab_size(self) -> int:
        """
        获取词汇表大小
        
        Returns:
            分词器的词汇表大小，如果分词器没有vocab_size属性则返回256（字节级分词器的默认值）
        """
        return getattr(self.tok, 'vocab_size', 256)

    def _encode(self, text: str) -> List[int]:
        """
        将文本编码为token ID列表
        
        Args:
            text: 待编码的文本字符串
            
        Returns:
            token ID列表
        """
        # 如果分词器有encode方法，使用它进行编码
        if hasattr(self.tok, 'encode'):
            # 检查 BPE tokenizer 是否已正确初始化
            if hasattr(self.tok, '_tok') and self.tok._tok is None:
                raise RuntimeError(
                    "BPE tokenizer 未初始化。需要先调用 train() 或 load() 方法，"
                    "或者使用 ByteTokenizer 作为备选方案。"
                )
            try:
                ids = self.tok.encode(text)
                # 如果返回的是torch.Tensor，转换为列表
                if isinstance(ids, torch.Tensor):
                    ids = ids.tolist()
                return ids
            except AttributeError as e:
                # 如果 encode 失败，可能是 tokenizer 未初始化
                raise RuntimeError(
                    f"分词器编码失败: {e}。"
                    "请确保 BPE tokenizer 已训练或加载，或使用 ByteTokenizer。"
                ) from e
        # 否则使用UTF-8字节编码（字节级分词器的备选方案）
        return list(text.encode('utf-8'))

    def collate(self, batch: List[Tuple[str, str, str]]):
        """
        整理批次数据，将偏好对转换为tokenized的张量对
        
        Args:
            batch: 批次数据，每个元素是三元组 (prompt, chosen, rejected)
                - prompt: 用户提示
                - chosen: 被选中的回复（更好的回复）
                - rejected: 被拒绝的回复（更差的回复）
        
        Returns:
            (pos, neg): 两个torch.Tensor，形状为 [batch_size, block_size]
                - pos: 正样本（chosen回复）的token ID张量
                - neg: 负样本（rejected回复）的token ID张量
        """
        pos_ids, neg_ids = [], []  # 存储正样本和负样本的token ID列表
        
        # 遍历批次中的每个偏好对
        for prompt, chosen, rejected in batch:
            # 使用SFT模板格式化正样本（prompt + chosen）
            pos_text = format_example(Example(prompt, chosen))
            # 使用SFT模板格式化负样本（prompt + rejected）
            neg_text = format_example(Example(prompt, rejected))
            
            # 编码并截断到block_size长度
            pos_ids.append(self._encode(pos_text)[:self.block_size])
            neg_ids.append(self._encode(neg_text)[:self.block_size])
        
        def pad_to(x, pad=2):
            """
            将序列填充或截断到block_size长度
            
            Args:
                x: token ID列表
                pad: 填充token ID，默认值为2
                
            Returns:
                填充或截断后的列表，长度为block_size
            """
            # 如果长度小于block_size，用pad填充；否则截断到block_size
            return x + [pad] * (self.block_size - len(x)) if len(x) < self.block_size else x[:self.block_size]
        
        # 将列表转换为张量，并进行填充/截断
        pos = torch.tensor([pad_to(x) for x in pos_ids], dtype=torch.long)
        neg = torch.tensor([pad_to(x) for x in neg_ids], dtype=torch.long)
        
        return pos, neg


if __name__ == "__main__":
    """测试代码：验证PairCollator的基本功能"""
    print("=" * 60)
    print("PairCollator 测试")
    print("=" * 60)
    
    # 创建测试数据
    test_batch = [
        ("什么是机器学习？", "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。", "机器学习就是编程。"),
        ("解释一下神经网络", "神经网络是模拟人脑神经元结构的计算模型，由多个层和节点组成。", "神经网络就是电脑。"),
    ]
    
    print("\n【1. 初始化PairCollator】")
    collator = None
    try:
        # 首先尝试使用 BPE tokenizer（如果可用）
        # 如果 BPE tokenizer 需要训练或加载，会回退到 ByteTokenizer
        collator = PairCollator(block_size=128)
        print(f"✓ 初始化成功")
        print(f"  - 分词器类型: {type(collator.tok).__name__}")
        print(f"  - 词汇表大小: {collator.vocab_size}")
        print(f"  - Block size: {collator.block_size}")
        
        # 检查 BPE tokenizer 是否已正确初始化
        if hasattr(collator.tok, '_tok') and collator.tok._tok is None:
            print(f"  ⚠ 警告: BPE tokenizer 的 _tok 为 None，需要先训练或加载")
            print(f"  尝试使用 ByteTokenizer 作为备选...")
            # 强制使用 ByteTokenizer
            if ByteTokenizer is not None:
                collator.tok = ByteTokenizer()
                print(f"  ✓ 已切换到 ByteTokenizer")
            else:
                raise RuntimeError("BPE tokenizer 未初始化且 ByteTokenizer 不可用")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        print(f"  提示: 如果使用 BPE tokenizer，需要先调用 train() 或 load() 方法")
        print(f"  或者确保 ByteTokenizer 可用作为备选方案")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n【2. 输入数据示例】")
    for i, (prompt, chosen, rejected) in enumerate(test_batch, 1):
        print(f"\n样本 {i}:")
        print(f"  Prompt: {prompt}")
        print(f"  Chosen: {chosen}")
        print(f"  Rejected: {rejected}")
    
    print("\n【3. 格式化后的文本示例】")
    try:
        if 'format_example' in globals() and 'Example' in globals():
            example = Example(test_batch[0][0], test_batch[0][1])
            formatted = format_example(example)
            print(f"  \n格式化后的正样本文本（前100字符）: {formatted[:100]}...")
            
            example_neg = Example(test_batch[0][0], test_batch[0][2])
            formatted_neg = format_example(example_neg)
            print(f"  格式化后的负样本文本（前100字符）: {formatted_neg[:100]}...")
        else:
            print("  注意: format_example 不可用，跳过格式化文本展示")
    except Exception as e:
        print(f"  格式化文本时出错: {e}")
    
    print("\n【4. 检查分词器状态】")
    # 检查 tokenizer 是否可以正常编码
    try:
        test_text = "测试文本"
        test_ids = collator._encode(test_text)
        print(f"✓ 分词器编码测试成功")
        print(f"  - 测试文本: '{test_text}'")
        print(f"  - 编码结果: {test_ids[:10]}... (前10个token IDs)")
        print(f"  - Token数量: {len(test_ids)}")
    except Exception as e:
        print(f"✗ 分词器编码测试失败: {e}")
        print(f"  错误详情:")
        import traceback
        traceback.print_exc()
        print(f"\n  解决方案:")
        if hasattr(collator.tok, '_tok') and collator.tok._tok is None:
            print(f"  - BPE tokenizer 需要先训练或加载")
            print(f"  - 可以调用: collator.tok.train(data_path) 或 collator.tok.load(bpe_dir)")
        print(f"  - 或者使用 ByteTokenizer: collator = PairCollator(block_size=128)")
        exit(1)
    
    print("\n【5. 执行collate操作】")
    try:
        pos_tensor, neg_tensor = collator.collate(test_batch)
        print(f"✓ Collate操作成功")
        print(f"  - 正样本张量形状: {pos_tensor.shape}")
        print(f"  - 负样本张量形状: {neg_tensor.shape}")
        print(f"  - 批次大小: {pos_tensor.shape[0]}")
        print(f"  - 序列长度: {pos_tensor.shape[1]}")
    except Exception as e:
        print(f"✗ Collate操作失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n【6. Token ID示例】")
    print(f"  正样本第一个序列的前20个token IDs:")
    print(f"    {pos_tensor[0, :20].tolist()}")
    print(f"  负样本第一个序列的前20个token IDs:")
    print(f"    {neg_tensor[0, :20].tolist()}")
    
    print("\n【7. 数据统计信息】")
    print(f"  - 正样本非填充token数量（第一个样本）: {(pos_tensor[0] != 2).sum().item()}")
    print(f"  - 负样本非填充token数量（第一个样本）: {(neg_tensor[0] != 2).sum().item()}")
    print(f"  - 正样本唯一token数量（第一个样本）: {len(torch.unique(pos_tensor[0]))}")
    print(f"  - 负样本唯一token数量（第一个样本）: {len(torch.unique(neg_tensor[0]))}")
    print(f"  - 正样本: {pos_tensor[0]}")
    print(f"  - 负样本: {neg_tensor[0]}")
    
    print("\n【8. 张量数据类型和设备】")
    print(f"  - 数据类型: {pos_tensor.dtype}")
    print(f"  - 设备: {pos_tensor.device}")
    print(f"  - 最小值: {pos_tensor.min().item()}, 最大值: {pos_tensor.max().item()}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)