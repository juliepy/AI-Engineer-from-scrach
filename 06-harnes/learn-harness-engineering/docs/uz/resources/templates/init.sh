#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Bu buyruqlarni loyihangizdagi haqiqiy buyruqlar bilan almashtiring.
INSTALL_CMD=(npm install)
VERIFY_CMD=(npm test)
START_CMD=(npm run dev)

echo "==> Ishchi katalog (Working directory): $PWD"
echo "==> Bogʻliqliklarni oʻrnatish (Syncing dependencies)"
"${INSTALL_CMD[@]}"

echo "==> Bazaviy tekshiruvni ishga tushirish (Running baseline verification)"
"${VERIFY_CMD[@]}"

echo "==> Ishga tushirish buyrugʻi (Startup command)"
printf '    %q' "${START_CMD[@]}"
printf '\n'

if [ "${RUN_START_COMMAND:-0}" = "1" ]; then
  echo "==> Ilovani ishga tushirish (Starting the app)"
  exec "${START_CMD[@]}"
fi

echo "Agar init.sh ilovani toʻgʻridan-toʻgʻri ishga tushirishini xohlasangiz, RUN_START_COMMAND=1 qilib bering."
