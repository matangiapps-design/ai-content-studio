"""Generate and assemble the ODIA HERO film with WaveSpeed Wan 3.0.

Set WAVESPEED_API_KEY in the server environment. Paid provider generation is
performed only when this script is run. Optional narration/music/SRT assets can
be supplied at assembly time; no soundtrack is fabricated when absent.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from services.wan3_client import Wan3Client  # noqa: E402

CHARACTER = (
    "Biku: the exact same small white stickman hero, round white head, expressive black eyes, "
    "thin black arms and legs, bright red cape. Preserve exact proportions, face and cape."
)
STYLE = (
    "Cinematic 3D animated family film, Puri Odisha Jagannath Rath Yatra, respectful devotional atmosphere, "
    "colourful decorated traditional chariot and flags, expressive animation, natural cape motion, "
    "detailed environment, cinematic lighting, smooth camera movement. Stickman animation only, no live-action actors."
)
NEGATIVE = (
    "No character redesign, no missing red cape, no extra limbs, no distorted faces, no flicker, "
    "no watermark, no text, no unsafe crowd behaviour. Respect Jagannath culture."
)


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()


def to_seconds(timecode: str) -> int:
    minutes, seconds = timecode.split(":")
    return int(minutes) * 60 + int(seconds)


def run_ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Path to ODIA HERO film JSON manifest")
    parser.add_argument("--resolution", choices=["480p", "720p", "1080p"], default="1080p")
    parser.add_argument("--output-dir", default="outputs/odia_hero")
    parser.add_argument("--submit-only", action="store_true", help="Submit jobs and save task IDs without polling")
    parser.add_argument("--resume", action="store_true", help="Resume polling/downloading saved task IDs")
    parser.add_argument("--voiceover", help="Recorded/TTS narration audio file (Odia)")
    parser.add_argument("--music", help="Original or licensed devotional music file")
    parser.add_argument("--subtitles", help="Subtitle SRT file (Odia or bilingual)")
    parser.add_argument("--no-upscale", action="store_true", help="Keep 1080p output instead of 4K upscale")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    film_id = data.get("film_id", manifest_path.stem)
    target_seconds = int(data.get("target_duration_seconds", 244))
    delivery = data.get("delivery", {})
    width = int(delivery.get("target_width", 3840))
    height = int(delivery.get("target_height", 2160))
    fps = int(delivery.get("fps", 24))
    out = Path(args.output_dir) / safe_name(film_id)
    clips = out / "clips"
    normalized = out / "normalized"
    clips.mkdir(parents=True, exist_ok=True)
    normalized.mkdir(parents=True, exist_ok=True)
    task_file = out / "wan_tasks.json"

    if args.resume:
        if not task_file.exists():
            raise SystemExit(f"No saved task file to resume: {task_file}")
        tasks = json.loads(task_file.read_text(encoding="utf-8"))
    else:
        client = Wan3Client()
        tasks = []
        scenes = data["scenes"]
        for index, scene in enumerate(scenes, 1):
            duration = to_seconds(scene["end"]) - to_seconds(scene["start"])
            if not 2 <= duration <= 30:
                raise ValueError(f"Scene {index} duration {duration}s is outside Wan 3.0 limits (2–30s).")
            prompt = f"{CHARACTER} {STYLE} Scene action: {scene['beat']}. {NEGATIVE}"
            task_id = client.submit(
                prompt, duration=duration, aspect_ratio="16:9",
                resolution=args.resolution, enable_audio=False,
                enable_prompt_expansion=False, seed=4100 + index,
            )
            tasks.append({
                "scene": index, "task_id": task_id, "start": scene["start"],
                "end": scene["end"], "duration": duration, "beat": scene["beat"],
            })
            task_file.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Submitted scene {index}/{len(scenes)}: {task_id}", flush=True)

    if args.submit_only:
        print(f"Task IDs saved to {task_file}. Run again with --resume after jobs are submitted.")
        return

    client = Wan3Client()
    normalized_paths = []
    for task in tasks:
        scene_number = int(task["scene"])
        raw_path = clips / f"scene-{scene_number:02d}.mp4"
        if not raw_path.exists():
            url = client.wait(task["task_id"])
            client.download(url, str(raw_path))
            print(f"Downloaded {raw_path}", flush=True)

        expected = int(task.get("duration") or (to_seconds(task["end"]) - to_seconds(task["start"])))
        normalized_path = normalized / f"scene-{scene_number:02d}.mp4"
        run_ffmpeg([
            "-i", str(raw_path), "-t", str(expected),
            "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,"
                   f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-movflags", "+faststart", str(normalized_path),
        ])
        normalized_paths.append(normalized_path)

    concat_file = out / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path.resolve().as_posix()}'\n" for path in normalized_paths),
        encoding="utf-8",
    )
    silent_1080 = out / "odia-hero-picture-1080p.mp4"
    run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-t", str(target_seconds), "-r", str(fps),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(silent_1080),
    ])

    inputs = ["-i", str(silent_1080)]
    filters = []
    audio_labels = []
    if args.voiceover:
        inputs += ["-i", args.voiceover]
        filters.append(f"[1:a]aresample=48000,apad,atrim=0:{target_seconds},volume=1.0[voice]")
        audio_labels.append("[voice]")
    if args.music:
        music_index = 2 if args.voiceover else 1
        inputs += ["-i", args.music]
        filters.append(f"[{music_index}:a]aresample=48000,apad,atrim=0:{target_seconds},volume=0.18[music]")
        audio_labels.append("[music]")

    audio_filter = ""
    if len(audio_labels) == 2:
        filters.append("[voice][music]amix=inputs=2:duration=longest:normalize=0[aout]")
        audio_filter = "[aout]"
    elif len(audio_labels) == 1:
        filters.append(f"{audio_labels[0]}anull[aout]")
        audio_filter = "[aout]"

    final_1080 = out / "odia-hero-final-1080p.mp4"
    command = [*inputs]
    if filters:
        command += ["-filter_complex", ";".join(filters)]
    command += ["-map", "0:v:0"]
    if audio_filter:
        command += ["-map", audio_filter, "-c:a", "aac", "-b:a", "192k"]
    else:
        command += ["-an"]
    command += [
        "-t", str(target_seconds), "-r", str(fps), "-c:v", "libx264",
        "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(final_1080),
    ]
    run_ffmpeg(command)

    if args.subtitles:
        subtitled = out / "odia-hero-subtitled-1080p.mp4"
        subtitle_path = str(Path(args.subtitles).resolve()).replace("\\", "\\\\").replace(":", "\\:")
        run_ffmpeg([
            "-i", str(final_1080), "-vf", f"subtitles='{subtitle_path}'",
            "-t", str(target_seconds), "-r", str(fps),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(subtitled),
        ])
        final_1080 = subtitled

    if args.no_upscale:
        print(f"1080p master: {final_1080}")
    else:
        final_4k = out / "odia-hero-final-4k.mp4"
        run_ffmpeg([
            "-i", str(final_1080), "-vf", f"scale={width}:{height}:flags=lanczos",
            "-t", str(target_seconds), "-r", str(fps),
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "copy" if audio_filter else "aac",
            "-movflags", "+faststart", str(final_4k),
        ])
        print(f"4K master: {final_4k}")

    if not args.voiceover:
        print("NOTE: No narration audio was supplied; output is silent.")
    if not args.subtitles:
        print("NOTE: No subtitle SRT was supplied; output has no subtitles.")
    if not args.music:
        print("NOTE: No music was supplied; output has no music.")
    print(f"Picture timeline target: {target_seconds}s at {fps}fps.")


if __name__ == "__main__":
    main()
