"""
评估函数模块
提供用于评估模型预测结果的指标函数，包括精确匹配和基于token的F1分数。
"""
from __future__ import annotations
import re
from typing import List, Tuple


def _normalize(s: str) -> str:
    """
    规范化字符串，用于评估前的预处理。
    
    将字符串转换为小写，移除非字母数字字符（保留空格），
    并将多个连续空格合并为单个空格。
    
    Args:
        s: 待规范化的字符串
        
    Returns:
        规范化后的字符串
        
    Example:
        >>> _normalize("Hello, World!  How are you?")
        'hello world how are you'
    """
    s = s.lower()  # 转换为小写
    s = re.sub(r"[^a-z0-9\s]", " ", s)  # 移除非字母数字字符，保留空格
    s = re.sub(r"\s+", " ", s).strip()  # 合并多个空格为单个空格，并去除首尾空格
    return s


def exact_match(pred: str, gold: str) -> float:
    """
    计算精确匹配分数。
    
    比较预测结果和标准答案在规范化后是否完全一致。
    
    Args:
        pred: 预测结果字符串
        gold: 标准答案字符串
        
    Returns:
        如果完全匹配返回1.0，否则返回0.0
        
    Example:
        >>> exact_match("Hello World", "hello world")
        1.0
        >>> exact_match("Hello", "World")
        0.0
    """
    return float(_normalize(pred) == _normalize(gold))


def token_f1(pred: str, gold: str) -> float:
    """
    计算基于token的F1分数。
    
    将预测和标准答案按token（单词）进行比较，计算F1分数。
    F1 = 2 * (precision * recall) / (precision + recall)
    
    Args:
        pred: 预测结果字符串
        gold: 标准答案字符串
        
    Returns:
        F1分数，范围在0.0到1.0之间
        
    Example:
        >>> token_f1("hello world", "world hello")
        1.0
        >>> token_f1("hello", "hello world")
        0.6666666666666666
    """
    # 规范化并分割为token列表
    p = _normalize(pred).split()
    g = _normalize(gold).split()
    
    # 如果两者都为空，返回1.0
    if not p and not g:
        return 1.0
    # 如果其中一个为空，返回0.0
    if not p or not g:
        return 0.0
    
    # 计算共同token的数量（考虑重复）
    common = 0
    gp = g.copy()  # 复制标准答案token列表，用于移除已匹配的token
    for t in p:
        if t in gp:
            gp.remove(t)  # 移除已匹配的token，避免重复计算
            common += 1
    
    # 如果没有共同token，返回0.0
    if common == 0:
        return 0.0
    
    # 计算精确率（precision）和召回率（recall）
    prec = common / len(p)  # 精确率 = 共同token数 / 预测token数
    rec = common / len(g)   # 召回率 = 共同token数 / 标准答案token数
    
    # 计算F1分数
    return 2 * prec * rec / (prec + rec)


if __name__ == "__main__":
    """
    测试代码：测试所有评估函数
    """
    print("=" * 60)
    print("评估函数测试")
    print("=" * 60)
    
    # 测试 _normalize 函数
    print("\n【测试 _normalize 函数】")
    test_cases_normalize = [
        ("Hello, World!  How are you?", "hello world how are you"),
        ("  Multiple   Spaces  ", "multiple spaces"),
        ("UPPERCASE lowercase 123", "uppercase lowercase 123"),
        ("Special@Chars#Here!", "special chars here"),
    ]
    for input_str, expected in test_cases_normalize:
        result = _normalize(input_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: '{input_str}'")
        print(f"   输出: '{result}'")
        print(f"   期望: '{expected}'")
        if result != expected:
            print(f"   ⚠ 不匹配!")
    
    # 测试 exact_match 函数
    print("\n【测试 exact_match 函数】")
    test_cases_exact = [
        ("Hello World", "hello world", 1.0, "完全匹配（大小写不同）"),
        ("Hello", "World", 0.0, "完全不匹配"),
        ("  Test  ", "test", 1.0, "匹配（有空格）"),
        ("Answer: 42", "answer 42", 1.0, "匹配（标点符号不同）"),
        ("Python", "Java", 0.0, "完全不匹配"),
    ]
    for pred, gold, expected, desc in test_cases_exact:
        result = exact_match(pred, gold)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc}")
        print(f"   预测: '{pred}' | 标准: '{gold}'")
        print(f"   结果: {result} | 期望: {expected}")
        if result != expected:
            print(f"   ⚠ 不匹配!")
    
    # 测试 token_f1 函数
    print("\n【测试 token_f1 函数】")
    test_cases_f1 = [
        ("hello world", "world hello", 1.0, "完全匹配（顺序不同）"),
        ("hello", "hello world", 2/3, "部分匹配（预测是子集）"),
        ("hello world", "hello", 2/3, "部分匹配（标准是子集）"),
        ("python java", "python cpp", 0.5, "部分匹配（一半相同）"),
        ("", "", 1.0, "两者都为空"),
        ("hello", "", 0.0, "预测为空"),
        ("", "world", 0.0, "标准为空"),
        ("cat dog", "dog cat bird", 2/3, "部分匹配（有额外token）"),
    ]
    for pred, gold, expected, desc in test_cases_f1:
        result = token_f1(pred, gold)
        # 允许小的浮点数误差
        match = abs(result - expected) < 1e-6
        status = "✓" if match else "✗"
        print(f"{status} {desc}")
        print(f"   预测: '{pred}' | 标准: '{gold}'")
        print(f"   结果: {result:.6f} | 期望: {expected:.6f}")
        if not match:
            print(f"   ⚠ 不匹配! 差异: {abs(result - expected):.6f}")
    
    # 综合测试示例
    print("\n【综合测试示例】")
    print("-" * 60)
    predictions = [
        "The answer is 42",
        "Hello, World!",
        "Python programming",
        "Wrong answer",
    ]
    gold_answers = [
        "the answer is 42",
        "hello world",
        "python programming language",
        "correct answer",
    ]
    
    print("预测结果 vs 标准答案:")
    print()
    for i, (pred, gold) in enumerate(zip(predictions, gold_answers), 1):
        em_score = exact_match(pred, gold)
        f1_score = token_f1(pred, gold)
        print(f"示例 {i}:")
        print(f"  预测: '{pred}'")
        print(f"  标准: '{gold}'")
        print(f"  精确匹配 (EM): {em_score:.4f}")
        print(f"  Token F1: {f1_score:.4f}")
        print()
    
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)