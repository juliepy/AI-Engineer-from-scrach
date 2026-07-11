"""Prompt/response formatting utilities (6.1).
提示/响应格式化工具 (6.1)。
We keep a very simple template with clear separators.
我们使用一个非常简单的模板，带有清晰的分隔符。
"""
from dataclasses import dataclass

# 格式化模板：用于将指令和响应组合成标准格式
# 使用 <s> 作为开始标记，</s> 作为结束标记
template = (
    "<s>\n"
    "### Instruction:\n{instruction}\n\n"
    "### Response:\n{response}</s>"
)

@dataclass
class Example:
    """示例数据类，包含指令和响应。
    
    Attributes:
        instruction: 指令文本
        response: 响应文本
    """
    instruction: str
    response: str


def format_example(ex: Example) -> str:
    """格式化完整的示例（包含指令和响应）。
    
    Args:
        ex: 包含指令和响应的示例对象
        
    Returns:
        格式化后的字符串，包含指令和响应
    """
    return template.format(instruction=ex.instruction.strip(), response=ex.response.strip())


def format_prompt_only(instruction: str) -> str:
    """仅格式化提示（只包含指令，响应为空）。
    
    Args:
        instruction: 指令文本
        
    Returns:
        格式化后的字符串，只包含指令部分，响应部分为空
    """
    return template.format(instruction=instruction.strip(), response="")


if __name__ == "__main__":
    # 测试 format_example 函数
    print("=" * 50)
    print("测试 format_example 函数:")
    print("=" * 50)
    example = Example(
        instruction="请解释什么是机器学习",
        response="机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出预测。"
    )
    formatted = format_example(example)
    print(formatted)
    print()
    
    # 测试 format_prompt_only 函数
    print("=" * 50)
    print("测试 format_prompt_only 函数:")
    print("=" * 50)
    prompt = format_prompt_only("什么是深度学习？")
    print(prompt)
    print()
    
    # 测试带空格的输入（验证 strip 功能）
    print("=" * 50)
    print("测试 strip 功能（去除前后空格）:")
    print("=" * 50)
    example_with_spaces = Example(
        instruction="  请解释神经网络  ",
        response="  神经网络是模拟人脑神经元连接的计算模型。  "
    )
    formatted_stripped = format_example(example_with_spaces)
    print(formatted_stripped)