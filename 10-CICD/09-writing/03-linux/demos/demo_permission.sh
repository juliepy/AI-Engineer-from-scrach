#!/bin/bash
# 权限演示：创建文件 → chmod/stat → 无执行位失败 → 加上执行位
set -euo pipefail

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
cd "$tmpdir"

echo "=== 1) 写脚本但不给执行位 ==="
cat > hello.sh <<'EOF'
#!/bin/bash
echo "hello from $0"
EOF
chmod 644 hello.sh
stat -c 'mode=%a owner=%U:%G name=%n' hello.sh

echo
echo "=== 2) 直接 ./ 应失败 ==="
set +e
./hello.sh
code=$?
set -e
echo "exit=$code (期望非 0)"

echo
echo "=== 3) chmod u+x 后再跑 ==="
chmod u+x hello.sh
stat -c 'mode=%a name=%n' hello.sh
./hello.sh

echo
echo "=== 4) 目录缺 x 无法进入 ==="
mkdir nest
echo x > nest/file.txt
chmod 600 nest
set +e
ls nest 2>&1 | head -2
set -e
chmod u+x nest
echo "after +x:" $(ls nest)

echo
echo "OK — 对照 03-权限.md"
