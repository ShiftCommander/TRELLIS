# Avatar Pipeline Decision

## Decision
Use Hunyuan3D as the primary Colab pipeline for the avatar delivery goal.

Keep TRELLIS as a separate fallback and comparison pipeline.

## Why Hunyuan3D Is Primary
- The current goal is a textured GLB avatar from one image.
- Hunyuan3D is built as a two-stage mesh + texture pipeline.
- Hunyuan3D-2mini is the best default for Colab T4 because it is lighter.
- Hunyuan3D-2.1 PBR is the quality upgrade path, but it needs substantially more VRAM.

## Why TRELLIS Stays
- TRELLIS is already integrated in this repo with QA, acceptance, and packaging.
- It can produce backup geometry/variants when Hunyuan output is weak.
- It should remain isolated in its own notebook and scripts.

## Separation Rule
Do not paste TRELLIS cells into a Hunyuan notebook or Hunyuan cells into a TRELLIS notebook.

Use:
- `notebooks/colab_hunyuan3d_avatar.ipynb` for the primary Colab run.
- `notebooks/colab_trellis_avatar.ipynb` only as fallback/benchmark.
- `notebooks/kaggle_trellis_avatar.ipynb` only for TRELLIS on Kaggle.

## Practical Order
1. Run Hunyuan3D on Colab T4.
2. If texture fails, keep the shape GLB and retry texture on higher VRAM.
3. If shape fidelity is poor, run TRELLIS as a second candidate generator.
4. Compare results manually before accepting the final GLB.
