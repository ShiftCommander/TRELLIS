#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSON file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_file(path: Path, label: str, failures: list[str]):
    if not path.exists():
        failures.append(f"Missing {label}: {path}")
        return
    if path.is_file() and path.stat().st_size == 0:
        failures.append(f"Empty {label}: {path}")


def main():
    parser = argparse.ArgumentParser(description="Acceptance audit for avatar 3D pipeline.")
    parser.add_argument("--out-dir", default="outputs/avatar-man-1")
    parser.add_argument("--min-best-view-score", type=float, default=0.82)
    parser.add_argument("--min-selected-seed-score", type=float, default=0.82)
    parser.add_argument("--strict-final-glb", action="store_true", help="Fail if baked final GLB is missing.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    manifest_path = out_dir / "manifest.json"
    qa_summary_path = out_dir / "qa" / "qa_summary.json"

    failures: list[str] = []
    check_file(manifest_path, "manifest", failures)
    check_file(qa_summary_path, "qa summary", failures)

    if failures:
        raise RuntimeError(" | ".join(failures))

    manifest = load_json(manifest_path)
    qa = load_json(qa_summary_path)

    selected_seed = manifest.get("selected_seed")
    variants = manifest.get("variants", [])
    selected_variant = next((v for v in variants if v.get("seed") == selected_seed), None)
    if selected_variant is None:
        failures.append(f"selected_seed {selected_seed} not found in manifest variants")

    selected_seed_score = float(selected_variant.get("score_combined", 0.0)) if selected_variant else 0.0
    best_view_score = float(qa.get("best_view", {}).get("score", 0.0))

    raw_glb = Path(manifest.get("final_raw_glb", out_dir / "avatar-man-1_final_raw.glb"))
    raw_turntable = Path(manifest.get("final_raw_turntable", out_dir / "avatar-man-1_turntable_raw.mp4"))
    final_glb = out_dir / "avatar-man-1_final.glb"
    base_tex = out_dir / "textures" / "baseColor.png"
    normal_tex = out_dir / "textures" / "normal.png"
    rough_tex = out_dir / "textures" / "roughness.png"
    board = out_dir / "qa" / "comparison_board.png"

    check_file(raw_glb, "raw GLB", failures)
    check_file(raw_turntable, "raw turntable", failures)
    check_file(board, "QA board", failures)

    if selected_seed_score < args.min_selected_seed_score:
        failures.append(
            f"Selected seed score too low: {selected_seed_score:.4f} < {args.min_selected_seed_score:.4f}"
        )
    if best_view_score < args.min_best_view_score:
        failures.append(f"Best QA view score too low: {best_view_score:.4f} < {args.min_best_view_score:.4f}")

    if final_glb.exists():
        check_file(final_glb, "final baked GLB", failures)
        check_file(base_tex, "baseColor texture", failures)
        check_file(normal_tex, "normal texture", failures)
        check_file(rough_tex, "roughness texture", failures)
    elif args.strict_final_glb:
        failures.append(f"Missing final baked GLB in strict mode: {final_glb}")

    report = {
        "out_dir": str(out_dir),
        "selected_seed": selected_seed,
        "selected_seed_score": round(selected_seed_score, 6),
        "best_view_score": round(best_view_score, 6),
        "thresholds": {
            "min_selected_seed_score": args.min_selected_seed_score,
            "min_best_view_score": args.min_best_view_score,
            "strict_final_glb": args.strict_final_glb,
        },
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }

    report_path = out_dir / "qa" / "acceptance_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
