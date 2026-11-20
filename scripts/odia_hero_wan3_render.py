"""Render ODIA HERO scenes through WaveSpeedAI Wan 3.0 and assemble with FFmpeg.

Usage:
  python scripts/odia_hero_wan3_render.py docs/ODIA_HERO/film-01.json
  python scripts/odia_hero_wan3_render.py docs/ODIA_HERO/film-02-stuck-rath-wheel.json

Set WAVESPEED_API_KEY in the server .env. This incurs provider charges per generated scene.
The script defaults to a 720p scene generation; final 4K upscaling is a separate step.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from pathlib import Path
from wan3_client import Wan3Client

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = ("Biku: the exact same small white stickman hero, round white head, expressive black eyes, "
             "thin black arms and legs, bright red cape. Preserve exact proportions, face and cape.")
STYLE = ("Cinematic 3D animated family film, Puri Odisha Jagannath Rath Yatra, respectful devotional atmosphere, "
         "colourful decorated traditional chariot and flags, expressive animation, natural cape motion, "
         "detailed environment, cinematic lighting, smooth camera movement. Stickman animation only, no live-action actors.")
NEGATIVE = ("No character redesign, no missing red cape, no extra limbs, no distorted faces, no flicker, "
            "no watermark, no text, no unsafe crowd behaviour. Respect Jagannath culture.")

def safe_name(value):
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", help="Path to ODIA HERO film JSON manifest")
    parser.add_argument("--resolution", choices=["480p", "720p", "1080p"], default="720p")
    parser.add_argument("--output-dir", default="outputs/odia_hero")
    parser.add_argument("--submit-only", action="store_true", help="Submit jobs and save task IDs without polling")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    film_id = data.get("film_id", manifest_path.stem)
    out = Path(args.output_dir) / safe_name(film_id)
    clips = out / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    client = Wan3Client()
    tasks = []
    scenes = data["scenes"]

    for index, scene in enumerate(scenes, 1):
        prompt = f"{CHARACTER} {STYLE} Scene action: {scene['beat']}. {NEGATIVE}"
        start = scene["start"]
        end = scene["end"]
        def seconds(tc):
            mm, ss = tc.split(":")
            return int(mm) * 60 + int(ss)
        duration = seconds(end) - seconds(start)
        duration = max(2, min(30, duration))
        task_id = client.submit(prompt, duration=duration, aspect_ratio="16:9",
                                resolution=args.resolution, enable_audio=False,
                                enable_prompt_expansion=False, seed=4100 + index)
        tasks.append({"scene": index, "task_id": task_id, "start": start, "end": end, "beat": scene["beat"]})
        (out / "wan_tasks.json").write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        print(f"Submitted scene {index}/{len(scenes)}: {task_id}", flush=True)

    if args.submit_only:
        print(f"Task IDs saved to {out / 'wan_tasks.json'}")
        return

    clip_paths = []
    for task in tasks:
        url = client.wait(task["task_id"])
        path = clips / f"scene-{task['scene']:02d}.mp4"
        client.download(url, str(path))
        clip_paths.append(path)
        print(f"Downloaded {path}", flush=True)

    concat_file = out / "concat.txt"
    concat_file.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in clip_paths), encoding="utf-8")
    rough = out / "odia-hero-rough.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(rough)], check=True)
    print(f"Rough silent assembly created: {rough}")
    print("Next: add Odia narration/music/subtitles, trim to exactly 244 seconds, QA, then upscale/export 4K.")

if __name__ == "__main__":
    main()
