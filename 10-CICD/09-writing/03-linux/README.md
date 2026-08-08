# 03 · Linux 运维排查速通（CI / SDET）

面向 **Runner / 容器 / 宿主机** 上的笔试与线上排查：  
进程、网络、权限、core dump、日志、后台任务。

在 **WSL / Linux** 下练习；Windows 原生环境很多命令不可用。

## 目录

| 文件 | 主题 | 面试高频场景 |
| --- | --- | --- |
| [`00-速查.md`](./00-速查.md) | 一页命令表 | 考前速记 |
| [`01-进程排查.md`](./01-进程排查.md) | 找进程 / CPU·内存 / 僵死 / 杀进程 | Job 卡住、CPU 打满 |
| [`02-网络调试.md`](./02-网络调试.md) | 端口 / 连通 / DNS / 抓包入门 | Runner 连不上、依赖拉失败 |
| [`03-权限.md`](./03-权限.md) | 属主 / chmod / sudo / 能力 | Permission denied |
| [`04-core-dump.md`](./04-core-dump.md) | ulimit / core_pattern / gdb | 原生崩溃现场 |
| [`05-日志分析.md`](./05-日志分析.md) | journalctl / syslog / 应用日志 | 对齐 shell/python 日志题 |
| [`06-后台任务.md`](./06-后台任务.md) | `&` / nohup / screen / systemd | 后台跑任务、断线保活 |
| [`demos/`](./demos/) | 可跑小脚本 | 本地验证 |

## 推荐顺序

```
00 速查扫一眼
  → 01 进程（先会 ps/top/kill）
  → 02 网络（ss + curl + ping）
  → 03 权限（chmod/chown/sudo）
  → 06 后台（& / nohup / jobs）
  → 05 日志（journalctl + 文本日志）
  → 04 core dump（了解链路即可）
  → demos/ 跑一遍
```

## 怎么跑 demo

```bash
cd 03-linux/demos
bash demo_process.sh
bash demo_network.sh
bash demo_permission.sh
bash demo_bg.sh
# core dump 演示（可选，会编译小程序）
bash demo_coredump.sh
```

## 和前后模块的关系

| 模块 | 关系 |
|------|------|
| [`01-basic-shell`](../01-basic-shell/) | 脚本语法 + grep/sed/awk 日志 |
| [`02-log-python`](../02-log-python/) | Python 解析 / 筛异常任务 |
| **本目录** | 系统层：进程·网络·权限·崩溃·守护 |
