# 从零开始构建大语言模型 — 实践课程 (PyTorch)
# LLM from Scratch — Hands-On Curriculum (PyTorch)


## 第 0 部分 — 基础与思维方式 (Part 0 — Foundations & Mindset)
- **0.1** Understanding the high-level LLM training pipeline (pretraining → finetuning → alignment)  
  理解大语言模型训练的高层流程（预训练 → 微调 → 对齐）
- *0.2* Transformer 简介
- **0.3** Hardware & software environment setup (PyTorch, CUDA/Mac, mixed precision, profiling tools)  
  硬件与软件环境配置（PyTorch、CUDA/Mac、混合精度、性能分析工具）

```
conda create -n llm_from_scratch python=3.11
conda activate llm_from_scratch
pip install -r requirements.txt
```

llm_from_scratch\llm_env\Scripts\activate.bat
deactivate


## 第 1 部分 — 核心 Transformer 架构 (Part 1 — Core Transformer Architecture)
- **1.1** Positional embeddings (absolute learned vs. sinusoidal)  
  位置编码（绝对可学习编码 vs. 正弦编码）
- **1.2** Self-attention from first principles (manual computation with a tiny example)  
  从第一性原理理解自注意力机制（使用小例子手动计算）
- **1.3** Building a *single attention head* in PyTorch  
  在 PyTorch 中构建*单个注意力头*
- **1.4** Multi-head attention (splitting, concatenation, projections)  
  多头注意力（分割、拼接、投影）
- **1.5** Feed-forward networks (MLP layers) — GELU, dimensionality expansion  
  前馈网络（MLP 层）— GELU 激活函数、维度扩展
- **1.5** Residual connections & **LayerNorm**  
  残差连接与 **LayerNorm**
- **1.6** Stacking into a full Transformer block  
  堆叠成完整的 Transformer 块

## 第 2 部分 — 训练一个微型语言模型 (Part 2 — Training a Tiny LLM)
- **2.1** Byte-level tokenization  
  字节级分词
- **2.2** Dataset batching & shifting for next-token prediction  
  数据集批处理与偏移（用于下一个词预测）
- **2.3** Cross-entropy loss & label shifting  
  交叉熵损失与标签偏移
- **2.4** Training loop from scratch (no Trainer API)  
  从零开始编写训练循环（不使用 Trainer API）
- **2.5** Sampling: temperature, top-k, top-p  
  采样方法：temperature、top-k、top-p
- **2.6** Evaluating loss on val set  
  在验证集上评估损失

## 第 3 部分 — 架构现代化 (Part 3 — Modernizing the Architecture)
- **3.1** **RMSNorm** (replace LayerNorm, compare gradients & convergence)  
  **RMSNorm**（替换 LayerNorm，比较梯度与收敛性）
- **3.2** **RoPE** (Rotary Positional Embeddings) — theory & code  
  **RoPE**（旋转位置编码）— 理论与代码
- **3.3** SwiGLU activations in MLP  
  MLP 中的 SwiGLU 激活函数
- **3.4** KV cache for faster inference  
  KV 缓存（加速推理）
- **3.5** Sliding-window attention & **attention sink**  
  滑动窗口注意力与 **注意力池**
- **3.6** Rolling buffer KV cache for streaming  
  用于流式处理的循环缓冲区 KV 缓存

## 第 4 部分 — 规模扩展 (Part 4 — Scaling Up)
- **4.1** Switching from byte-level to BPE tokenization  
  从字节级切换到 BPE 分词
- **4.2** Gradient accumulation & mixed precision  
  梯度累积与混合精度
- **4.3** Learning rate schedules & warmup  
  学习率调度与预热
- **4.4** Checkpointing & resuming  
  检查点保存与恢复
- **4.5** Logging & visualization (TensorBoard / wandb)  
  日志记录与可视化（TensorBoard / wandb）

## 第 5 部分 — 混合专家模型 (Part 5 — Mixture-of-Experts, MoE)
- **5.1** MoE theory: expert routing, gating networks, and load balancing  
  MoE 理论：专家路由、门控网络与负载均衡
- **5.2** Implementing MoE layers in PyTorch  
  在 PyTorch 中实现 MoE 层
- **5.3** Combining MoE with dense layers for hybrid architectures  
  将 MoE 与稠密层结合以构建混合架构

## 第 6 部分 — 监督微调 (Part 6 — Supervised Fine-Tuning, SFT)
- **6.1** Instruction dataset formatting (prompt + response)  
  指令数据集格式化（提示词 + 回复）
- **6.2** Causal LM loss with masked labels  
  带掩码标签的因果语言模型损失
- **6.3** Curriculum learning for instruction data  
  指令数据的课程学习
- **6.4** Evaluating outputs against gold responses  
  根据标准答案评估输出

## 第 7 部分 — 奖励建模 (Part 7 — Reward Modeling)
- **7.1** Preference datasets (pairwise rankings)  
  偏好数据集（成对排序）
- **7.2** Reward model architecture (transformer encoder)  
  奖励模型架构（transformer 编码器）
- **7.3** Loss functions: Bradley–Terry, margin ranking loss  
  损失函数：Bradley-Terry、边际排序损失
- **7.4** Sanity checks for reward shaping  
  奖励塑造的合理性检查

## 第 8 部分 — 基于 PPO 的 RLHF (Part 8 — RLHF with PPO)
- **8.1** Policy network: our base LM (from SFT) with a value head for reward prediction.  
  策略网络：我们的基础语言模型（来自 SFT）加上一个用于奖励预测的价值头
- **8.2** Reward signal: provided by the reward model trained in Part 7.  
  奖励信号：由第 7 部分训练的奖励模型提供
- **8.3** PPO objective: balance between maximizing reward and staying close to the SFT policy (KL penalty).  
  PPO 目标：在最大化奖励和保持接近 SFT 策略（KL 惩罚）之间取得平衡
- **8.4** Training loop: sample prompts → generate completions → score with reward model → optimize policy via PPO.  
  训练循环：采样提示词 → 生成补全 → 使用奖励模型评分 → 通过 PPO 优化策略
- **8.5** Logging & stability tricks: reward normalization, KL-controlled rollout length, gradient clipping.  
  日志记录与稳定性技巧：奖励归一化、KL 控制的展开长度、梯度裁剪

## 第 9 部分 — 基于 GRPO 的 RLHF (Part 9 — RLHF with GRPO)
- **9.1** Group-relative baseline: instead of a value head, multiple completions are sampled per prompt and their rewards are normalized against the group mean.  
  组相对基线：不使用价值头，而是为每个提示词采样多个补全，并将它们的奖励相对于组均值进行归一化
- **9.2** Advantage calculation: each completion's advantage = (reward – group mean reward), broadcast to all tokens in that trajectory.  
  优势计算：每个补全的优势 = (奖励 - 组平均奖励)，广播到该轨迹中的所有词元
- **9.3** Objective: PPO-style clipped policy loss, but *policy-only* (no value loss).  
  目标函数：PPO 风格的裁剪策略损失，但*仅策略*（无价值损失）
- **9.4** KL regularization: explicit KL(π‖π_ref) penalty term added directly to the loss (not folded into the advantage).  
  KL 正则化：显式的 KL(π‖π_ref) 惩罚项直接添加到损失中（不折叠到优势中）
- **9.5** Training loop differences: sample `k` completions per prompt → compute rewards → subtract per-prompt mean → apply GRPO loss with KL penalty.  
  训练循环差异：每个提示词采样 `k` 个补全 → 计算奖励 → 减去每个提示词的均值 → 应用带 KL 惩罚的 GRPO 损失
