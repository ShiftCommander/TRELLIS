#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

INPUT_IMAGE="${1:-/Users/tim/Desktop/avatar-man-1 (1).png}"
OUT_DIR="${2:-outputs/avatar-man-1}"
TEXTURE_SIZE="${3:-2048}"
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-0}"

mkdir -p assets/custom "$OUT_DIR/textures"

PYTHON_BIN="python3"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

if [[ "$SKIP_PREFLIGHT" != "1" ]]; then
  "$PYTHON_BIN" scripts/preflight_avatar_gpu.py
fi

"$PYTHON_BIN" scripts/avatar_pipeline.py \
  --input-image "$INPUT_IMAGE" \
  --workspace-copy "assets/custom/avatar-man-1.png" \
  --out-dir "$OUT_DIR" \
  --seeds "11,23,37" \
  --preferred-seed 23 \
  --texture-size "$TEXTURE_SIZE" \
  --simplify 0.92

RAW_GLB="$OUT_DIR/avatar-man-1_final_raw.glb"
FINAL_GLB="$OUT_DIR/avatar-man-1_final.glb"
TEX_DIR="$OUT_DIR/textures"

if command -v blender >/dev/null 2>&1; then
  blender -b -P scripts/blender_cleanup_bake.py -- \
    --input-glb "$RAW_GLB" \
    --out-glb "$FINAL_GLB" \
    --tex-dir "$TEX_DIR" \
    --texture-size "$TEXTURE_SIZE"
else
  echo "Blender not found in PATH; skipping cleanup bake."
fi

SELECTED_COLOR_TURNTABLE="$("$PYTHON_BIN" -c 'import json,sys; d=json.load(open(sys.argv[1])); s=d["selected_seed"]; v=next(x for x in d["variants"] if x["seed"]==s); print(v["turntable_color"])' "$OUT_DIR/manifest.json")"
SOURCE_IMAGE_IN_MANIFEST="$("$PYTHON_BIN" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["workspace_copy"])' "$OUT_DIR/manifest.json")"

"$PYTHON_BIN" scripts/generate_avatar_qa.py \
  --source-image "$SOURCE_IMAGE_IN_MANIFEST" \
  --turntable-color "$SELECTED_COLOR_TURNTABLE" \
  --out-dir "$OUT_DIR"

"$PYTHON_BIN" scripts/validate_avatar_outputs.py --out-dir "$OUT_DIR"

"$PYTHON_BIN" scripts/audit_avatar_acceptance.py \
  --out-dir "$OUT_DIR" \
  --min-selected-seed-score 0.82 \
  --min-best-view-score 0.82

"$PYTHON_BIN" scripts/package_avatar_delivery.py \
  --out-dir "$OUT_DIR" \
  --bundle-name "avatar-man-1_delivery"
