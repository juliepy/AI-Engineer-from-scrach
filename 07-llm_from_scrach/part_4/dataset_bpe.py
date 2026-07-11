"""
BPE 分词器数据集模块
===================

本模块提供了用于语言模型训练的数据集类，使用 BPE tokenizer 将文本转换为 token IDs，
并创建滑动窗口的数据块用于自回归语言模型训练。

主要功能：
- TextBPEBuffer: 将文本文件一次性编码为 token IDs，然后通过滑动窗口创建训练样本
- make_loader: 便捷函数，用于创建 PyTorch DataLoader
"""

from __future__ import annotations
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import Tuple
from tokenizer_bpe import BPETokenizer

class TextBPEBuffer(Dataset):
    """基于 BPE tokenizer 的文本数据集类。
    
    该类实现了类似内存映射的单文件数据集：
    - 一次性将整个文本文件编码为 token IDs（长张量）
    - 通过滑动窗口方式创建训练样本
    - 每个样本返回 (x, y) 对，其中 y 是 x 向右偏移一个位置的序列
    
    这种设计适用于自回归语言模型（如 GPT）的训练，模型需要根据前文预测下一个 token。
    
    示例：
        tokenizer = BPETokenizer()
        tokenizer.load("path/to/tokenizer")
        dataset = TextBPEBuffer("data.txt", tokenizer, block_size=256)
        x, y = dataset[0]  # x 是前 256 个 tokens，y 是后 256 个 tokens（错位 1 位）
    """
    
    def __init__(self, path: str, tokenizer: BPETokenizer, block_size: int = 256):
        """初始化数据集。
        
        Args:
            path: 文本文件路径
            tokenizer: BPE 分词器实例，用于将文本编码为 token IDs
            block_size: 每个训练样本的长度（context window 大小），默认为 256
        """
        super().__init__()
        self.block_size = block_size
        # 读取文本文件（使用 UTF-8 编码）
        text = Path(path).read_text(encoding='utf-8')
        # 使用 tokenizer 将整个文本编码为 token IDs，并转换为 PyTorch 长整型张量
        self.ids = torch.tensor(tokenizer.encode(text), dtype=torch.long)
    
    def __len__(self):
        """返回数据集的样本数量。
        
        数据集大小 = 总 token 数 - block_size - 1
        减 1 是因为需要为 y 序列预留一个额外的 token（y 比 x 偏移 1 位）
        
        Returns:
            数据集中可用的样本数量
        """
        return max(0, self.ids.numel() - self.block_size - 1)
    
    def __getitem__(self, i: int):
        """获取第 i 个训练样本。
        
        返回 (x, y) 对，其中：
        - x: 从位置 i 开始的 block_size 个 tokens（输入序列）
        - y: 从位置 i+1 开始的 block_size 个 tokens（目标序列，用于预测）
        
        这种设计使得模型在位置 t 预测 token[t+1]，符合自回归语言模型的训练方式。
        
        Args:
            i: 样本索引
            
        Returns:
            (x, y) 元组，都是长度为 block_size 的 1D 张量
        """
        # 输入序列：从位置 i 开始的 block_size 个 tokens
        x = self.ids[i:i+self.block_size]
        # 目标序列：从位置 i+1 开始的 block_size 个 tokens（比 x 偏移 1 位）
        y = self.ids[i+1:i+self.block_size+1]
        return x, y

def make_loader(path: str, tokenizer: BPETokenizer, block_size: int, batch_size: int, shuffle=True) -> DataLoader:
    """创建用于训练的数据加载器（DataLoader）。
    
    这是一个便捷函数，用于快速创建配置好的 DataLoader。
    
    Args:
        path: 文本文件路径
        tokenizer: BPE 分词器实例
        block_size: 每个样本的长度（context window 大小）
        batch_size: 批次大小
        shuffle: 是否在每个 epoch 开始时打乱数据，默认为 True
        
    Returns:
        配置好的 PyTorch DataLoader 实例
        
    注意：
        - drop_last=True 表示如果最后一个批次不完整则丢弃，确保所有批次大小一致
        - 这对于某些模型（如需要固定批次大小的模型）很重要
    """
    # 创建数据集实例
    ds = TextBPEBuffer(path, tokenizer, block_size)
    # 创建并返回 DataLoader，drop_last=True 确保所有批次大小一致
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=True)


