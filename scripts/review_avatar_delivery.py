#!/usr/bin/env python3
import argparse
import json
import shutil
import tempfile
from pathlib import Path


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_first(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def summarize_bundle(bundle_root: Path) -> dict:
    manifest = find_first([bundle_root / "manifest.json", bundle_root / "qa" / "manifest.json"])
    acceptance = find_first(
        [bundle_root / "qa" / "acceptance_report.json", bundle_root / "acceptance_report.json"]
    )
    qa_summary = find_first([bundle_root / "qa" / "qa_summary.json", bundle_root / "qa_summary.json"])

    final_glb = find_first(
        [
            bundle_root / "model" / "avatar-man-1_final.glb",
            bundle_root / "avatar-man-1_final.glb",
        ]
    )
    raw_glb = find_first(
        [
            bundle_root / "model" / "avatar-man-1_final_raw.glb",
            bundle_root / "avatar-man-1_final_raw.glb",
        ]
    )
    turntable = find_first(
        [
            bundle_root / "preview" / "avatar-man-1_turntable_raw.mp4",
            bundle_root / "avatar-man-1_turntable_raw.mp4",
        ]
    )
    base = find_first([bundle_root / "textures" / "baseColor.png", bundle_root / "baseColor.png"])
    normal = find_first([bundle_root / "textures" / "normal.png", bundle_root / "normal.png"])
    rough = find_first([bundle_root / "textures" / "roughness.png", bundle_root / "roughness.png"])
    board = find_first([bundle_root / "qa" / "comparison_board.png", bundle_root / "comparison_board.png"])

    out = {
        "bundle_root": str(bundle_root),
        "files": {
            "manifest": str(manifest) if manifest else None,
            "acceptance_report": str(acceptance) if acceptance else None,
            "qa_summary": str(qa_summary) if qa_summary else None,
            "final_glb": str(final_glb) if final_glb else None,
            "raw_glb": str(raw_glb) if raw_glb else None,
            "turntable": str(turntable) if turntable else None,
            "textures": {
                "baseColor": str(base) if base else None,
                "normal": str(normal) if normal else None,
                "roughness": str(rough) if rough else None,
            },
            "qa_board": str(board) if board else None,
        },
        "status": "UNKNOWN",
        "notes": [],
    }

    if manifest:
        data = read_json(manifest)
        out["selected_seed"] = data.get("selected_seed")
        out["selected_score_combined"] = data.get("selected_score_combined")
    else:
        out["notes"].append("manifest.json missing")

    if acceptance:
        a = read_json(acceptance)
        out["acceptance_status"] = a.get("status")
        out["acceptance_failures"] = a.get("failures", [])
        if a.get("status") == "PASS":
            out["status"] = "PASS"
        else:
            out["status"] = "FAIL"
    else:
        out["notes"].append("acceptance_report.json missing")

    if qa_summary:
        q = read_json(qa_summary)
        out["best_view_score"] = q.get("best_view", {}).get("score")
    else:
        out["notes"].append("qa_summary.json missing")

    if not final_glb and not raw_glb:
        out["status"] = "FAIL"
        out["notes"].append("No GLB model found")
    if not turntable:
        out["notes"].append("Turntable preview missing")
    if not board:
        out["notes"].append("QA board missing")

    if final_glb and not (base and normal and rough):
        out["notes"].append("Final GLB exists but one or more textures are missing")

    return out


def main():
    parser = argparse.ArgumentParser(description="Review an avatar delivery bundle (.zip or folder).")
    parser.add_argument("--bundle", required=True, help="Path to avatar-man-1_delivery.zip or extracted folder")
    parser.add_argument("--out-json", default="", help="Optional output report path")
    args = parser.parse_args()

    bundle = Path(args.bundle).resolve()
    if not bundle.exists():
        raise FileNotFoundError(f"Bundle path not found: {bundle}")

    cleanup_dir = None
    bundle_root = bundle
    if bundle.is_file() and bundle.suffix.lower() == ".zip":
        cleanup_dir = Path(tempfile.mkdtemp(prefix="avatar_bundle_"))
        shutil.unpack_archive(str(bundle), str(cleanup_dir))
        entries = [p for p in cleanup_dir.iterdir()]
        if len(entries) == 1 and entries[0].is_dir():
            bundle_root = entries[0]
        else:
            bundle_root = cleanup_dir

    report = summarize_bundle(bundle_root)
    text = json.dumps(report, indent=2)
    print(text)

    if args.out_json:
        Path(args.out_json).write_text(text + "\n", encoding="utf-8")

    if cleanup_dir:
        shutil.rmtree(cleanup_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
