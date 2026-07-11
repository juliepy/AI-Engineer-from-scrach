"""
监督微调（SFT）数据集加载模块

该模块提供了用于加载和准备监督微调（Supervised Fine-Tuning）数据集的工具。
主要功能包括从 HuggingFace 加载指令数据集，并提供回退机制以确保在没有网络或库的情况下也能工作。
"""

from __future__ import annotations
from typing import List, Dict, Tuple
from dataclasses import dataclass
import os
import traceback

# 尝试导入 datasets 库，如果导入失败则使用回退数据
try:
    from datasets import load_dataset
except Exception:
    print("Couldn't import `datasets`. Will use fallback data only.")
    load_dataset = None
    
from datasets import load_dataset

from formatters import Example


@dataclass
class SFTItem:
    """
    监督微调数据项
    
    用于表示一个监督微调的训练样本，包含提示词和对应的响应。
    
    Attributes:
        prompt (str): 输入提示词，通常是用户的指令或问题
        response (str): 期望的模型响应，即正确的回答
    """
    prompt: str
    response: str


def load_tiny_hf(split: str = "train[:200]", sample_dataset: bool = False) -> List[SFTItem]:
    """
    从 HuggingFace 加载小型指令数据集，如果失败则使用内置的回退数据
    
    该函数尝试从 HuggingFace 加载 `tatsu-lab/alpaca` 数据集，该数据集使用
    标准的指令格式（instruction, input, output）。如果加载失败或指定使用
    回退数据，则返回内置的小型示例数据集。
    
    Args:
        split (str): 数据集分割字符串，默认为 "train[:200]" 表示训练集的前200条
        sample_dataset (bool): 如果为 True，则跳过 HuggingFace 加载，直接使用回退数据
    
    Returns:
        List[SFTItem]: SFT 数据项列表，每个项包含 prompt 和 response
    
    Note:
        - 如果数据集中的 input 字段不为空，会将其追加到 instruction 后面
        - 只有当 instruction 和 output 都不为空时，才会创建数据项
        - 如果 HuggingFace 加载失败，会自动使用内置的回退数据
    """
    items: List[SFTItem] = []
    print(f"Loading dataset from HuggingFace: {split}")
    
    # 尝试从 HuggingFace 加载数据集
    if load_dataset is not None and not sample_dataset:
        try:
            # 加载 alpaca 数据集
            ds = load_dataset("tatsu-lab/alpaca", split=split)
            print(f"ds length : {len(ds)}")
            
            # 遍历数据集中的每一行
            for row in ds:
                # 提取并清理 instruction、input 和 output 字段
                instr = row.get("instruction", "").strip()
                inp = row.get("input", "").strip()
                out = row.get("output", "").strip()
                
                # 如果 input 字段存在，将其追加到 instruction 后面
                if inp:
                    instr = instr + "\n" + inp
                
                # 只有当 instruction 和 output 都不为空时，才创建数据项
                if instr and out:
                    items.append(SFTItem(prompt=instr, response=out))
        except Exception as e:
            # 如果加载失败，打印详细错误信息，后续会使用回退数据
            print(f"load dataset failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            pass
    
    # 如果没有成功加载数据，使用内置的回退数据
    if not items:
        # 内置的小型示例数据集
        print(f"use fallback data")
        seeds = [
            ("First prime number", "2"),
            ("What are the three primary colors?", "red"),
            ("Device name which points to direction?", "compass"),
        ]
        items = [SFTItem(prompt=p, response=r) for p, r in seeds]
    
    return items


# ==================== 测试函数 ====================

def test_load_dataset():
    """测试数据集加载并打印数据集内容"""
    print("=" * 60)
    print("测试数据集加载")
    print("=" * 60)
    
    # 加载数据集
    items = load_tiny_hf()
    
    # 打印数据集基本信息
    print(f"\n数据集总数: {len(items)}")
    print(f"数据项类型: {type(items[0]).__name__}")
    print(f"数据项属性: {list(items[0].__dict__.keys())}")
    
    # 打印前几个样本的详细内容
    print("\n" + "=" * 60)
    print("数据集样本预览（前 3 条）:")
    print("=" * 60)
    
    for i, item in enumerate(items[:3], 1):
        print(f"\n【样本 {i}】")
        print(f"Prompt ({len(item.prompt)} 字符):")
        print(f"  {item.prompt}")
        print(f"Response ({len(item.response)} 字符):")
        print(f"  {item.response}")
        print("-" * 60)
    
    # 打印统计信息
    print("\n" + "=" * 60)
    print("数据集统计信息:")
    print("=" * 60)
    
    prompt_lengths = [len(item.prompt) for item in items]
    response_lengths = [len(item.response) for item in items]
    
    print(f"Prompt 长度统计:")
    print(f"  平均长度: {sum(prompt_lengths) / len(prompt_lengths):.1f} 字符")
    print(f"  最短: {min(prompt_lengths)} 字符")
    print(f"  最长: {max(prompt_lengths)} 字符")
    
    print(f"\nResponse 长度统计:")
    print(f"  平均长度: {sum(response_lengths) / len(response_lengths):.1f} 字符")
    print(f"  最短: {min(response_lengths)} 字符")
    print(f"  最长: {max(response_lengths)} 字符")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 运行测试
    test_load_dataset()