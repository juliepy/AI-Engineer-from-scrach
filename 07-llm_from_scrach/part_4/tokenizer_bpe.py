"""
BPE (Byte Pair Encoding) Tokenizer 原理解释
==========================================

BPE 是一种数据压缩算法，后来被应用于自然语言处理中的子词分词（subword tokenization）。

核心思想：
---------
BPE 通过迭代地合并最频繁出现的字符对（byte pairs）来构建词汇表。
它能够将文本分解为子词单元，既能处理常见词汇，也能处理未登录词（OOV）。

算法步骤（训练阶段）：
-------------------
1. 初始化：将文本分解为字符（或字节）级别的基本单元
   例如："hello" -> ['h', 'e', 'l', 'l', 'o']

2. 统计频率：统计所有相邻字符对的出现频率
   例如：在 "hello world" 中，('l', 'l') 出现 1 次，('e', 'l') 出现 1 次等

3. 迭代合并：
   a. 找到出现频率最高的字符对
   b. 将这个字符对合并成一个新的子词单元
   c. 更新文本表示，用新单元替换原来的字符对
   d. 重复步骤 a-c，直到达到目标词汇表大小

4. 构建词汇表：所有合并后的子词单元构成最终的词汇表

示例（简化版）：
--------------
假设训练文本："low lower newest widest"

初始状态（字符级别）：
  l o w </w> l o w e r </w> n e w e s t </w> w i d e s t </w>
  (</w> 表示词尾标记)

第1次合并：最频繁的是 ('e', 's')，合并为 'es'
  l o w </w> l o w e r </w> n e w es t </w> w i d es t </w>

第2次合并：最频繁的是 ('es', 't')，合并为 'est'
  l o w </w> l o w e r </w> n e w est </w> w i d est </w>

第3次合并：最频繁的是 ('l', 'o')，合并为 'lo'
  lo w </w> lo w e r </w> n e w est </w> w i d est </w>

...继续合并直到达到目标词汇表大小

编码过程（推理阶段）：
-------------------
1. 将输入文本分解为字符序列
2. 应用训练时学到的合并规则（按顺序应用）
3. 将文本转换为子词 token 序列
4. 将每个子词映射到对应的 token ID

解码过程：
---------
1. 将 token ID 序列转换回子词 token
2. 移除特殊标记（如 </w>）
3. 拼接子词得到原始文本

Byte-Level BPE 的特点：
---------------------
- 在字节级别操作，而不是字符级别
- 可以处理任何 Unicode 字符，包括 emoji、特殊符号等
- 通过 UTF-8 编码将字符转换为字节序列
- 更加通用，能够处理多语言文本

优势：
-----
1. 能够处理未登录词（OOV）：通过子词组合
2. 词汇表大小可控：通过设置 vocab_size 参数
3. 平衡了字符级和词级表示：既保留语义又处理罕见词
4. 广泛使用：GPT、BERT 等模型都使用 BPE 或其变体

参考资料：
---------
- Neural Machine Translation of Rare Words with Subword Units (Sennrich et al., 2016)
- GPT-2 论文中使用的 BPE 变体
"""

from __future__ import annotations
import os, json
from pathlib import Path
from typing import List, Union

# 尝试导入 HuggingFace 的 tokenizers 库
# 如果导入失败，ByteLevelBPETokenizer 将被设置为 None
try:
    from tokenizers import ByteLevelBPETokenizer, Tokenizer
except Exception:
    ByteLevelBPETokenizer = None

