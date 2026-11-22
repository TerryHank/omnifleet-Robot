#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARCH="$(uname -m)"

case "${ARCH}" in
  x86_64|amd64)
    ARCHIVE="${PKG_DIR}/vendor/MVS-5.0.1_x86_64_20260512.tar.gz"
    OUTER_DIR="MVS-5.0.1_x86_64_20260512"
    ;;
  aarch64|arm64)
    ARCHIVE="${PKG_DIR}/vendor/MVS-5.0.1_aarch64_20260512.tar.gz"
    OUTER_DIR="MVS-5.0.1_aarch64_20260512"
    ;;
  *)
    echo "Unsupported architecture for bundled MVS SDK: ${ARCH}" >&2
    exit 2
    ;;
esac

if [[ ! -f "${ARCHIVE}" ]]; then
  echo "Archive not found: ${ARCHIVE}" >&2
  exit 3
fi

WORK_DIR="$(mktemp -d)"
cleanup() {
  if [[ "${KEEP_MVS_INSTALLER_TMP:-0}" != "1" ]]; then
    rm -rf "${WORK_DIR}"
  else
    echo "Kept installer temp directory: ${WORK_DIR}"
  fi
}
trap cleanup EXIT

tar -xzf "${ARCHIVE}" -C "${WORK_DIR}"
INSTALLER_DIR="${WORK_DIR}/${OUTER_DIR}"

if [[ ! -f "${INSTALLER_DIR}/setup.sh" ]]; then
  echo "setup.sh not found in ${INSTALLER_DIR}" >&2
  exit 4
fi

echo "Installing MVS system runtime from ${ARCHIVE}"
sudo env MVS_INSTALLER_DIR="${INSTALLER_DIR}" bash -lc 'cd "${MVS_INSTALLER_DIR}" && source ./setup.sh'
echo "MVS system runtime installation finished."
