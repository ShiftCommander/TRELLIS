# Avatar 3D Pipeline Runbook

Pipeline choice is documented in [avatar_pipeline_decision.md](avatar_pipeline_decision.md).

This runbook executes the full plan for:
- Source image: `/Users/tim/Desktop/avatar-man-1 (1).png`
- High quality texture: `2048`
- Delivery: textured `GLB` + preview turntable

## 1) Prepare Linux GPU environment

Use a Linux machine with NVIDIA GPU (>=16 GB VRAM), CUDA toolchain, and Python 3.10+.
For free cloud runs, use the Kaggle or Colab quickstart instead of trying to run this on macOS.

From repo root (recommended):

```bash
./scripts/bootstrap_gpu_linux.sh
```

If `flash-attn` is not supported by the GPU, use xformers backend instead.
Preflight report is written to:
- `outputs/avatar-man-1/qa/preflight_report.json`

## 2) Run TRELLIS generation (3 variants, fixed seeds)

```bash
./scripts/run_avatar_pipeline.sh "/Users/tim/Desktop/avatar-man-1 (1).png" "outputs/avatar-man-1" 2048
```
If you already validated the machine and want to skip preflight:
```bash
SKIP_PREFLIGHT=1 ./scripts/run_avatar_pipeline.sh "/Users/tim/Desktop/avatar-man-1 (1).png" "outputs/avatar-man-1" 2048
```

This performs:
- source copy/preprocess to `assets/custom/avatar-man-1.png`
- generation for seeds `11, 23, 37`
- automatic best-seed selection from visual scoring (`selection_mode=auto`)
- raw exports under `outputs/avatar-man-1/variants/`
- selected candidate copied to:
  - `outputs/avatar-man-1/avatar-man-1_final_raw.glb`
  - `outputs/avatar-man-1/avatar-man-1_turntable_raw.mp4`
- manifest metadata: `outputs/avatar-man-1/manifest.json`
- QA board + summary:
  - `outputs/avatar-man-1/qa/comparison_board.png`
  - `outputs/avatar-man-1/qa/qa_summary.json`
- Acceptance audit:
  - `outputs/avatar-man-1/qa/acceptance_report.json` (`PASS` or `FAIL`)
- Delivery bundle (created only after audit `PASS`):
  - Folder: `outputs/avatar-man-1/avatar-man-1_delivery/`
  - Zip: `outputs/avatar-man-1/avatar-man-1_delivery.zip`
- output validation: `scripts/validate_avatar_outputs.py`

## 3) Blender cleanup, UV, bake, final export

If Blender is in PATH, `run_avatar_pipeline.sh` already triggers:

```bash
blender -b -P scripts/blender_cleanup_bake.py -- \
  --input-glb outputs/avatar-man-1/avatar-man-1_final_raw.glb \
  --out-glb outputs/avatar-man-1/avatar-man-1_final.glb \
  --tex-dir outputs/avatar-man-1/textures \
  --texture-size 2048
```

Produced files:
- `outputs/avatar-man-1/avatar-man-1_final.glb`
- `outputs/avatar-man-1/textures/baseColor.png`
- `outputs/avatar-man-1/textures/normal.png`
- `outputs/avatar-man-1/textures/roughness.png`

## 4) Validation checklist

- Shape: no major limb/pose artifacts.
- Texture: seams not obvious in medium shot.
- PBR response: cloth/leather/skin roughness separation looks plausible.
- Face fidelity: recognizable in front and 3/4 view.
- Final GLB opens without errors in Blender and web GLB viewers.
