"""
字节级分词器模块

这个模块实现了一个超简单的字节级分词器（ByteTokenizer），
它将文本直接编码为字节序列，每个字节作为一个token。
这种方法的优点是：
- 词汇表大小固定为256（所有可能的字节值）
- 可以处理任何UTF-8文本，无需预训练
- 实现简单，无需复杂的词汇表管理
"""
from __future__ import annotations
import torch


class ByteTokenizer:
    """超简单的字节级分词器。
    
    这个分词器将字符串直接编码为字节序列，每个字节作为一个token。
    这是最简单的分词方法，适合学习和实验。
    
    主要功能：
    - encode(str) -> LongTensor [N]: 将字符串编码为整数张量
    - decode(Tensor[int]) -> str: 将整数张量解码为字符串
    - vocab_size = 256: 词汇表大小固定为256（所有可能的字节值）
    """
    
    def encode(self, s: str) -> torch.Tensor:
        """将字符串编码为字节序列张量。
        
        参数:
            s (str): 要编码的字符串
            
        返回:
            torch.Tensor: 形状为 [N] 的长整型张量，包含字符串的UTF-8字节值
                         其中 N 是字符串编码后的字节数
                         
        示例:
            >>> tokenizer = ByteTokenizer()
            >>> tokenizer.encode("hello")
            tensor([104, 101, 108, 108, 111])
        """
        # 将字符串编码为UTF-8字节序列，然后转换为整数列表，最后创建张量
        return torch.tensor(list(s.encode('utf-8')), dtype=torch.long)

    def decode(self, ids) -> str:
        """将整数张量或列表解码为字符串。
        
        参数:
            ids: 可以是 torch.Tensor 或整数列表，包含要解码的字节值
            
        返回:
            str: 解码后的字符串
            
        注意:
            - 如果遇到无效的UTF-8字节序列，会使用 'ignore' 错误处理策略跳过
            - 输入可以是张量或列表，会自动转换
            
        示例:
            >>> tokenizer = ByteTokenizer()
            >>> tokenizer.decode(tensor([104, 101, 108, 108, 111]))
            'hello'
        """
        # 如果输入是张量，先转换为Python列表
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        # 将整数列表转换为字节对象，然后解码为UTF-8字符串
        # errors='ignore' 表示遇到无效字节时忽略而不是抛出异常
        return bytes(ids).decode('utf-8', errors='ignore')

    @property
    def vocab_size(self) -> int:
        """返回词汇表大小。
        
        对于字节级分词器，词汇表大小固定为256，
        因为一个字节可以表示0-255的所有可能值。
        
        返回:
            int: 词汇表大小，固定为256
        """
        return 256


# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("ByteTokenizer 测试")
    print("=" * 50)
    
    # 创建分词器实例
    tokenizer = ByteTokenizer()
    
    # 测试1: 基本编码和解码
    print("\n[测试1] 基本编码和解码")
    test_text = "I AM JULIE"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)
    print(f"原文: {test_text}")
    print("字母 -> token:\n", " ".join(f"'{ch}'-> {tok}\n" for ch, tok in zip(test_text, encoded.tolist())))
    print(f"token数量: {len(encoded)}")
    print(f"解码: {decoded}")
    print(f"✓ 编码解码成功: {test_text == decoded}")
    
    
    # 测试2: 

    print("\n[测试3] 词汇表大小")
    print(f"词汇表大小: {tokenizer.vocab_size}")
    print(f"✓ 词汇表大小正确: {tokenizer.vocab_size == 256}")
    
   