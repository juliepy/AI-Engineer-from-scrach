# GRPO (Group Relative Policy Optimization) 训练方法详解

## 一、GRPO 概述

GRPO（Group Relative Policy Optimization）是 PPO（Proximal Policy Optimization）的一个变体，专门设计用于语言模型的强化学习训练。与标准 PPO 相比，GRPO 的核心创新在于：

1. **轨迹级别的优势估计**：不需要价值函数头（Value Head）
2. **组内相对优势**：使用组内平均奖励作为基线，计算相对优势
3. **简化架构**：减少了模型复杂度，提高了训练效率

## 二、GRPO 架构流程（对应架构图）

根据架构图，GRPO 的训练流程如下：

```
输入 q → Policy Model → [o₁, o₂, ..., o_G] → Reference Model + Reward Model → [r₁, r₂, ..., r_G]
                                                                                      ↓
Policy Model ← KL散度反馈 ← [A₁, A₂, ..., A_G] ← Group Computation
```

### 详细步骤解析：

#### 1. **输入阶段（Query q）**
- **代码位置**：`train_grpo.py:114-124`
- **功能**：从提示池中选择 P 个提示，每个提示将生成 G 个完成
- **关键参数**：
  - `batch_prompts` (P)：每步的提示数量
  - `group_size` (G)：每个提示的完成数量

```python
# 选择P个提示，每个提示生成G个完成 → B = P*G 个轨迹
P = max(1, args.batch_prompts)
batch_prompts = prompts_pool[pool_idx: pool_idx + P]
prompt_texts = [format_prompt_only(p).replace("</s>", "") for p in batch_prompts]
```

#### 2. **生成阶段（Policy Model → o₁...o_G）**
- **代码位置**：`train_grpo.py:126-153`
- **功能**：使用当前策略模型为每个提示生成 G 个不同的响应
- **关键点**：
  - 使用 `policy.generate()` 生成响应
  - 每个响应都是独立的采样结果
  - 记录每个轨迹的边界位置（提示/响应分离点）

```python
for pid, p_ids in enumerate(prompt_in_ids):
    for g in range(G):  # 为每个提示生成G个完成
        idx = torch.tensor([p_ids], dtype=torch.long, device=device)
        out = policy.generate(idx, max_new_tokens=args.resp_len, temperature=2, top_k=3)
        full_ids = out[0].tolist()
        resp_ids = full_ids[boundary:]  # 提取响应部分
```

#### 3. **评估阶段（Reference Model + Reward Model）**
- **代码位置**：
  - Reference Model：`train_grpo.py:85-91`（初始化），`train_grpo.py:180`（计算对数概率）
  - Reward Model：`train_grpo.py:93-101`（初始化），`train_grpo.py:146`（计算奖励）
- **功能**：
  - **Reference Model**：冻结的参考策略，用于计算 KL 散度，防止策略偏离太远
  - **Reward Model**：评估生成响应的质量，给出标量奖励分数

```python
# 初始化冻结的参考策略
ref = PolicyWithValue(...).to(device)
ref.lm.load_state_dict(ckpt['model'])
for p_ in ref.parameters():
    p_.requires_grad_(False)  # 冻结所有参数

# 计算奖励
r_scalar = compute_reward(rm, tok, batch_prompts[pid], resp_ids, device)
```

#### 4. **奖励计算（r₁...r_G）**
- **代码位置**：`train_grpo.py:24-45`（compute_reward 函数）
- **功能**：对每个生成的响应计算奖励分数
- **关键点**：
  - 使用完整格式化的文本（提示+响应）
  - 奖励模型输出标量分数

```python
def compute_reward(reward_model, tok, prompt_text, response_ids, device):
    resp_text = tok.decode(response_ids)
    text = format_example(Example(prompt_text, resp_text))
    ids = tok.encode(text)
    x = torch.tensor([ids[:tok.block_size]], dtype=torch.long, device=device)
    r = reward_model(x)
    return float(r[0].item())
```

