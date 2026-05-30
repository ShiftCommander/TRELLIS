# Kaggle Quickstart (TRELLIS Avatar 3D)

## But
Produire:
- `avatar-man-1_final.glb` (ou `avatar-man-1_final_raw.glb` si Blender indisponible)
- textures PBR (`baseColor`, `normal`, `roughness`)
- QA (`comparison_board.png`, `qa_summary.json`, `acceptance_report.json`)
- bundle final `avatar-man-1_delivery.zip`

## 1) Préparer l'image source sur Kaggle
1. Ouvre Kaggle -> `Datasets` -> `New Dataset`.
2. Upload ton image: `avatar-man-1.png`.
3. Publie le dataset (même privé).
4. Note le chemin final, ex: `/kaggle/input/avatar-man/avatar-man-1.png`.

## 2) Lancer le notebook prêt à l'emploi
1. Ouvre `Code` -> `New Notebook`.
2. `Settings`:
- Accelerator: `GPU`
- Internet: `ON`
3. Ajoute ton dataset image via `Add data`.
4. Copie/colle le contenu de [notebooks/kaggle_trellis_avatar.ipynb](/Users/tim/Code environments/TRELLIS/notebooks/kaggle_trellis_avatar.ipynb) (ou upload ce notebook).
5. Mets la bonne valeur de `INPUT_IMAGE`.
6. Exécute toutes les cellules.

## 3) Récupérer les livrables
À la fin, télécharge depuis le panneau `Files`:
- `/kaggle/working/outputs/avatar-man-1/avatar-man-1_delivery.zip`

Si le zip n'existe pas, télécharge:
- `/kaggle/working/outputs/avatar-man-1/`

## 4) Alternative script (sans notebook)
Tu peux exécuter directement:
```bash
bash scripts/kaggle_run_avatar.sh "/kaggle/input/avatar-man/avatar-man-1.png"
```

## Notes
- Kaggle gratuit peut interrompre les sessions GPU ou limiter le quota.
- Si un run échoue pour quota/VRAM, relance avec `TEXTURE_SIZE=1024` puis remonte à `2048`.
