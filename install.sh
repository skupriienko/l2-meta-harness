#!/usr/bin/env bash
# One-liner installer for l2-meta-harness
set -euo pipefail

echo "==> Installing l2-meta-harness in editable mode..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo "==> Verifying installation of meta-harness..."
meta-harness --help >/dev/null

echo "==> Installation complete! Run 'meta-harness --help' to get started."
