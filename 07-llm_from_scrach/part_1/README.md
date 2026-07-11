# Part 1 — 核心 Transformer 架构

从零手搓 Transformer 的**第一部分**：分词器 → 位置编码 → 自注意力 → 多头 → FFN → Transformer Block。

推荐用 `orchestrator.py` 串联演示与测试，按课节逐步学习。

---

## 学习目标

学完 Part 1，你应该能回答：

1. 字节级分词器如何把文本变成 token id？`vocab_size` 为什么是 256？
2. 位置编码解决什么问题？学习式 vs 正弦式有何区别？
2. Self-Attention 五步：`Q/K/V` 投影 → `QK^T/√d_k` → mask → softmax → `@V`
4. 单头 vs 多头的区别（`d_k` 是向量维度，不是头数）
5. 因果掩码为什么让上三角为 0？
6. Transformer Block 里残差 + LayerNorm 怎么串起来？

---

## 环境准备

```bash
cd 07-llm_from_scrach
# 建议用课程环境（见上级 README_cn.md）
pip install -r requirements.txt

cd part_1
```

依赖：`numpy`、`torch`、`pytest`、`matplotlib`（可视化时需要）。

---

## 项目结构

```text
part_1/
├── orchestrator.py               # 一键跑通 Part 1 演示 + 测试
├── tokenizer.py                  # 0  字节级分词器（ByteTokenizer）
├── pos_encoding.py               # 1.1 位置编码（学习式 + 正弦式）
├── attn_numpy_demo.py            # 1.2 NumPy 手算自注意力（无 PyTorch）
├── attn_numpy_demo.ipynb         # 1.2 同上，Notebook 分步版
├── single_head.py                # 1.3 单头注意力（PyTorch）
├── multi_head.py                 # 1.4 多头注意力（带 shape 追踪）
├── ffn.py                        # 1.5 前馈网络（GELU）
├── block.py                      # 1.6 Transformer Block（残差 + LayerNorm）
├── attn_mask.py                  # 因果掩码工具
├── vis_utils.py                  # 可视化辅助
├── demo_mha_shapes.py            # 多头矩阵乘法逐步打印
├── demo_visualize_multi_head.py  # 多头注意力热力图
├── images/                       # 讲义配图
├── out/                          # 运行后生成（日志、PNG）
└── tests/
    ├── test_attn_math.py         # NumPy 手算 vs PyTorch 单头对齐
    └── test_causal_mask.py       # 因果掩码行为验证
```

---

## 教学步骤（推荐 7 节课）

### 第 0 课 · 分词器

**文件：** `tokenizer.py`

**要点：**

- 模型输入不是字符串，而是 **token id 序列**（整数张量）
- **字节级分词**：`str → UTF-8 bytes → [0, 255]`，每个字节一个 token
- `vocab_size = 256` 固定，无需预训练词表，任意 UTF-8 文本都能编码
- `encode(s) -> LongTensor [N]`；`decode(ids) -> str`（无效字节用 `errors='ignore'` 跳过）

**课堂操作：**

```bash
python tokenizer.py
```

对照 `images/token.png`，理解「文本 → 字节序列 → Embedding 查表」这条链路。

**检查点：** `"hello"` 编码后是 `[104, 101, 108, 108, 111]`，解码能还原原文。

---

### 第 1 课 · 1.1 位置编码

**文件：** `pos_encoding.py`

**要点：**

- Transformer 并行处理 token，本身没有顺序信息
- **学习式**：`nn.Embedding(max_len, d_model)`，可训练，长度外推差
- **正弦式**：固定公式，可外推到更长序列

**课堂操作：**

```bash
python pos_encoding.py
```

对照 `images/pos_embeding.png`，观察不同位置的编码向量。

---

### 第 2 课 · 1.2 从第一性原理手算 Attention

**文件：** `attn_numpy_demo.py` 或 `attn_numpy_demo.ipynb`

**要点：**

- 本例：`T=3`，`d_model=4`，`d_k=d_v=4`，**单头**
- 五步：`X → Q,K,V → Scores → Mask → Weights → Output`
- `d_k` 是 Q/K 向量长度，**不是头数**

**课堂操作：**

```bash
python attn_numpy_demo.py
```

或用 Notebook 逐步执行，对照 `images/single_head_att.png`。

**检查点：** 能说出 `Scores (1,3,3)`、`Weights (1,3,3)`、`Output (1,3,4)` 各代表什么。

