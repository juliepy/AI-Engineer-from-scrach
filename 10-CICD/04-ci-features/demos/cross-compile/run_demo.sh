#!/usr/bin/env bash
# 固件 CI 迷你链路：Docker 交叉编译 → 上传 HTTP →（板端安装测试仅说明）
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8765}"
mkdir -p out/firmware http_repo

# 选择 docker 命令：普通用户需在 docker 组，否则用 sudo
# 覆盖示例：DOCKER_CMD="sudo docker" ./run_demo.sh
if [[ -n "${DOCKER_CMD:-}" ]]; then
  # shellcheck disable=SC2206
  DOCKER=($DOCKER_CMD)
elif docker info >/dev/null 2>&1; then
  DOCKER=(docker)
elif sudo -n docker info >/dev/null 2>&1; then
  DOCKER=(sudo docker)
  echo "提示：当前用 sudo docker。长期修复见下方。"
else
  cat <<'EOF'
ERROR: 无法访问 Docker（permission denied on /var/run/docker.sock）

本次先跑通（任选）：
  DOCKER_CMD="sudo docker" ./run_demo.sh
  # 或： sudo ./run_demo.sh

长期修复（做一次，然后重开终端）：
  sudo groupadd -f docker
  sudo usermod -aG docker "$USER"
  newgrp docker
  docker info
EOF
  exit 1
fi

echo "==> [1/3] docker build：工具链镜像"
"${DOCKER[@]}" build -t ci-cross-demo:local .

echo "==> [2/3] docker run：checkout 元数据 + 交叉编译（不在 PC 跑固件）"
"${DOCKER[@]}" run --rm \
  -v "$(pwd):/src" \
  -w /src \
  ci-cross-demo:local \
  bash /src/scripts/build_in_container.sh

echo "==> [3/3] 启动 HTTP 制品库并上传"
python3 scripts/http_repo_server.py --root http_repo --port "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 1
python3 scripts/upload_firmware.py --base-url "http://127.0.0.1:${PORT}"

echo
echo "可用浏览器或 curl 核对："
echo "  curl -I http://127.0.0.1:${PORT}/$(ls out/firmware/fw-*.bin | xargs -n1 basename | tail -1)"
