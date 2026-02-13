from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

from PIL import Image


def repeated_words(lines: Iterable[str]) -> list[str]:
    words = []
    for line in lines:
        words.extend([w.lower() for w in line.split() if len(w) > 3])
    dupes = [w for w, c in Counter(words).items() if c > 2]
    return dupes


def trim_overlay(line: str, max_chars: int = 70) -> str:
    return line if len(line) <= max_chars else f"{line[: max_chars - 1].rstrip()}…"


def safe_area_check(lines: Iterable[str]) -> list[str]:
    warnings = []
    for line in lines:
        if len(line) > 70:
            warnings.append(f"Overlay too long and auto-trimmed: {line[:30]}...")
    return warnings


def low_res_images(image_paths: list[str], min_w: int = 1080, min_h: int = 1080) -> list[str]:
    bad = []
    for path in image_paths:
        try:
            with Image.open(path) as img:
                w, h = img.size
                if w < min_w or h < min_h:
                    bad.append(path)
        except Exception:
            bad.append(path)
    return bad


def pick_best_images(candidates: list[str], max_count: int = 8) -> list[str]:
    scored = []
    for path in candidates:
        p = Path(path)
        if not p.exists():
            continue
        try:
            with Image.open(path) as img:
                w, h = img.size
                scored.append((w * h, path))
        except Exception:
            continue
    scored.sort(reverse=True)
    return [p for _, p in scored[:max_count]]