---

### 第 3 课 · 1.3 单头注意力（PyTorch）

**文件：** `single_head.py`、`attn_mask.py`

**要点：**

- 公式：`Attention(Q,K,V) = softmax(QK^T / √d_k) · V`
- `causal_mask`：上三角置 `-inf`，保证 token 只能看自己和前面
- PyTorch 实现与 NumPy 手算应对齐

**课堂操作：**

```bash
python single_head.py
```

---

### 第 4 课 · 1.4 多头注意力

**文件：** `multi_head.py`、`demo_mha_shapes.py`

**要点：**

- `d_head = d_model // n_head`
- 流程：split → 每头独立 attention → concat → `W_o` 投影
- 多头 = 多套 Q/K/V，不是 `d_k=2` 就有 2 个头

**课堂操作：**

```bash
python multi_head.py
python demo_mha_shapes.py    # 逐步打印 shape，日志写入 out/mha_shapes.txt
```

对照 `images/multi_head_attention.png`、`images/attention.png`。

**可选可视化：**

```bash
python demo_visualize_multi_head.py
# 或在 orchestrator 里加 --visualize
```

---

### 第 5 课 · 1.5 前馈网络 FFN

**文件：** `ffn.py`

**要点：**

- 结构：`Linear → GELU → Linear`
- 中间层通常 `4 × d_model`（升维再压回）
- 每个 token 独立过 FFN（与 attention 的「token 之间交互」互补）

**课堂操作：**

```bash
python ffn.py
```

---

### 第 6 课 · 1.6 Transformer Block 拼装

**文件：** `block.py`

**要点（Pre-LN 架构）：**

```text
x → LN → MultiHeadAttention → +x (残差)
  → LN → FFN               → +x (残差)
```

**课堂操作：**

```bash
python block.py
```

**检查点：** 能画出 Block 数据流，说明为什么需要两次残差连接。

---

## 一键验收：`orchestrator.py`

全部课节学完后，用 orchestrator **串联跑通** Part 1：

```bash
cd part_1
python orchestrator.py
```

带可视化（保存注意力热力图到 `out/`）：

```bash
python orchestrator.py --visualize
```

### orchestrator 执行顺序

| 顺序 | 命令 | 对应课节 | 作用 |
|------|------|----------|------|
| 1 | `python attn_numpy_demo.py` | 1.2 | NumPy 手算 sanity check |
| 2 | `pytest tests/test_attn_math.py` | 1.2 ↔ 1.3 | 手算结果与 PyTorch 单头一致 |
| 3 | `pytest tests/test_causal_mask.py` | 1.3 | 因果掩码正确 |
| 4 | `python demo_mha_shapes.py` | 1.4 | 多头 shape 逐步追踪 |
| 5 | `python demo_visualize_multi_head.py` | 1.4 | （`--visualize`）注意力热力图 |

全部通过时输出：

```text
All Part 1 demos/tests completed.
```

---

## 常见问题

**Q: 必须先跑 orchestrator 吗？**  
A: 不用。按 0 → 1.1 → 1.6 顺序学各文件；orchestrator 是**期末验收**，确认你理解了整条链路。

**Q: `attn_numpy_demo.py` 和 `.ipynb` 选哪个？**  
A: 课堂讲解推荐 Notebook（可一步步改数字）；快速验证用 `.py`。

**Q: orchestrator 为什么不跑 `tokenizer.py` / `pos_encoding.py` / `block.py`？**  
A: 它聚焦 **attention 数学正确性**（手算、单头、多头、掩码）。分词器、位置编码和 Block 在各模块里单独 `python xxx.py` 演示。

**Q: pytest 失败怎么办？**  
A: 先看失败用例名。常见原因：改了 `attn_numpy_demo.py` 的权重矩阵但未同步测试期望值。

---

## 与课程大纲对应

| 大纲编号 | 本目录文件 |
|----------|------------|
| 0 分词器 | `tokenizer.py` |
| 1.1 位置编码 | `pos_encoding.py` |
| 1.2 手算 Self-Attention | `attn_numpy_demo.py` / `.ipynb` |
| 1.3 单头注意力 | `single_head.py` |
| 1.4 多头注意力 | `multi_head.py` |
| 1.5 FFN + 残差/LN | `ffn.py` |
| 1.6 Transformer Block | `block.py` |

下一部分：**Part 2 — 训练微型语言模型**（loss、训练循环、完整 LM）。
