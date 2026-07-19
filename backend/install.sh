#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "${BIN_DIR}"

ln -sf "${SCRIPT_DIR}/k8s-sense" "${BIN_DIR}/k8s-sense"

echo "Installed k8s-sense to ${BIN_DIR}"
echo "Make sure ${BIN_DIR} is on your PATH."
