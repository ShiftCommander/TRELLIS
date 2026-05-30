#!/usr/bin/env python3
import argparse
import shutil
import json
import os
import sys
from pathlib import Path

import imageio
import numpy as np
from PIL import Image

os.environ.setdefault("SPCONV_ALGO", "native")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.utils import postprocessing_utils, render_utils


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def preprocess_input_image(src: Path, dst: Path, target_long_side: int = 1536) -> Path:
    ensure_dir(dst.parent)
    image = Image.open(src).convert("RGB")
    w, h = image.size
    long_side = max(w, h)
    if long_side < target_long_side:
        scale = target_long_side / long_side
        image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    image.save(dst)
    return dst


def render_turntable(video_frames, out_mp4: Path, fps: int = 24) -> None:
    imageio.mimsave(out_mp4, video_frames, fps=fps)


def resize_to_match(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = min(a.shape[0], b.shape[0])
    w = min(a.shape[1], b.shape[1])
    a_img = Image.fromarray(a).resize((w, h), Image.Resampling.BILINEAR)
    b_img = Image.fromarray(b).resize((w, h), Image.Resampling.BILINEAR)
    return np.asarray(a_img), np.asarray(b_img)


def detail_score(image: np.ndarray) -> float:
    gray = image.astype(np.float32).mean(axis=2)
    dx = np.abs(gray[:, 1:] - gray[:, :-1]).mean()
    dy = np.abs(gray[1:, :] - gray[:-1, :]).mean()
    return float(dx + dy)


def similarity_score(ref: np.ndarray, candidate: np.ndarray) -> float:
    ref_m, cand_m = resize_to_match(ref, candidate)
    ref_f = ref_m.astype(np.float32) / 255.0
    cand_f = cand_m.astype(np.float32) / 255.0
    mse = np.mean((ref_f - cand_f) ** 2)
    sim = 1.0 / (1.0 + float(mse))
    return sim


def generate_variant(
    pipeline,
    image: Image.Image,
    seed: int,
    out_dir: Path,
    texture_size: int,
    simplify: float,
    reference_np: np.ndarray,
):
    outputs = pipeline.run(
        image,
        seed=seed,
        formats=["gaussian", "mesh"],
        preprocess_image=False,
        sparse_structure_sampler_params={"steps": 12, "cfg_strength": 7.5},
        slat_sampler_params={"steps": 12, "cfg_strength": 3.0},
    )

    mesh = outputs["mesh"][0]
    gs = outputs["gaussian"][0]
    glb = postprocessing_utils.to_glb(gs, mesh, simplify=simplify, texture_size=texture_size, verbose=False)

    glb_path = out_dir / f"seed_{seed}.glb"
    mp4_path = out_dir / f"seed_{seed}_turntable.mp4"
    ply_path = out_dir / f"seed_{seed}.ply"

    mesh_video = render_utils.render_video(mesh, num_frames=120)["normal"]
    color_video = render_utils.render_video(gs, num_frames=120)["color"]
    color_mp4_path = out_dir / f"seed_{seed}_color.mp4"
    first_color_frame = np.asarray(color_video[0])
    sim = similarity_score(reference_np, first_color_frame)
    det = detail_score(first_color_frame)
    combined = sim * 0.8 + min(det / 50.0, 1.0) * 0.2

    glb.export(glb_path)
    render_turntable(mesh_video, mp4_path)
    render_turntable(color_video, color_mp4_path)
    gs.save_ply(ply_path)

    return {
        "seed": seed,
        "glb": str(glb_path),
        "turntable": str(mp4_path),
        "turntable_color": str(color_mp4_path),
        "gaussian": str(ply_path),
        "score_similarity": round(sim, 6),
        "score_detail": round(det, 6),
        "score_combined": round(combined, 6),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Avatar 3D generation pipeline with TRELLIS")
    parser.add_argument("--input-image", required=True, help="Absolute path to source image.")
    parser.add_argument("--workspace-copy", default="assets/custom/avatar-man-1.png")
    parser.add_argument("--out-dir", default="outputs/avatar-man-1")
    parser.add_argument("--seeds", default="11,23,37", help="Comma-separated seeds.")
    parser.add_argument("--texture-size", type=int, default=2048)
    parser.add_argument("--simplify", type=float, default=0.92)
    parser.add_argument("--model", default="microsoft/TRELLIS-image-large")
    parser.add_argument("--preferred-seed", type=int, default=23, help="Seed picked as default final candidate.")
    parser.add_argument(
        "--selection-mode",
        choices=["auto", "preferred"],
        default="auto",
        help="auto selects highest combined score; preferred uses preferred-seed.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_image = Path(args.input_image).expanduser().resolve()
    if not input_image.exists():
        raise FileNotFoundError(f"Input image not found: {input_image}")

    workspace_copy = Path(args.workspace_copy)
    output_dir = Path(args.out_dir)
    ensure_dir(output_dir)

    preprocessed_image_path = preprocess_input_image(input_image, workspace_copy)
    image = Image.open(preprocessed_image_path).convert("RGB")
    image_np = np.asarray(image)

    pipeline = TrellisImageTo3DPipeline.from_pretrained(args.model)
    try:
        pipeline.cuda()
    except Exception as exc:
        raise RuntimeError(
            "CUDA initialization failed. Run this pipeline on a Linux NVIDIA GPU machine with TRELLIS deps installed."
        ) from exc

    variant_dir = output_dir / "variants"
    ensure_dir(variant_dir)

    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    results = []
    for seed in seeds:
        seed_dir = variant_dir / f"seed_{seed}"
        ensure_dir(seed_dir)
        results.append(generate_variant(pipeline, image, seed, seed_dir, args.texture_size, args.simplify, image_np))

    if args.selection_mode == "auto":
        selected_seed = max(results, key=lambda r: r["score_combined"])["seed"]
    else:
        selected_seed = args.preferred_seed if args.preferred_seed in seeds else seeds[0]
    selected = next(r for r in results if r["seed"] == selected_seed)
    final_glb = output_dir / "avatar-man-1_final_raw.glb"
    final_turntable = output_dir / "avatar-man-1_turntable_raw.mp4"

    shutil.copy2(selected["glb"], final_glb)
    shutil.copy2(selected["turntable"], final_turntable)

    manifest = {
        "input_image": str(input_image),
        "workspace_copy": str(preprocessed_image_path),
        "texture_size": args.texture_size,
        "simplify": args.simplify,
        "seeds": seeds,
        "selection_mode": args.selection_mode,
        "preferred_seed": args.preferred_seed,
        "selected_seed": selected_seed,
        "selected_score_combined": selected["score_combined"],
        "final_raw_glb": str(final_glb),
        "final_raw_turntable": str(final_turntable),
        "variants": results,
    }
    with open(output_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
