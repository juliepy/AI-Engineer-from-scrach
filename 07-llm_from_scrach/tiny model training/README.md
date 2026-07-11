# Tiny GPT 训练示例

用 PyTorch 实现的极简 **字节级 GPT**（下一字节预测）：`tiny_llm` 包含模型 / 数据集 / 分词 / 采样；根目录 **`train.py`** 为训练入口，**`corpus/`** 下放示例文本。

## 依赖

需要 **Python 3.10+**。推荐在本目录单独建虚拟环境（已加入 `.gitignore` 的 `.venv/` 仅本地使用）：

**Windows（PowerShell）**

```powershell
cd "tiny model training"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows（cmd）**：`.\.venv\Scripts\activate.bat`  
**Linux / macOS**：`python3 -m venv .venv` 后执行 `source .venv/bin/activate`，再 `pip install -r requirements.txt`。

激活环境后，`python`、`pip` 均指向该隔离环境。

（若需特定 CUDA 版 PyTorch，可到 [pytorch.org](https://pytorch.org/get-started/locally/) 按说明安装以覆盖默认 wheel。）

## 运行

```bash
cd "tiny model training"
python train.py --data corpus/tiny.txt --steps 300 --sample_every 100
```

强制 CPU：加 `--cpu`。其它参数：`python train.py --help`。

## 代码框架图（文本）

运行时各模块大致关系如下（箭头表示依赖 / 数据流，`train.py` 为编排入口）：

```
                        +------------------------------+
                        |          train.py            |
                        |  参数解析 · 优化器 · 训练循环 · |
                        |  评估 · 保存检查点 · 周期性采样 · |
                        +--------------+---------------+
                                       |
              +--------------------------+---------------------------+
              |                          |                           |
              v                          v                           v
   +----------------------+    +----------------------+    +------------------+
   |     ByteTokenizer    |    |      ByteDataset     |    | corpus/*.txt      |
   |  字节 <-> token(256)|    |  读字节 train/val     |    | 原始语料（输入）  |
   +----------+-----------+    |  get_batch(x,y)      |    +--------+---------+
              |                 +----------+-----------+             |
              | vocab_size                 |                            |
              |                            +----------------------------+
              |                                        |
              v                                        v
   +=======================================================================+
   |                              GPT (gpt.py)                             |
   |   嵌入 · N 层因果 Transformer · 语言模型头 · 下一字节交叉熵            |
   |   generate(...) 内需采样时调用 utils/sampling.py (top-k / top-p)     |
   +=======================================================================+
              |
              v
   +----------------------+              +--------------------------+
   | runs/.../*.pt       |              | 采样文本 -> tok.decode() |
   | 检查点(model_*)       |              | （train.py 中打印预览）    |
   +----------------------+              +--------------------------+
```

## 目录一览

默认检查点目录 **`--out_dir runs/min-gpt`**（可自行修改）；`runs/` 已 `.gitignore`。`min-gpt/` 下仅两个 `.pt`、无子目录。

```
train.py                  # 训练入口：参数、数据与模型、训练循环、评估、保存检查点、周期性生成样本
corpus/
└── tiny.txt              # 示例语料（纯文本，供字节级数据集读取）
tiny_llm/
├── data/
│   └── dataset.py        # ByteDataset：读字节、划分 train/val、按块提供 (x, y) 批次
├── models/
│   └── gpt.py            # GPT：因果自注意力、Transformer Block、前向与 generate
├── tokenizers/
│   └── byte_tokenizer.py # ByteTokenizer：文本与字节 token 互转（词表 256）
└── utils/
    └── sampling.py       # 生成时 logits 过滤：top-k、top-p（nucleus）
runs/
└── min-gpt/
    ├── model_best.pt     # eval 验证 loss 当前最优时覆盖保存
    └── model_final.pt    # 训练结束再存一份收尾权重
```

