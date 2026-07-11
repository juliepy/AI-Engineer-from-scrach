# --- 方式A：pypdf 读取纯文本PDF ---
from pypdf import PdfReader

def normalize_text(text: str) -> str:
    """文本清洗：去除多余空行、空格"""
    import re
    print(f"\n\n清洗前: {text}")
    text = re.sub(r"\n{3,}", "\n\n", text) # 将文本中的多余空行去除
    text = re.sub(r" +", " ", text) # 将文本中的多余空格去除
    text = text.strip() # 将文本中的多余空格和空行去除
    print(f"清洗后: {text}")
    return text   # 返回清洗后的文本


def extract_pdf_pypdf(path: str) -> str:
    print(f"\n\n提取前: {path}")
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return normalize_text("\n".join(parts))


# --- 方式B：Unstructured 智能分区解析（区分标题/段落/表格，适合RAG分段） ---
# 需要额外安装：pip install "unstructured[pdf]" unstructured-inference
# from unstructured.partition.auto import partition
#
# def extract_pdf_unstructured(pdf_path: str) -> list:
#     elements = partition(filename=pdf_path)
#     texts = [el.text for el in elements if getattr(el, "text", None)]
#     return texts


# 调用示例
if __name__ == "__main__":
    pdf_file = "手册.pdf"
    content = extract_pdf_pypdf(pdf_file)
    print(f"[pypdf 提取结果]\n{content[:500]}")
