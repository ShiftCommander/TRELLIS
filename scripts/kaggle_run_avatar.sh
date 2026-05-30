#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/kaggle_run_avatar.sh "/kaggle/input/<dataset>/avatar-man-1.png"
# Optional env:
#   TRELLIS_REPO_URL (default: https://github.com/microsoft/TRELLIS.git)
#   TRELLIS_BRANCH   (default: main)
#   OUT_DIR          (default: /kaggle/working/outputs/avatar-man-1)
#   TEXTURE_SIZE     (default: 2048)
#   SKIP_PREFLIGHT   (default: 1 on Kaggle)

INPUT_IMAGE="${1:-}"
if [[ -z "$INPUT_IMAGE" ]]; then
  echo "Missing input image path."
  echo "Example: bash scripts/kaggle_run_avatar.sh \"/kaggle/input/avatar/avatar-man-1.png\""
  exit 1
fi

TRELLIS_REPO_URL="${TRELLIS_REPO_URL:-https://github.com/microsoft/TRELLIS.git}"
TRELLIS_BRANCH="${TRELLIS_BRANCH:-main}"
OUT_DIR="${OUT_DIR:-/kaggle/working/outputs/avatar-man-1}"
TEXTURE_SIZE="${TEXTURE_SIZE:-2048}"
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-1}"

WORK_ROOT="/kaggle/working"
REPO_DIR="$WORK_ROOT/TRELLIS"

echo "[1/5] Clone TRELLIS"
rm -rf "$REPO_DIR"
git clone --recurse-submodules --branch "$TRELLIS_BRANCH" "$TRELLIS_REPO_URL" "$REPO_DIR"
cd "$REPO_DIR"

echo "[2/5] Install dependencies"
# Kaggle usually has no conda. Use setup without --new-env.
. ./setup.sh --demo --xformers --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast || true
python3 -m pip install --upgrade pip
python3 -m pip install imageio pillow numpy

echo "[3/5] Sync custom pipeline scripts from workspace copy if present"
if [[ -d /kaggle/input/trellis-custom-scripts ]]; then
  cp -r /kaggle/input/trellis-custom-scripts/* "$REPO_DIR"/
fi

echo "[4/5] Run avatar pipeline"
chmod +x scripts/*.sh || true
SKIP_PREFLIGHT="$SKIP_PREFLIGHT" ./scripts/run_avatar_pipeline.sh "$INPUT_IMAGE" "$OUT_DIR" "$TEXTURE_SIZE"

echo "[5/5] Collect outputs"
mkdir -p /kaggle/working/final_delivery
cp -r "$OUT_DIR" /kaggle/working/final_delivery/
if [[ -f "$OUT_DIR/avatar-man-1_delivery.zip" ]]; then
  cp "$OUT_DIR/avatar-man-1_delivery.zip" /kaggle/working/final_delivery/
fi

echo "Done. Files available in /kaggle/working/final_delivery"