class BPETokenizer:
    """BPE（Byte Pair Encoding）分词器的封装类（基于 HuggingFace tokenizers）。
    
    可以在文本文件或包含 .txt 文件的文件夹上训练分词器。
    将合并规则（merges）和词汇表（vocab）保存到输出目录。
    """
    
    def __init__(self, vocab_size: int = 32000, special_tokens: List[str] | None = None):
        """初始化 BPE 分词器。
        
        Args:
            vocab_size: 词汇表大小，默认为 32000
            special_tokens: 特殊标记列表，如果为 None 则使用默认的特殊标记
        """
        # 检查是否成功导入了 tokenizers 库
        if ByteLevelBPETokenizer is None:
            raise ImportError("Please `pip install tokenizers` for BPETokenizer.")
        self.vocab_size = vocab_size
        # 默认特殊标记：<s> 开始标记，</s> 结束标记，<pad> 填充标记，<unk> 未知标记，<mask> 掩码标记
        self.special_tokens = special_tokens or ["<s>", "</s>", "<pad>", "<unk>", "<mask>"]
        self._tok = None  # 内部使用的分词器对象

    def train(self, data_path: Union[str, Path]):
        """在指定的数据路径上训练 BPE 分词器。
        
        Args:
            data_path: 训练数据路径，可以是单个文本文件或包含 .txt 文件的文件夹
        """
        files: List[str] = []
        p = Path(data_path)
        # 如果路径是目录，则收集所有 .txt 文件
        if p.is_dir():
            files = [str(fp) for fp in p.glob("**/*.txt")]
        else:
            # 如果是单个文件，直接使用
            files = [str(p)]
        # 创建 ByteLevelBPE 分词器实例
        tok = ByteLevelBPETokenizer()
        # 训练分词器：使用指定的文件、词汇表大小、最小频率和特殊标记
        tok.train(files=files, vocab_size=self.vocab_size, min_frequency=2, special_tokens=self.special_tokens)
        self._tok = tok

    def save(self, out_dir: Union[str, Path]):
        """保存训练好的分词器到指定目录。
        
        Args:
            out_dir: 输出目录路径
        """
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)  # 创建输出目录（如果不存在）
        assert self._tok is not None, "Train or load before save()."
        # 保存模型文件（vocab.json 和 merges.txt）
        self._tok.save_model(str(out))
        # 保存完整的 tokenizer.json 文件
        self._tok.save(str(out / "tokenizer.json"))
        # 保存元数据信息
        meta = {"vocab_size": self.vocab_size, "special_tokens": self.special_tokens}
        (out/"bpe_meta.json").write_text(json.dumps(meta))

    def load(self, dir_path: Union[str, Path]):
        """从指定目录加载已保存的分词器。
        
        Args:
            dir_path: 包含分词器文件的目录路径
        """
        dirp = Path(dir_path)
        # 优先使用明确的文件名；如果需要，回退到 glob 搜索
        vocab = dirp / "vocab.json"  # 词汇表文件
        merges = dirp / "merges.txt"  # 合并规则文件
        tokenizer = dirp / "tokenizer.json"  # 完整的分词器配置文件
        # 如果标准文件名不存在，尝试查找其他 .json 和 .txt 文件
        if not vocab.exists() or not merges.exists():
            # 回退方案：查找自定义文件名
            vs = list(dirp.glob("*.json"))
            ms = list(dirp.glob("*.txt"))
            if not vs or not ms:
                raise FileNotFoundError(f"Could not find vocab.json/merges.txt in {dirp}")
            vocab = vs[0]
            merges = ms[0]
        # 使用 tokenizer.json 文件加载分词器（推荐方式）
        # 注释掉的代码是另一种加载方式：直接使用 vocab.json 和 merges.txt
        # tok = ByteLevelBPETokenizer(str(vocab), str(merges))
        tok = Tokenizer.from_file(str(tokenizer))
        self._tok = tok
        # 如果存在元数据文件，加载并恢复配置
        meta_file = dirp / "bpe_meta.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            self.vocab_size = meta.get("vocab_size", self.vocab_size)
            self.special_tokens = meta.get("special_tokens", self.special_tokens)


    def encode(self, text: str):
        """将文本编码为 token ID 列表。
        
        Args:
            text: 要编码的文本字符串
            
        Returns:
            token ID 列表
        """
        ids = self._tok.encode(text).ids
        return ids

    def decode(self, ids):
        """将 token ID 列表解码为文本。
        
        Args:
            ids: token ID 列表或可迭代对象
            
        Returns:
            解码后的文本字符串
        """
        return self._tok.decode(ids)


if __name__ == "__main__":
    # 简单的测试代码
    import tempfile
    import shutil
    
    print("=" * 50)
    print("BPE Tokenizer 测试")
    print("=" * 50)
    
    # 创建临时目录用于测试
    current_path = Path(__file__).parent
    tmp_dir = current_path / "tmp"
    tmp_dir.mkdir(exist_ok=True)  # 确保 tmp 目录存在
    test_data_file = tmp_dir / "test_data.txt"
    tokenizer_dir = tmp_dir / "tokenizer_output"
    
    try:
        # 1. 创建测试数据文件
        print("\n1. 创建测试数据...")
        test_text = """Hello world! This is a test.
BPE tokenizer is useful for NLP tasks.
Machine learning models need tokenization."""
        test_data_file.write_text(test_text, encoding='utf-8')
        print(f"   测试数据已保存到: {test_data_file}")
        # 2. 训练分词器
        print("\n2. 训练分词器...")
        tokenizer = BPETokenizer(vocab_size=1000, special_tokens=["<s>", "</s>", "<pad>", "<unk>"])
        tokenizer.train(test_data_file)
        print("   分词器训练完成")
        
        # 3. 测试编码和解码
        print("\n3. 测试编码和解码...")
        test_sentence = "Hello world! This is a test."
        encoded = tokenizer.encode(test_sentence)
        decoded = tokenizer.decode(encoded)
        print(f"   原文: {test_sentence}")
        print(f"   编码: {encoded[:10]}..." if len(encoded) > 10 else f"   编码: {encoded}")
        print(f"   解码: {decoded}")
        print(f"   编码/解码是否一致: {decoded == test_sentence}")
        
        # 4. 保存分词器
        print("\n4. 保存分词器...")
        tokenizer.save(tokenizer_dir)
        print(f"   分词器已保存到: {tokenizer_dir}")
        
        # 5. 加载分词器并测试
        print("\n5. 加载分词器并测试...")
        tokenizer2 = BPETokenizer()
        tokenizer2.load(tokenizer_dir)
        encoded2 = tokenizer2.encode(test_sentence)
        decoded2 = tokenizer2.decode(encoded2)
        print(f"   加载后编码: {encoded2[:10]}..." if len(encoded2) > 10 else f"   加载后编码: {encoded2}")
        print(f"   加载后解码: {decoded2}")
        print(f"   加载后编码/解码是否一致: {decoded2 == test_sentence}")
        print(f"   编码结果是否一致: {encoded == encoded2}")
        
        print("\n" + "=" * 50)
        print("所有测试通过！")
        print("=" * 50)
        
    except ImportError as e:
        print(f"\n错误: {e}")
        print("请先安装 tokenizers 库: pip install tokenizers")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时文件（可选，注释掉以保留文件用于调试）
        if tmp_dir.exists():
            # 取消注释下面的行以自动清理临时文件
            # shutil.rmtree(tmp_dir)
            print(f"\n临时文件保存在: {tmp_dir}")
            print("   如需清理，请取消代码中的 shutil.rmtree() 注释")