#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This bootstrap script is intended for Linux GPU hosts."
  exit 1
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "conda is required. Install Miniconda first."
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

. ./setup.sh --new-env --demo --xformers --flash-attn --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast
eval "$(conda shell.bash hook)"
conda activate trellis
python -m pip install --upgrade pip
python -m pip install imageio pillow numpy

python scripts/preflight_avatar_gpu.py || true

echo "Bootstrap complete. Run:"
echo "./scripts/run_avatar_pipeline.sh \"/abs/path/to/avatar.png\" \"outputs/avatar-man-1\" 2048"
