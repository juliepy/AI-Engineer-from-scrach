"""
字节级数据集模块

这个模块实现了一个字节级数据集类（ByteDataset），用于处理文本文件的原始字节数据，
并将其转换为适合语言模型训练的批次数据。

主要功能：
- 从文件读取原始字节数据
- 将数据分割为训练集和验证集
- 生成用于语言模型训练的 (x, y) 数据块对
- 支持随机采样批次数据
"""
from __future__ import annotations
from pathlib import Path
import torch


class ByteDataset:
    """字节级数据集类，用于语言模型训练。
    
    这个类读取文本文件的原始字节数据，并将其转换为适合语言模型训练的格式。
    数据会被分割为训练集和验证集，并提供批次数据生成功能。
    
    主要功能：
    - 从文件读取字节数据并转换为张量
    - 将数据分割为训练集和验证集
    - 生成用于语言模型训练的 (x, y) 数据块对
    - 支持随机采样批次数据
    
    属性:
        train (torch.Tensor): 训练集数据，形状为 [N_train]
        val (torch.Tensor): 验证集数据，形状为 [N_val]
        block_size (int): 序列长度（上下文窗口大小）
    """
    
    def __init__(self, path: str, block_size: int = 256, split: float = 0.9):
        """初始化数据集。
        
        从指定路径读取文本文件的原始字节数据，将其转换为张量，
        并按照指定比例分割为训练集和验证集。
        
        参数:
            path (str): 文本文件的路径
            block_size (int, optional): 序列长度（上下文窗口大小），默认为 256
            split (float, optional): 训练集所占比例，默认为 0.9（即90%用于训练，10%用于验证）
            
        注意:
            - 文件会以二进制模式读取，直接获取原始字节数据
            - 字节数据会被转换为长整型张量（dtype=torch.long）
            - split 参数决定了训练集和验证集的分割点
        """
        # 读取文件的原始字节数据
        data = Path(path).read_bytes()
        # 将字节数据转换为长整型张量
        data = torch.tensor(list(data), dtype=torch.long)
        # 计算训练集和验证集的分割点
        n = int(len(data) * split)
        # 分割数据：前 n 个字节作为训练集，剩余作为验证集
        self.train = data[:n]
        self.val = data[n:]
        # 保存序列长度（上下文窗口大小）
        self.block_size = block_size

    def get_batch(self, which: str, batch_size: int, device: torch.device):
        """获取一个批次的数据用于训练或验证。
        
        从训练集或验证集中随机采样多个序列块，生成 (x, y) 数据对。
        其中 x 是输入序列，y 是目标序列（x 向右偏移一位）。
        
        参数:
            which (str): 指定使用哪个数据集，'train' 表示训练集，其他值表示验证集
            batch_size (int): 批次大小，即一次返回多少个序列块
            device (torch.device): 目标设备（如 'cpu' 或 'cuda'），数据会被移动到该设备
            
        返回:
            tuple[torch.Tensor, torch.Tensor]: 返回 (x, y) 元组
                - x: 输入序列张量，形状为 [batch_size, block_size]
                - y: 目标序列张量，形状为 [batch_size, block_size]
                   y 是 x 向右偏移一位的结果，用于语言模型的下一token预测任务
                   
        注意:
            - 如果数据文件太小（小于 block_size + 1），会抛出断言错误
            - 每次调用都会随机采样不同的序列块
            - 返回的张量会被移动到指定的设备上
            
        示例:
            >>> dataset = ByteDataset("data.txt", block_size=128)
            >>> x, y = dataset.get_batch('train', batch_size=32, device=torch.device('cpu'))
            >>> print(x.shape, y.shape)  # torch.Size([32, 128]) torch.Size([32, 128])
        """
        # 根据 which 参数选择使用训练集还是验证集
        buf = self.train if which == 'train' else self.val
        # 确保数据足够大，至少需要 block_size + 1 个字节
        # （因为 y 需要比 x 多一个位置）
        assert len(buf) > self.block_size + 1, 'file too small for given block_size'
        # 随机生成 batch_size 个起始索引
        # 索引范围：[0, len(buf) - block_size - 1]，确保不会越界
        ix = torch.randint(0, len(buf) - self.block_size - 1, (batch_size,))
        # 从每个起始索引开始，提取 block_size 长度的序列作为输入 x
        x = torch.stack([buf[i:i+self.block_size] for i in ix])
        # 从每个起始索引+1开始，提取 block_size 长度的序列作为目标 y
        # y 是 x 向右偏移一位的结果，用于预测下一个token
        # abcdefg 
        # block size = 5
        # x = abcde [1, 2 , 3 , 4 , 5]
        # y = bcdefg [2, 3 , 4 , 5 , 6]
        # batch_zise 个 (x, y) = ([1, 2 , 3 , 4 , 5], [2, 3 , 4 , 5 , 6])
        y = torch.stack([buf[i+1:i+1+self.block_size] for i in ix])
        # 将数据移动到指定设备并返回
        return x.to(device), y.to(device)


