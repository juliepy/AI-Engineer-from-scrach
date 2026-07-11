# SOP：Chrome DevTools 验证闭环

当 UI 改动必须经过真实交互、截图、DOM 状态和 console 输出来判断，而不是只靠读代码时，就用这份 SOP。

## 目标

把 UI 验证变成 agent 可以反复执行的交互闭环，直到这条用户旅程变干净。

## 核心闭环

1. 选定目标页面或 app 实例。
2. 清掉旧的 console 噪声。
3. 记录 BEFORE 状态。
4. 触发 UI 路径。
5. 观察交互过程中的 runtime events。
6. 记录 AFTER 状态。
7. 修复问题，必要时重启 app。
8. 反复重跑验证，直到这条旅程 clean。

## 必需输入

- 稳定的启动命令
- 可重复的 UI journey
- 能抓 DOM、console 或截图的方式
- 明确“什么算 clean”的规则

## 执行 SOP

1. 把目标旅程写进 active plan。
2. 用可观察行为定义成功：文本出现、按钮可点、错误消失、console 干净、请求成功。
3. 交互前先拍初始状态。
4. 一次只触发一条路径。
5. 记录 runtime event、DOM 变化和可见输出。
6. 如果失败，只修最小负责层，然后重启。
7. 重跑同一路径，对比 BEFORE/AFTER 证据。

## Clean 标准

- 目标可见状态已经出现
- 没有意外错误
- console 噪声已理解或清理
- 重跑同一路径结果一致

## 需要同步更新的仓库工件

- 当前 active execution plan
- 如果它变成黄金旅程，更新 `docs/RELIABILITY.md`
- 如果可见行为改变了，更新 product spec
