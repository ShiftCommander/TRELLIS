#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def must_exist(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    if path.is_file() and path.stat().st_size == 0:
        raise RuntimeError(f"Empty {label}: {path}")


def main():
    parser = argparse.ArgumentParser(description="Validate avatar pipeline outputs.")
    parser.add_argument("--out-dir", default="outputs/avatar-man-1")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    manifest = out_dir / "manifest.json"
    raw_glb = out_dir / "avatar-man-1_final_raw.glb"
    raw_mp4 = out_dir / "avatar-man-1_turntable_raw.mp4"
    final_glb = out_dir / "avatar-man-1_final.glb"
    tex_dir = out_dir / "textures"
    tex_base = tex_dir / "baseColor.png"
    tex_normal = tex_dir / "normal.png"
    tex_rough = tex_dir / "roughness.png"
    qa_dir = out_dir / "qa"
    qa_board = qa_dir / "comparison_board.png"
    qa_summary = qa_dir / "qa_summary.json"

    must_exist(out_dir, "output directory")
    must_exist(manifest, "manifest.json")
    must_exist(raw_glb, "raw final GLB")
    must_exist(raw_mp4, "raw turntable")

    with manifest.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "variants" not in data or len(data["variants"]) < 3:
        raise RuntimeError("Expected at least 3 generated variants in manifest.")
    if "selected_seed" not in data:
        raise RuntimeError("Missing selected_seed in manifest.")
    if "selection_mode" not in data:
        raise RuntimeError("Missing selection_mode in manifest.")

    required_variant_fields = {"seed", "glb", "turntable", "turntable_color", "score_combined"}
    for variant in data["variants"]:
        missing = required_variant_fields - set(variant.keys())
        if missing:
            raise RuntimeError(f"Variant missing fields {sorted(missing)}: {variant}")

    if final_glb.exists():
        must_exist(final_glb, "final baked GLB")
    if tex_base.exists() or tex_normal.exists() or tex_rough.exists():
        must_exist(tex_base, "baseColor texture")
        must_exist(tex_normal, "normal texture")
        must_exist(tex_rough, "roughness texture")
    if qa_dir.exists():
        must_exist(qa_board, "QA board")
        must_exist(qa_summary, "QA summary")

    print("Validation OK")
    print(f"Manifest: {manifest}")
    print(f"Raw GLB: {raw_glb}")
    print(f"Raw turntable: {raw_mp4}")
    if final_glb.exists():
        print(f"Final GLB: {final_glb}")
    if qa_summary.exists():
        print(f"QA summary: {qa_summary}")


if __name__ == "__main__":
    main()
