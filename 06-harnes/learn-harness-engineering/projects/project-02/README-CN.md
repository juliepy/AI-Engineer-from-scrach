# Project 02: Agent-Readable Workspace

演示仓库可读性和显式连续性产物如何减少跨会话开发中的上下文丢失。

## 目录说明

| 目录 | 含义 |
|------|------|
| `starter/` | **起点**——基于 P1 solution 的代码，新增文档导入、详情视图、持久化功能待实现。harness 较弱：AGENTS.md 简陋，没有 session-handoff。 |
| `solution/` | **参考实现**——所有新功能已实现，配备完整的 workspace 文档（ARCHITECTURE.md、PRODUCT.md、session-handoff.md）。 |

## 使用方法

```sh
# 需要至少 2 个 agent 会话来完成
cd starter
npm install
# Session A: 实现文档导入和详情视图
# Session B: 实现持久化（观察 agent 能否快速恢复上下文）

cd ../solution
npm install
# 用完整 harness 重跑，对比会话恢复速度
```

## 具体任务对应关系

从 `starter/` 开始。starter 已经有 Project 01 的应用壳和一个较弱的
harness。本项目要补的是 Project 02 的产品切片，以及让第二个会话能快速接手的仓库文档。

| 功能 / 产物 | starter 状态 | solution 证据 |
|------|------|------|
| 文档导入 | renderer、preload、IPC、`DocumentService` 的导入链路不完整 | `ImportPanel.tsx`, `ipc-handlers.ts`, `document-service.ts` |
| 文档详情 | 详情面板还不能通过 IPC 加载并显示完整内容 | `DocumentDetail.tsx`, `IPC_CHANNELS.GET_DOCUMENT_CONTENT` |
| 基本持久化 | 导入文档不能完整跨重启恢复 | `persistence-service.ts`, `documents-meta.json` 处理 |
| agent 可读状态 | starter 没有最终交接文件 | `session-handoff.md`, 扩展后的 `docs/ARCHITECTURE.md` 和 `docs/PRODUCT.md` |

请按两次会话来跑：Session A 在三个功能全部完成前停止，Session B 只能依靠仓库状态继续。主要比较指标是有无交接文件时的恢复速度。

## 本项目涉及的功能

- 文档导入流程（文件选择器 + IPC 传输）
- 文档详情视图（元数据 + 内容展示）
- 基本持久化（导入的文档在重启后保留）

## 对应课件

- [Lecture 03: 让仓库成为唯一的真相来源](../../docs/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md)
- [Lecture 04: 拆分指令文件，而不是一个巨型文件](../../docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
