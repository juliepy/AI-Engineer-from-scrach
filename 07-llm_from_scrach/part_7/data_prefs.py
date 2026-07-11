"""
偏好数据加载模块
用于加载和准备用于强化学习人类反馈（RLHF）的偏好数据集
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

# 尝试导入 datasets 库，如果失败则设置为 None
try:
    from datasets import load_dataset
except Exception:
    load_dataset = None

@dataclass
class PrefExample:
    """偏好示例数据类
    
    用于表示一个偏好对，包含：
    - prompt: 提示文本（输入）
    - chosen: 被选中的回复（更好的回复）
    - rejected: 被拒绝的回复（较差的回复）
    """
    prompt: str
    chosen: str
    rejected: str


def load_preferences(split: str = "train[:200]") -> List[PrefExample]:
    """加载偏好数据集
    
    尝试从 Anthropic HH-RLHF 数据集加载偏好对，如果加载失败则使用后备的玩具数据集。
    HH 数据集字段：'chosen'（被选中的完整对话）和 'rejected'（被拒绝的完整对话）。
    这里使用空字符串作为 prompt。
    
    Args:
        split: 数据集分割，默认为 "train[:200]"（训练集的前200条）
    
    Returns:
        偏好示例列表，每个示例包含 prompt、chosen 和 rejected
    """
    items: List[PrefExample] = []
    # 如果 datasets 库可用，尝试加载 Anthropic HH-RLHF 数据集
    if load_dataset is not None:
        try:
            ds = load_dataset("Anthropic/hh-rlhf", split=split)
            for row in ds:
                # 提取并清理 chosen 和 rejected 字段
                ch = str(row.get("chosen", "")).strip()
                rj = str(row.get("rejected", "")).strip()
                # 只有当两个字段都不为空时才添加
                if ch and rj:
                    items.append(PrefExample(prompt="", chosen=ch, rejected=rj))
        except Exception:
            print("Failed to load Anthropic/hh-rlhf dataset. Using fallback toy pairs.")
            print("加载 Anthropic/hh-rlhf 数据集失败，使用后备的玩具数据集。")
            pass
    # 如果加载失败或 datasets 库不可用，使用后备的玩具偏好对
    if not items:
        items = [
            PrefExample("Summarize: Scaling laws for neural language models.",
                        "Scaling laws describe how performance improves predictably as model size, data, and compute increase.",
                        "Scaling laws are when you scale pictures to look bigger."),
            PrefExample("Give two uses of attention in transformers.",
                        "It lets the model focus on relevant tokens and enables parallel context integration across positions.",
                        "It remembers all past words exactly without any computation."),
        ]
    return items


if __name__ == "__main__":
    """测试代码：加载偏好数据集并打印重要信息"""
    print("=" * 80)
    print("开始加载偏好数据集...")
    print("=" * 80)
    
    # 加载偏好数据集
    preferences = load_preferences()
    
    # 打印基本信息
    print(f"\n✓ 成功加载 {len(preferences)} 个偏好示例")
    print(f"✓ datasets 库状态: {'可用' if load_dataset is not None else '不可用'}")
    
    # 打印前几个示例的详细信息
    print("\n" + "=" * 80)
    print("示例详情（前 3 个）:")
    print("=" * 80)
    
    for i, example in enumerate(preferences[:3], 1):
        print(f"\n【示例 {i}】")
        print(f"  Prompt: {repr(example.prompt) if example.prompt else '(空)'}")
        print(f"  Chosen 长度: {len(example.chosen)} 字符")
        print(f"  Rejected 长度: {len(example.rejected)} 字符")
        print(f"  Chosen (前100字符): {example.chosen[:100]}...")
        print(f"  Rejected (前100字符): {example.rejected[:100]}...")
    
    # 统计信息
    print("\n" + "=" * 80)
    print("统计信息:")
    print("=" * 80)
    if preferences:
        avg_chosen_len = sum(len(ex.chosen) for ex in preferences) / len(preferences)
        avg_rejected_len = sum(len(ex.rejected) for ex in preferences) / len(preferences)
        print(f"  平均 Chosen 长度: {avg_chosen_len:.1f} 字符")
        print(f"  平均 Rejected 长度: {avg_rejected_len:.1f} 字符")
        print(f"  有 Prompt 的示例数: {sum(1 for ex in preferences if ex.prompt)}")
        print(f"  无 Prompt 的示例数: {sum(1 for ex in preferences if not ex.prompt)}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)