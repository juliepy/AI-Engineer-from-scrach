# 固件 CI 迷你链路：Docker 交叉编译 → 上传 HTTP →（板端安装测试仅说明）
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Port = if ($env:PORT) { $env:PORT } else { 8765 }
New-Item -ItemType Directory -Force -Path out\firmware, http_repo | Out-Null

Write-Host "==> [1/3] docker build：工具链镜像" -ForegroundColor Cyan
docker build -t ci-cross-demo:local .

Write-Host "==> [2/3] docker run：checkout 元数据 + 交叉编译（不在 PC 跑固件）" -ForegroundColor Cyan
$here = (Get-Location).Path
docker run --rm -v "${here}:/src" -w /src ci-cross-demo:local bash /src/scripts/build_in_container.sh

Write-Host "==> [3/3] 启动 HTTP 制品库并上传" -ForegroundColor Cyan
$server = Start-Process -FilePath "python" -ArgumentList @(
    "scripts/http_repo_server.py", "--root", "http_repo", "--port", "$Port"
) -PassThru -WindowStyle Hidden
try {
    Start-Sleep -Seconds 1
    python scripts/upload_firmware.py --base-url "http://127.0.0.1:$Port"
} finally {
    if (-not $server.HasExited) { Stop-Process -Id $server.Id -Force }
}

Write-Host ""
Write-Host "Done. Firmware is on the HTTP repo for the board to download — not for running on the PC." -ForegroundColor Green