# 测试代码
if __name__ == "__main__":
    import tempfile
    import os
    
    print("=" * 50)
    print("ByteDataset 测试")
    print("=" * 50)
    
    # 创建临时测试文件
    test_content = "This is a test file. " * 100  # 创建足够长的内容
    test_content += "Hello, World!" * 50
    
    path = Path(__file__).parent / 'tests' / 'toy.txt'
    # 确保 tests 目录存在，如果不存在则创建
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(test_content)
    print(f"test_file_path: {path}")
    
    try:
        # 测试1: 基本初始化
        print("\n[测试1] 基本初始化")
        dataset = ByteDataset(path, block_size=16, split=0.8)
        print(f"训练集大小: {len(dataset.train)}")
        print(f"验证集大小: {len(dataset.val)}")
        print(f"总数据大小: {len(dataset.train) + len(dataset.val)}")
        print(f"block_size: {dataset.block_size}")
        print(f"✓ 数据集初始化成功")
        
        # 测试2: 数据分割比例
        print("\n[测试2] 数据分割比例")
        total_size = len(dataset.train) + len(dataset.val)
        train_ratio = len(dataset.train) / total_size
        val_ratio = len(dataset.val) / total_size
        print(f"训练集比例: {train_ratio:.2%}")
        print(f"验证集比例: {val_ratio:.2%}")
        print(f"✓ 分割比例正确: {0.75 <= train_ratio <= 0.85}")  # 允许一些误差
        
        # 测试3: 获取批次数据
        print("\n[测试3] 获取批次数据")
        device = torch.device('cpu')
        batch_size = 4
        x, y = dataset.get_batch('train', batch_size=batch_size, device=device)
        print(f"x 形状: {x.shape}")
        print(f"y 形状: {y.shape}")
        print(f"✓ 批次形状正确: {x.shape == (batch_size, dataset.block_size)}")
        print(f"✓ y 形状与 x 相同: {x.shape == y.shape}")
        for i in range(batch_size):
            print(f"-" * 50)
            print(f"x[{i}]: {x[i].tolist()}")
            print(f"y[{i}]: {y[i].tolist()}")
            print(f"-" * 50)
        
        # 测试4: x 和 y 的偏移关系（核心测试）
        print("\n[测试4] x 和 y 的偏移关系（核心测试）")
        # 获取一个批次，检查 y 是否是 x 向右偏移一位
        x, y = dataset.get_batch('train', batch_size=1, device=device)
        # 对于每个样本，y 应该是 x 向右偏移一位
        x_sample = x[0]
        y_sample = y[0]
        # 检查：y[i] 应该等于 x[i+1]（对于 i < block_size-1）
        offset_correct = torch.all(y_sample[:-1] == x_sample[1:])
        print(f"x[0:5]: {x_sample[:5].tolist()}")
        print(f"y[0:5]: {y_sample[:5].tolist()}")
        print(f"✓ 偏移关系正确: {offset_correct.item()}")
        
        # 测试5: 训练集和验证集分别获取批次
        print("\n[测试5] 训练集和验证集分别获取批次")
        x_train, y_train = dataset.get_batch('train', batch_size=2, device=device)
        x_val, y_val = dataset.get_batch('val', batch_size=2, device=device)
        print(f"训练批次 x 形状: {x_train.shape}")
        print(f"验证批次 x 形状: {x_val.shape}")
        print(f"✓ 训练集和验证集都能正常获取批次")
        
        # 测试6: 不同 block_size
        print("\n[测试6] 不同 block_size")
        dataset2 = ByteDataset(path, block_size=16, split=0.9)
        x, y = dataset2.get_batch('train', batch_size=3, device=device)
        print(f"block_size=16 时，x 形状: {x.shape}")
        print(f"✓ 不同 block_size 正常工作: {x.shape == (3, 16)}")
        
        # 测试7: 设备移动
        print("\n[测试7] 设备移动")
        x, y = dataset.get_batch('train', batch_size=2, device=device)
        print(f"x 设备: {x.device}")
        print(f"y 设备: {y.device}")
        print(f"✓ 数据已移动到指定设备: {x.device == device}")
        
        # 测试8: 随机性测试（多次获取应该得到不同的数据）
        print("\n[测试8] 随机性测试")
        x1, y1 = dataset.get_batch('train', batch_size=1, device=device)
        x2, y2 = dataset.get_batch('train', batch_size=1, device=device)
        # 如果数据足够大，两次采样应该大概率不同
        are_different = not torch.equal(x1, x2)
        print(f"两次采样是否不同: {are_different}")
        print(f"✓ 随机采样功能正常")
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
    finally:
        pass
    #     # 清理临时文件
    #     if os.path.exists(test_file_path):
    #         os.unlink(test_file_path)
    #         print(f"\n已清理临时测试文件: {test_file_path}")