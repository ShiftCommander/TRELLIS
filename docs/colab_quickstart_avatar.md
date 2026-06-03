# Colab Quickstart (TRELLIS Avatar 3D Fallback)

Use this only as a fallback/benchmark. The primary Colab path is [colab_hunyuan3d_avatar.ipynb](</Users/tim/Code environments/TRELLIS/notebooks/colab_hunyuan3d_avatar.ipynb>).

## 1) Démarrer
1. Ouvre [Google Colab](https://colab.research.google.com/).
2. Passe le runtime en `GPU`.
3. Upload `avatar-man-1.png` avec la cellule du notebook.

## 2) Lancer
Utilise [colab_trellis_avatar.ipynb](</Users/tim/Code environments/TRELLIS/notebooks/colab_trellis_avatar.ipynb>) ou lance ces commandes dans Colab:

```bash
cd /content
rm -rf TRELLIS
git clone --recurse-submodules https://github.com/ShiftCommander/TRELLIS.git
cd TRELLIS
python3 -m pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
. ./setup.sh --basic --demo --xformers --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True ATTN_BACKEND=xformers SKIP_PREFLIGHT=1 ./scripts/run_avatar_pipeline.sh \
  "/content/avatar-man-1.png" \
  "/content/outputs/avatar-man-1" \
  1024
```

Commence avec `1024` sur GPU T4. Si ça passe et que tu as assez de VRAM, relance ensuite avec `2048`.

## 3) Récupérer
Le zip final sera ici:
```bash
/content/outputs/avatar-man-1/avatar-man-1_delivery.zip
```

Après téléchargement sur le Mac, vérifie le bundle:
```bash
cd "/Users/tim/Code environments/TRELLIS"
python3 scripts/review_avatar_delivery.py --bundle "/chemin/vers/avatar-man-1_delivery.zip"
```
