from __future__ import annotations

import subprocess
from pathlib import Path

from app.services.quality import trim_overlay

DATA_DIR = Path("data")
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def write_srt(lines: list[str], scene_duration: float, output: Path) -> None:
    def ts(value: float) -> str:
        hrs = int(value // 3600)
        mins = int((value % 3600) // 60)
        secs = int(value % 60)
        ms = int((value - int(value)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

    current = 0.0
    chunks = []
    for i, line in enumerate(lines, start=1):
        start = ts(current)
        end = ts(current + scene_duration)
        chunks.append(f"{i}\n{start} --> {end}\n{trim_overlay(line)}\n")
        current += scene_duration
    output.write_text("\n".join(chunks), encoding="utf-8")


def render_video(image_paths: list[str], overlays: list[str], output_name: str, music_path: str | None = None) -> tuple[str, str]:
    output_mp4 = EXPORT_DIR / f"{output_name}.mp4"
    srt_path = EXPORT_DIR / f"{output_name}.srt"
    scene_duration = max(1.2, 10 / max(1, len(image_paths)))

    concat_file = EXPORT_DIR / f"{output_name}_concat.txt"
    concat_lines = []
    for image in image_paths:
        concat_lines.append(f"file '{Path(image).resolve()}'")
        concat_lines.append(f"duration {scene_duration:.2f}")
    concat_file.write_text("\n".join(concat_lines), encoding="utf-8")
    write_srt(overlays, scene_duration, srt_path)

    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,"
        "zoompan=z='min(zoom+0.0009,1.1)':d=75:s=1080x1920:fps=30,"
        f"subtitles={srt_path.as_posix()}:force_style='Fontsize=16,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=3,Outline=2,MarginV=120'"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
    ]
    if music_path:
        cmd.extend(["-i", music_path])
    cmd.extend(
        [
            "-vf",
            vf,
            "-r",
            "30",
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            "-t",
            "10",
        ]
    )
    if music_path:
        cmd.extend(["-c:a", "aac", "-shortest"])
    else:
        cmd.extend(["-an"])
    cmd.append(str(output_mp4))

    subprocess.run(cmd, check=True, capture_output=True)
    return str(output_mp4), str(srt_path)
