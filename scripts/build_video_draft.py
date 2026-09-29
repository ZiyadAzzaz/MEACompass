"""Build the silent, timing-locked MEACompass competition-video draft.

The input directory must contain the 12 rendered competition-deck slides named
``slide-01.png`` through ``slide-12.png``.  The draft deliberately has no audio:
the final submission requires the author's English narration and subtitle
retiming against that real voice track.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


FPS = 30
WIDTH = 1920
HEIGHT = 1080

# Matches docs/video_shotlist.md exactly. Slide 10 is the authentic public-demo
# capture; the remaining frames are rendered directly from the public deck.
SEGMENTS = [
    (1, 18),
    (10, 40),
    (4, 14),
    (5, 18),
    (6, 35),
    (7, 19),
    (8, 21),
    (9, 35),
    (10, 30),
    (11, 32),
    (12, 23),
]


def _letterbox(image: np.ndarray) -> np.ndarray:
    scale = min(WIDTH / image.shape[1], HEIGHT / image.shape[0])
    size = (round(image.shape[1] * scale), round(image.shape[0] * scale))
    resized = cv2.resize(image, size, interpolation=cv2.INTER_LANCZOS4)
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    x = (WIDTH - resized.shape[1]) // 2
    y = (HEIGHT - resized.shape[0]) // 2
    canvas[y : y + resized.shape[0], x : x + resized.shape[1]] = resized
    return canvas


def build(slides_dir: Path, output: Path) -> None:
    frames: dict[int, np.ndarray] = {}
    for slide_number, _ in SEGMENTS:
        if slide_number in frames:
            continue
        path = slides_dir / f"slide-{slide_number:02d}.png"
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Required rendered slide is missing: {path}")
        frames[slide_number] = _letterbox(image)

    output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT)
    )
    if not writer.isOpened():
        raise RuntimeError("OpenCV could not initialize the free local MP4 writer")

    try:
        for slide_number, seconds in SEGMENTS:
            frame = frames[slide_number]
            for _ in range(seconds * FPS):
                writer.write(frame)
    finally:
        writer.release()

    if sum(seconds for _, seconds in SEGMENTS) != 285:
        raise AssertionError("The registered draft timeline must remain exactly 4:45")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slides-dir", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/media/MEACompass_Competition_Video_DRAFT_SILENT.mp4"),
    )
    args = parser.parse_args()
    build(args.slides_dir, args.output)


if __name__ == "__main__":
    main()
