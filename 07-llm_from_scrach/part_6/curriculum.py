"""
课程学习（Curriculum Learning）模块

该模块实现了基于长度的课程学习策略，按照提示（prompt）的长度从短到长排序，
让模型先学习简单的短样本，再逐步学习复杂的长样本。
"""
from __future__ import annotations
from typing import List

class LengthCurriculum:
    """
    基于长度的课程学习迭代器
    
    该类实现了课程学习策略，将训练样本按照提示长度从短到长排序，
    在训练过程中先迭代短样本，再逐步迭代长样本，帮助模型更好地学习。
    
    示例:
        items = [("长文本提示", "回答"), ("短提示", "回答"), ("中等长度提示", "回答")]
        curriculum = LengthCurriculum(items)
        for prompt, response in curriculum:
            # 会按照提示长度从短到长依次返回
            print(prompt, response)
    """
    
    def __init__(self, items: List[tuple[str, str]]):
        """
        初始化课程学习迭代器
        
        Args:
            items: 训练样本列表，每个元素是一个 (prompt, response) 元组
                  - prompt: 输入提示文本
                  - response: 对应的回答文本
        """
        # 按照提示（第一个元素）的长度进行排序，从短到长
        self.items = sorted(items, key=lambda p: len(p[0]))
        # 当前迭代索引，初始化为0
        self._i = 0
    
    def __iter__(self):
        """
        使类成为可迭代对象
        
        当使用 for 循环或 iter() 函数时，会调用此方法重置迭代器。
        
        Returns:
            self: 返回自身作为迭代器对象
        """
        # 重置迭代索引为0，开始新的迭代
        self._i = 0
        return self
    
    def __next__(self):
        """
        获取下一个训练样本
        
        实现迭代器协议，每次调用返回下一个按长度排序的样本。
        当所有样本都迭代完后，抛出 StopIteration 异常。
        
        Returns:
            tuple[str, str]: 下一个训练样本 (prompt, response)
            
        Raises:
            StopIteration: 当所有样本都已迭代完毕时抛出
        """
        # 检查是否已经遍历完所有样本
        if self._i >= len(self.items):
            raise StopIteration
        
        # 获取当前索引对应的样本
        it = self.items[self._i]
        # 索引递增，指向下一个样本
        self._i += 1
        # 返回当前样本
        return it


if __name__ == "__main__":
    """
    测试代码：演示 LengthCurriculum 类的功能
    """
    print("=" * 60)
    print("LengthCurriculum 测试")
    print("=" * 60)
    
    # 创建测试数据：包含不同长度的提示
    test_items = [
        ("这是一个非常长的提示文本，用于测试课程学习功能，应该排在最后", "回答1"),
        ("短", "回答2"),
        ("这是一个中等长度的提示文本", "回答3"),
        ("中", "回答4"),
        ("这是一个比较长的提示文本，用于测试排序功能", "回答5"),
    ]
    
    print("\n【原始数据】")
    print(f"样本总数: {len(test_items)}")
    for i, (prompt, response) in enumerate(test_items, 1):
        print(f"  {i}. 提示长度: {len(prompt):2d} | 提示: {prompt[:30]}{'...' if len(prompt) > 30 else ''} | 回答: {response}")
    
    # 创建课程学习迭代器
    curriculum = LengthCurriculum(test_items)
    
    print("\n【排序后的数据（按提示长度从短到长）】")
    for i, (prompt, response) in enumerate(curriculum.items, 1):
        print(f"  {i}. 提示长度: {len(prompt):2d} | 提示: {prompt[:30]}{'...' if len(prompt) > 30 else ''} | 回答: {response}")
    
    # 测试迭代功能
    print("\n【迭代测试】")
    print("第一次迭代:")
    for i, (prompt, response) in enumerate(curriculum, 1):
        print(f"  第 {i} 个样本: 提示长度={len(prompt):2d}, 提示='{prompt[:20]}{'...' if len(prompt) > 20 else ''}', 回答='{response}'")
    
    # 测试第二次迭代（验证迭代器可以重置）
    print("\n第二次迭代（验证迭代器重置）:")
    for i, (prompt, response) in enumerate(curriculum, 1):
        print(f"  第 {i} 个样本: 提示长度={len(prompt):2d}, 提示='{prompt[:20]}{'...' if len(prompt) > 20 else ''}', 回答='{response}'")
    
    # 测试手动迭代
    print("\n【手动迭代测试】")
    curriculum_iter = iter(curriculum)
    print("使用 next() 手动获取前3个样本:")
    for i in range(3):
        try:
            prompt, response = next(curriculum_iter)
            print(f"  样本 {i+1}: 提示长度={len(prompt):2d}, 提示='{prompt[:20]}{'...' if len(prompt) > 20 else ''}'")
        except StopIteration:
            print(f"  样本 {i+1}: 迭代结束")
            break
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)