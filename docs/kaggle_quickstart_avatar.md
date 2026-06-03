# Kaggle Quickstart (Avatar 3D)

## But
Produire un bundle `.zip` contenant un GLB 3D depuis `avatar-man-1.png`.

Le chemin recommande pour Kaggle est maintenant Hunyuan3D, car il est plus leger que TRELLIS sur GPU T4 et gere mieux la generation shape + texture.

## Option recommandee: Hunyuan3D embedded
Utilise [kaggle_hunyuan3d_avatar_embedded.ipynb](</Users/tim/Code environments/TRELLIS/notebooks/kaggle_hunyuan3d_avatar_embedded.ipynb>).

Ce notebook embarque directement `assets/custom/avatar-man-1.png`, donc il ne depend pas d'un upload d'image Kaggle. Il telecharge le repo Hunyuan3D au runtime, installe les dependances, genere la forme avec `Hunyuan3D-2mini`, puis tente la texture avec `Hunyuan3D-Paint`.

Reglages Kaggle:
1. `Accelerator: GPU`
2. `Internet: ON`
3. `Run All`

Sortie attendue:
```bash
/kaggle/working/outputs/avatar-man-1-hunyuan/avatar-man-1_hunyuan_delivery.zip
```

Le notebook echoue volontairement si `texture_status != PASS`, afin de ne pas confondre un mesh non texture avec une livraison complete.

## Option fallback: TRELLIS

## 1) Préparer Kaggle
1. Crée un dataset Kaggle avec l'image `avatar-man-1.png`.
2. Ouvre un notebook avec `Accelerator: GPU` et `Internet: ON`.
3. Ajoute ce dataset au notebook.

Le chemin image attendu ressemble à:
```bash
/kaggle/input/avatar-man/avatar-man-1.png
```

## 2) Lancer
Utilise [kaggle_trellis_avatar.ipynb](</Users/tim/Code environments/TRELLIS/notebooks/kaggle_trellis_avatar.ipynb>) ou lance ces commandes dans une cellule:

```bash
cd /kaggle/working
rm -rf TRELLIS
git clone --recurse-submodules https://github.com/ShiftCommander/TRELLIS.git
cd TRELLIS
python3 -m pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
. ./setup.sh --basic --demo --xformers --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True ATTN_BACKEND=xformers SKIP_PREFLIGHT=1 ./scripts/run_avatar_pipeline.sh \
  "/kaggle/input/avatar-man/avatar-man-1.png" \
  "/kaggle/working/outputs/avatar-man-1" \
  1024
```

Commence avec `1024` sur GPU T4. Si ça passe et que tu as assez de VRAM, relance ensuite avec `2048`.

## 3) Récupérer
Télécharge:
```bash
/kaggle/working/outputs/avatar-man-1/avatar-man-1_delivery.zip
```

Après téléchargement sur le Mac, vérifie le bundle:
```bash
cd "/Users/tim/Code environments/TRELLIS"
python3 scripts/review_avatar_delivery.py --bundle "/chemin/vers/avatar-man-1_delivery.zip"
```
