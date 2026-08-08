# Demo：用 Python 理解「容器负载均衡」

对应笔记：[01-优化方向.md](../../01-优化方向.md)

## 先说清楚

| 问题 | 答案 |
|------|------|
| GitLab 负载均衡的 Python 代码在哪？ | **不在你的业务仓库里**；调度在 GitLab / Runner（Go） |
| 你要会的是什么？ | 理解规则：`tags` 分池 + `concurrent` 限流 + 谁闲谁接 |
| 这个 Demo 做什么？ | 用十几行 Python **模拟**最少连接调度，方便建立直觉 |

## GitLab 自带负载均衡策略吗？

**有调度，但没有像 Nginx 那样可选的「轮询 / 最少连接 / IP 哈希」策略开关。**

GitLab 自带的是 **Job → Runner 分配**：

1. Job 进入队列  
2. 找出 **在线、tags 匹配、还没跑满** 的 Runner  
3. 把 Job 派给其中一个有空位的 Runner  
4. 该 Runner 用 Docker 执行器 **再起一个容器** 跑 `script`

你能控制的「均衡手段」主要是运维配置，不是 yml 里选算法：

| 你配什么 | 作用 |
|----------|------|
| 多台 / 多个 Runner | 多个工人抢活，天然分流 |
| Job `tags` | 进哪个池（test / build） |
| Runner `concurrent` / `limit`（`config.toml`） | 每台最多同时几个 Job（几个容器） |
| 共享 Runner 公平性 | 多项目挤同一池时，平台侧会排队协调（细节随版本变） |

所以：

- 面试别说：「我们开了 GitLab 的 round-robin 策略」——**没有这种用户选项**  
- 应该说：「多 Runner + tags 分池 + concurrent 限流，平台把 Job 派给空闲且匹配的 Runner，每个 Job 一个容器」

本 Demo 里的「最少连接」只是**帮助理解**的简化模型，不等于 GitLab 官方公开的可选项名称。

## 跑

```bash
cd demos/runner_lb
python schedule_demo.py
```

会看到多个 `app-test` Job 分到 `runner-test-1/2` 并行起容器，`build_fw` 进构建池。

## 核心函数（记思路即可）

```python
def pick_runner(runners, job):
    candidates = [r for r in runners if job.tag in r.tags and r.free_slots > 0]
    return min(candidates, key=lambda r: r.running)  # 最少连接
```