if __name__ == "__main__":
    # 测试代码
    import tempfile
    import shutil
    
    print("=" * 60)
    print("BPE 数据集测试")
    print("=" * 60)
    
    # 创建临时目录用于测试
    current_path = Path(__file__).parent
    tmp_dir = current_path / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    test_data_file = tmp_dir / "test_dataset.txt"
    tokenizer_dir = tmp_dir / "test_tokenizer"
    
    try:
        # 1. 创建测试数据文件
        print("\n1. 创建测试数据文件...")
        test_text = """The quick brown fox jumps over the lazy dog.
Machine learning is a subset of artificial intelligence.
Natural language processing enables computers to understand human language.
Deep learning models can learn complex patterns from data.
Transformers have revolutionized the field of NLP."""
        test_data_file.write_text(test_text, encoding='utf-8')
        print(f"   测试数据已保存到: {test_data_file}")
        print(f"   文本长度: {len(test_text)} 字符")
        
        # 2. 训练或加载 tokenizer
        print("\n2. 准备 tokenizer...")
        tokenizer = BPETokenizer(vocab_size=500, special_tokens=["<s>", "</s>", "<pad>", "<unk>"])
        
        # 检查是否已有训练好的 tokenizer
        if tokenizer_dir.exists() and (tokenizer_dir / "tokenizer.json").exists():
            print("   加载已存在的 tokenizer...")
            tokenizer.load(tokenizer_dir)
        else:
            print("   训练新的 tokenizer...")
            tokenizer.train(test_data_file)
            tokenizer.save(tokenizer_dir)
            print(f"   Tokenizer 已保存到: {tokenizer_dir}")
        
        # 3. 测试数据集基本功能
        print("\n3. 测试 TextBPEBuffer 数据集...")
        block_size = 32
        dataset = TextBPEBuffer(str(test_data_file), tokenizer, block_size=block_size)
        print(f"   数据集大小: {len(dataset)} 个样本")
        print(f"   每个样本长度 (block_size): {block_size}")
        # save text ids in a file
        text_ids_file = tmp_dir / "text_ids.pt"
        torch.save(dataset.ids, text_ids_file)
        print(f"   文本 IDs 已保存到: {text_ids_file}")
        
        # 4. 测试单个样本
        print("\n4. 测试单个样本...")
        x, y = dataset[0]
        print(f"   x 形状: {x.shape}, y 形状: {y.shape}")
        print(f"   x 前10个 tokens: {x[:10].tolist()}")
        print(f"   y 前10个 tokens: {y[:10].tolist()}")
        print(f"   x 最后一个 token: {x.tolist()}")
        print(f"   y 最后一个 token: {y.tolist()}")
        
        x, y = dataset[1]
        print(f"   x 形状: {x.shape}, y 形状: {y.shape}")
        print(f"   x 前10个 tokens: {x[:10].tolist()}")
        print(f"   y 前10个 tokens: {y[:10].tolist()}")
        print(f"   x 最后一个 token: {x.tolist()}")
        print(f"   y 最后一个 token: {y.tolist()}")
        
        
        # 验证错位关系：y[i] 应该等于 x[i+1]
        print("\n5. 验证 x 和 y 的错位关系...")
        is_correct = torch.allclose(y[:-1], x[1:])
        print(f"   y[:-1] == x[1:] (错位关系): {is_correct}")
        if is_correct:
            print("   ✓ 错位关系正确！y 序列是 x 序列向右偏移 1 位")
        else:
            print("   ✗ 错位关系错误！")
        
        # 6. 测试多个样本
        print("\n6. 测试多个样本...")
        print("   样本 0:")
        x0, y0 = dataset[0]
        print(f"      x[0:5] = {x0[:5].tolist()}")
        print(f"      y[0:5] = {y0[:5].tolist()}")
        
        print("   样本 1:")
        x1, y1 = dataset[1]
        print(f"      x[0:5] = {x1[:5].tolist()}")
        print(f"      y[0:5] = {y1[:5].tolist()}")
        
        # 验证滑动窗口：样本1的x应该是样本0的x向右移动1位
        is_sliding = torch.allclose(x1[:-1], x0[1:])
        print(f"   滑动窗口关系 (x1[:-1] == x0[1:]): {is_sliding}")
        if is_sliding:
            print("   ✓ 滑动窗口正确！")
        
        # 7. 测试 DataLoader
        print("\n7. 测试 DataLoader...")
        batch_size = 4
        loader = make_loader(
            str(test_data_file), 
            tokenizer, 
            block_size=block_size, 
            batch_size=batch_size, 
            shuffle=False  # 不打乱以便观察
        )
        print(f"   Batch size: {batch_size}")
        print(f"   总批次数: {len(loader)}")
        
        # 获取第一个批次
        batch_x, batch_y = next(iter(loader))
        print(f"   批次 x 形状: {batch_x.shape}")  # [batch_size, block_size]
        print(f"   批次 y 形状: {batch_y.shape}")  # [batch_size, block_size]
        
        # 验证批次中的错位关系
        print("\n8. 验证批次中的错位关系...")
        batch_correct = torch.allclose(batch_y[:, :-1], batch_x[:, 1:])
        print(f"   批次中 y[:, :-1] == x[:, 1:]: {batch_correct}")
        if batch_correct:
            print("   ✓ 批次中的错位关系正确！")
        
        # 9. 测试解码（查看实际文本）
        print("\n9. 查看解码后的文本...")
        sample_x = x0[:10].tolist()
        sample_y = y0[:10].tolist()
        decoded_x = tokenizer.decode(sample_x)
        decoded_y = tokenizer.decode(sample_y)
        print(f"   x 前10个 tokens 解码: {repr(decoded_x)}")
        print(f"   y 前10个 tokens 解码: {repr(decoded_y)}")
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except ImportError as e:
        print(f"\n错误: {e}")
        print("请确保已安装必要的库: pip install torch tokenizers")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时文件（可选）
        if tmp_dir.exists():
            # 取消注释下面的行以自动清理临时文件
            # shutil.rmtree(tmp_dir)
            print(f"\n临时文件保存在: {tmp_dir}")
            print("   如需清理，请取消代码中的 shutil.rmtree() 注释")