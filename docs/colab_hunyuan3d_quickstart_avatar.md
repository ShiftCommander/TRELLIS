# Colab Quickstart (Hunyuan3D Avatar)

## Use This First
Use [colab_hunyuan3d_avatar.ipynb](</Users/tim/Code environments/TRELLIS/notebooks/colab_hunyuan3d_avatar.ipynb>) for the primary avatar run on Colab.

This notebook targets Colab T4 by default:
- Hunyuan3D-2mini for shape generation.
- Hunyuan3D-Paint for texture generation.
- A zip bundle at `/content/outputs/avatar-man-1-hunyuan/avatar-man-1_hunyuan_delivery.zip`.

## When To Upgrade
If you have a higher VRAM GPU, use Hunyuan3D-2.1 PBR as the quality target.

Do not switch the default notebook to Hunyuan3D-2.1 for free Colab T4. It is better quality, but much heavier.

## Fallback
If Hunyuan produces a poor shape, run TRELLIS separately with [colab_trellis_avatar.ipynb](</Users/tim/Code environments/TRELLIS/notebooks/colab_trellis_avatar.ipynb>) and compare the GLB candidates.
