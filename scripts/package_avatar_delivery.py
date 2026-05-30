#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


def must_exist(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    if path.is_file() and path.stat().st_size == 0:
        raise RuntimeError(f"Empty {label}: {path}")


def copy_if_exists(src: Path, dst: Path):
    if src.exists() and src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main():
    parser = argparse.ArgumentParser(description="Package avatar outputs into a delivery bundle.")
    parser.add_argument("--out-dir", default="outputs/avatar-man-1")
    parser.add_argument("--bundle-name", default="avatar-man-1_delivery")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    qa_dir = out_dir / "qa"
    manifest = out_dir / "manifest.json"
    acceptance = qa_dir / "acceptance_report.json"
    final_glb = out_dir / "avatar-man-1_final.glb"
    raw_glb = out_dir / "avatar-man-1_final_raw.glb"
    raw_turntable = out_dir / "avatar-man-1_turntable_raw.mp4"
    qa_board = qa_dir / "comparison_board.png"
    qa_summary = qa_dir / "qa_summary.json"
    preflight = qa_dir / "preflight_report.json"
    tex_dir = out_dir / "textures"

    must_exist(manifest, "manifest")
    must_exist(acceptance, "acceptance report")
    report = json.loads(acceptance.read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise RuntimeError("Acceptance report is not PASS. Refusing to package delivery bundle.")

    bundle_root = out_dir / args.bundle_name
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True, exist_ok=True)

    copy_if_exists(manifest, bundle_root / "manifest.json")
    copy_if_exists(acceptance, bundle_root / "qa/acceptance_report.json")
    copy_if_exists(qa_board, bundle_root / "qa/comparison_board.png")
    copy_if_exists(qa_summary, bundle_root / "qa/qa_summary.json")
    copy_if_exists(preflight, bundle_root / "qa/preflight_report.json")
    copy_if_exists(raw_turntable, bundle_root / "preview/avatar-man-1_turntable_raw.mp4")

    if final_glb.exists():
        copy_if_exists(final_glb, bundle_root / "model/avatar-man-1_final.glb")
        copy_if_exists(tex_dir / "baseColor.png", bundle_root / "textures/baseColor.png")
        copy_if_exists(tex_dir / "normal.png", bundle_root / "textures/normal.png")
        copy_if_exists(tex_dir / "roughness.png", bundle_root / "textures/roughness.png")
        selected_model = "model/avatar-man-1_final.glb"
    else:
        copy_if_exists(raw_glb, bundle_root / "model/avatar-man-1_final_raw.glb")
        selected_model = "model/avatar-man-1_final_raw.glb"

    readme = (
        "# Avatar Delivery Bundle\n\n"
        f"- Source output dir: `{out_dir}`\n"
        f"- Selected model: `{selected_model}`\n"
        "- Includes QA artifacts and acceptance report.\n"
    )
    (bundle_root / "README.md").write_text(readme, encoding="utf-8")

    archive_base = out_dir / args.bundle_name
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=str(bundle_root))

    summary = {
        "status": "PASS",
        "bundle_dir": str(bundle_root),
        "bundle_zip": str(archive_path),
        "selected_model": selected_model,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
