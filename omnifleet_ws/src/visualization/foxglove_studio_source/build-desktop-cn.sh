#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
node_home="${NODE_HOME:-$HOME/.local/node-v20.20.2-linux-arm64}"
export PATH="$node_home/bin:$PATH"
export ELECTRON_MIRROR="${ELECTRON_MIRROR:-https://npmmirror.com/mirrors/electron/}"
export ELECTRON_BUILDER_BINARIES_MIRROR="${ELECTRON_BUILDER_BINARIES_MIRROR:-https://gh-proxy.com/https://github.com/electron-userland/electron-builder-binaries/releases/download/}"
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

cd "$repo_dir"
node scripts/audit-zh-translations.mjs
corepack yarn install --immutable
corepack yarn web:build:prod
npm --prefix desktop-cn ci --no-audit --no-fund
npm --prefix desktop-cn run dist:arm64