#### 5. **组计算（Group Computation）**
- **代码位置**：`train_grpo.py:190-231`
- **功能**：**GRPO 的核心创新** - 使用组内平均作为基线计算优势
- **关键公式**：
  ```
  组内平均奖励：μ_g = mean(r_i for i in group_g)
  优势值：A_i = r_i - μ_g
  ```
- **优势**：
  - 不需要价值函数头
  - 基线是自适应的（每个组有自己的基线）
  - 减少了方差，提高了训练稳定性

```python
# 计算每个提示组的形状化奖励的平均值
# GRPO的核心：使用组内平均作为基线
group_mean = torch.zeros(B, dtype=torch.float, device=device)
for pid in range(P):
    idxs = [i for i in range(B) if prompt_id_of[i] == pid]
    mean_val = raw_rewards_t[idxs_t].mean()  # 组内平均奖励
    group_mean[idxs_t] = mean_val

# 每个轨迹的优势，广播到其动作token
traj_adv = raw_rewards_t - group_mean  # (B,) GRPO的优势计算
```

#### 6. **KL 散度计算与反馈**
- **代码位置**：`train_grpo.py:176-188`, `train_grpo.py:241-242`
- **功能**：
  - 计算当前策略与参考策略的 KL 散度
  - 作为正则化项防止策略偏离太远
- **公式**：
  ```
  KL(π_new || π_ref) = E[log π_new(a|s) - log π_ref(a|s)]
  ```

```python
# 计算策略和参考策略的对数概率
pol_lp_full = model_logprobs(policy, seq)  # (B, T-1)
ref_lp_full = model_logprobs(ref, seq)     # (B, T-1)

# 动作token上的每token KL散度
kl_tok = (old_logp - ref_logp)  # (N_act,)
kl_now_ref_mean = (new_logp - ref_logp).mean()  # 平均KL散度
```

#### 7. **损失计算与更新（A₁...A_G → Policy Model）**
- **代码位置**：`train_grpo.py:233-260`, `grpo_loss.py:21-65`
- **功能**：计算 PPO 风格的裁剪损失并更新策略
- **损失函数**：
  ```
  L_total = L_PPO + λ_KL * KL(π_new || π_ref)
  
  其中：
  L_PPO = -E[min(ratio * A, clip(ratio, 1-ε, 1+ε) * A)]
  ratio = π_new(a|s) / π_old(a|s)
  ```

```python
# 计算GRPO损失
out_loss = ppo_policy_only_losses(
    new_logp=new_logp,
    old_logp=old_logp,
    adv=adv_flat,
    clip_ratio=0.2,
    kl_coef=args.kl_coef,
    kl_mean=kl_now_ref_mean,
)
loss = out_loss.total_loss

# 反向传播和优化
opt.zero_grad(set_to_none=True)
loss.backward()
torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
opt.step()
```

## 三、GRPO vs PPO 的关键区别

| 特性 | PPO | GRPO |
|------|-----|------|
| **价值函数** | 需要价值头（Value Head） | 不需要价值头 |
| **优势估计** | 使用 GAE（Generalized Advantage Estimation） | 使用组内相对优势 |
| **基线** | 价值函数估计 | 组内平均奖励 |
| **计算复杂度** | 较高（需要价值函数训练） | 较低（无需价值函数） |
| **适用场景** | 通用强化学习 | 语言模型 RLHF |

## 四、代码关键组件解析

### 1. **轨迹收集与填充**（`train_grpo.py:154-174`）

```python
# 填充为批次
B = len(seq_list)  # B = P*G
max_len = min(policy_ctx, max(s.numel() for s in seq_list))
seq = torch.zeros(B, max_len, dtype=torch.long, device=device)
mask = torch.zeros(B, max_len, dtype=torch.bool, device=device)

# 动作位置掩码：只对响应token计算损失
for i, (ids, bnd) in enumerate(zip(seq_list, boundary_list)):
    # ... 填充逻辑 ...
    mask[i, b:L] = True  # 只对响应部分计算损失
```

