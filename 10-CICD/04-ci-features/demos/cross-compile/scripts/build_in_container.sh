#!/usr/bin/env bash
# 固件构建 Job（在工具链 Docker 里跑）
# 真实链路：checkout → 交叉编译 → 打固件包（上传由宿主机 / 下一 Job 做）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p out/firmware

echo "========== 1) Checkout（Runner 工作区已有代码；这里记元数据） =========="
HOST_ARCH="$(uname -m)"
GIT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo nogit)"
cat > out/firmware/build-meta.json <<EOF
{
  "host_arch": "${HOST_ARCH}",
  "target": "aarch64-linux-gnu",
  "commit": "${GIT_SHA}",
  "note": "firmware is for the board, not to run on the CI PC"
}
EOF
echo "host(编译机)=${HOST_ARCH}  target=aarch64  commit=${GIT_SHA}"
cat out/firmware/build-meta.json
echo

echo "========== 2) 交叉编译（产出给板端，不在 PC 上跑） =========="
FW="out/firmware/fw-${GIT_SHA}.bin"
# Demo 用静态链出的 ARM64 ELF 假装固件镜像；产线可能是 .img / .swu / 厂家格式
aarch64-linux-gnu-gcc -static -O2 -o "${FW}" hello.c
file "${FW}"
sha256sum "${FW}" | tee "out/firmware/fw-${GIT_SHA}.sha256"
echo

echo "========== 3) 本 Job 结束：制品留在 out/firmware/ =========="
ls -la out/firmware/
echo
echo "下一步不在本容器里执行固件：上传到 HTTP 制品库 → 板端下载安装测试。"
