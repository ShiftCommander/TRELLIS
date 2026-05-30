#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import imageio
import numpy as np
from PIL import Image, ImageOps, ImageDraw


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resize_to(a: np.ndarray, target_wh: tuple[int, int]) -> np.ndarray:
    img = Image.fromarray(a).resize(target_wh, Image.Resampling.BILINEAR)
    return np.asarray(img)


def similarity_score(ref: np.ndarray, candidate: np.ndarray) -> float:
    h = min(ref.shape[0], candidate.shape[0])
    w = min(ref.shape[1], candidate.shape[1])
    ref_r = resize_to(ref, (w, h)).astype(np.float32) / 255.0
    cand_r = resize_to(candidate, (w, h)).astype(np.float32) / 255.0
    mse = np.mean((ref_r - cand_r) ** 2)
    return 1.0 / (1.0 + float(mse))


def load_frames(video_path: Path) -> list[np.ndarray]:
    reader = imageio.get_reader(str(video_path))
    frames = []
    for frame in reader:
        frames.append(np.asarray(frame))
    reader.close()
    if not frames:
        raise RuntimeError(f"No frames found in video: {video_path}")
    return frames


def make_labeled_tile(img: np.ndarray, label: str, size=(512, 512)) -> Image.Image:
    tile = Image.fromarray(resize_to(img, size))
    tile = ImageOps.pad(tile, size, method=Image.Resampling.BILINEAR, color=(245, 245, 245))
    draw = ImageDraw.Draw(tile)
    draw.rectangle([0, size[1] - 36, size[0], size[1]], fill=(0, 0, 0))
    draw.text((12, size[1] - 28), label, fill=(255, 255, 255))
    return tile


def main():
    parser = argparse.ArgumentParser(description="Generate QA board for avatar pipeline outputs.")
    parser.add_argument("--source-image", required=True)
    parser.add_argument("--turntable-color", required=True)
    parser.add_argument("--out-dir", default="outputs/avatar-man-1")
    args = parser.parse_args()

    source_path = Path(args.source_image).resolve()
    turntable_path = Path(args.turntable_color).resolve()
    out_dir = Path(args.out_dir).resolve()
    qa_dir = out_dir / "qa"
    ensure_dir(qa_dir)

    src = np.asarray(Image.open(source_path).convert("RGB"))
    frames = load_frames(turntable_path)
    n = len(frames)
    idxs = {
        "front": 0,
        "three_quarter": max(1, n // 8),
        "profile": max(2, n // 4),
        "back_three_quarter": max(3, (3 * n) // 8),
    }

    records = []
    for name, idx in idxs.items():
        frame = frames[idx]
        frame_path = qa_dir / f"{name}.png"
        Image.fromarray(frame).save(frame_path)
        score = similarity_score(src, frame)
        records.append({"view": name, "frame_index": idx, "image": str(frame_path), "score": round(score, 6)})

    board_w, board_h = 512, 512
    board = Image.new("RGB", (board_w * 5, board_h), color=(255, 255, 255))
    board.paste(make_labeled_tile(src, "source", (board_w, board_h)), (0, 0))
    for i, rec in enumerate(records, start=1):
        img = np.asarray(Image.open(rec["image"]).convert("RGB"))
        label = f"{rec['view']} | sim={rec['score']:.4f}"
        board.paste(make_labeled_tile(img, label, (board_w, board_h)), (board_w * i, 0))
    board_path = qa_dir / "comparison_board.png"
    board.save(board_path)

    best = max(records, key=lambda r: r["score"])
    summary = {
        "source_image": str(source_path),
        "turntable_color": str(turntable_path),
        "views": records,
        "best_view": best,
        "board": str(board_path),
    }
    summary_path = qa_dir / "qa_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