**关键点**：
- 只对响应 token 计算损失（忽略提示部分）
- 使用掩码标记动作位置
- 右对齐填充，保留最后 L 个 token

### 2. **优势广播**（`train_grpo.py:195-227`）

```python
# 构建从展平的动作token回到轨迹ID的索引映射
traj_id_for_token = []
for i in range(B):
    mrow = act_mask[i]
    n_i = int(mrow.sum().item())
    if n_i > 0:
        traj_id_for_token.extend([i] * n_i)

# 将轨迹级别的优势广播到token级别
adv_flat = traj_adv[traj_id_for_token]
```

**关键点**：
- 优势是轨迹级别的（每个响应一个优势值）
- 需要广播到该轨迹的所有动作 token
- 使用索引映射实现广播

### 3. **PPO 裁剪损失**（`grpo_loss.py:45-51`）

```python
# 计算重要性采样比率
ratio = torch.exp(new_logp - old_logp)  # (N,)

# PPO裁剪：取未裁剪和裁剪后的最小值
unclipped = ratio * adv
clipped = torch.clamp(ratio, 1.0 - clip_ratio, 1.0 + clip_ratio) * adv
policy_loss = -torch.mean(torch.min(unclipped, clipped))
```

**关键点**：
- 限制策略更新幅度（防止过大更新）
- 使用 `clip_ratio=0.2` 限制比率在 [0.8, 1.2] 范围内
- 取裁剪前后的最小值，确保保守更新

## 五、训练流程总结

1. **初始化**：
   - 加载 SFT 策略作为初始策略和参考策略
   - 加载奖励模型
   - 初始化优化器

2. **每个训练步骤**：
   ```
   a. 选择 P 个提示
   b. 为每个提示生成 G 个响应（共 P*G 个轨迹）
   c. 使用奖励模型计算每个响应的奖励
   d. 计算组内平均奖励作为基线
   e. 计算优势：A_i = r_i - μ_group
   f. 计算当前策略和参考策略的对数概率
   g. 计算 KL 散度
   h. 计算 PPO 损失（裁剪 + KL 惩罚）
   i. 反向传播并更新策略
   ```

3. **监控指标**：
   - `KL_move`：策略移动幅度（旧策略 vs 新策略）
   - `KL_ref`：与参考策略的偏离程度
   - `loss`：总损失值

## 六、关键超参数

- `group_size` (G)：每个提示的完成数量，影响基线计算的稳定性
- `kl_coef`：KL 散度惩罚系数，控制策略偏离参考策略的程度
- `clip_ratio`：PPO 裁剪比例，默认 0.2
- `lr`：学习率，通常较小（1e-5）
- `resp_len`：响应长度，影响生成文本的长度

## 七、优势与局限

### 优势：
1. **简化架构**：无需价值函数头，减少模型复杂度
2. **自适应基线**：组内平均作为基线，适应不同提示的奖励分布
3. **训练稳定**：相对优势减少了方差
4. **计算高效**：减少了需要训练的参数

### 局限：
1. **需要组采样**：必须为每个提示生成多个响应
2. **组大小敏感**：组大小影响基线质量
3. **不适合单样本场景**：需要多个样本才能计算组内平均

## 八、实际应用建议

1. **组大小选择**：通常 G=4 到 G=8，太小基线不稳定，太大计算开销大
2. **KL 系数调整**：从 0.01 开始，根据训练稳定性调整
3. **监控指标**：关注 KL_ref，确保策略不会偏离参考策略太远
4. **奖励模型质量**：奖励模型的质量直接影响训练效果

---

**总结**：GRPO 通过组内相对优势估计，简化了 PPO 的训练流程，特别适合语言模型的 RLHF 训练。其核心思想是用组内平均作为自适应基线，避免了价值函数的需求，同时保持了训练稳定性。
