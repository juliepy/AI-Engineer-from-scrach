# pip install sentence-transformers

from sentence_transformers import SentenceTransformer

# 加载中文 embedding 模型
print("加载模型...")
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
print("模型加载完成")

sentences = [
    "RAG 检索增强生成",
    "大模型需要外部知识库",
    "hello world",
]

# normalize_embeddings=True 后余弦相似度 = 点积
embeddings = model.encode(sentences, normalize_embeddings=True)

print(embeddings.shape)  # (2, 1024)
print(embeddings)
