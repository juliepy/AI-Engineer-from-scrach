import re
import unicodedata
def normalize_text(s: str) -> str:
    """
    规范化文本
    """
    # 1. 规范化文本
    s = unicodedata.normalize("NFKC", s) # 将文本规范化，使其符合Unicode标准
    
    # 2. 去除零宽字符
    s = s.replace("\u200b", "")  # 零宽字符
    
    # 3. 去除多余空格
    s = re.sub(r"\s+", " ", s).strip() # 将文本中的多余空格去除
    
    # 4. 返回规范化后的文本
    return s

def wash_data(data: list[str]) -> list[str]:
    """
    清洗数据
    """
    return [normalize_text(d) for d in data]        

if __name__ == "__main__":
    data = [
        "Hello,\u200b world!",      # 含零宽字符
        "  多余   空格   文本  ",    # 含多余空格
        "ｈｅｌｌｏ　ｗｏｒｌｄ",  # 全角字符
    ]
    for original, cleaned in zip(data, wash_data(data)):
        print(f"原始: {repr(original)}") # repr() 函数返回一个对象的官方字符串表示
        print(f"清洗: {repr(cleaned)}") # repr() 函数返回一个对象的官方字符串表示
        print()