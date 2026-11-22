"""Render a two-reference fashion video with Wan 3.0 Image-to-Video.

Requires WAVESPEED_API_KEY and FFmpeg. Each image is sent as a base64 data URL;
no public image hosting is required. Provider generation is paid.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from services.wan3_client import Wan3Client

PROMPT_1 = ("Use this reference as the exact first frame and preserve the adult model's face, "
"hair, makeup, proportions, royal-blue sheer gown with gold embroidery, earrings and heels. "
"She walks slowly and confidently toward the camera through the same grand chandelier ballroom. "
"The gown moves naturally; full-length framing; smooth stabilized backward dolly; warm gold light, "
"deep royal blue, glossy marble reflections, photorealistic natural skin texture, luxury fashion campaign.")
PROMPT_2 = ("Preserve the exact adult model identity, face, hairstyle, makeup, jewelry and royal-blue "
"gold-embroidered gown from the reference. She sits elegantly on the deep-blue velvet sofa in the "
"upscale night interior, gently turns her gaze toward camera and makes a subtle natural pose adjustment. "
"Medium-to-three-quarter framing, gentle cinematic push-in, warm chandelier light and city lights, "
"realistic anatomy, fabric and skin texture, premium luxury fashion editorial.")
NEGATIVE = ("No identity drift, face swap, wardrobe change, extra people, extra fingers, fused hands, "
"distorted anatomy, warped jewelry, flicker, frame morphing, plastic skin, excessive retouching, "
"beauty filter, text, logos, watermark, explicit nudity, sexualized camera angles.")

def ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--walking-image", required=True, help="First JPG/PNG reference")
    parser.add_argument("--seated-image", required=True, help="Second JPG/PNG reference")
    parser.add_argument("--output-dir", default="outputs/blue_couture")
    parser.add_argument("--resolution", choices=["480p", "720p", "1080p"], default="1080p")
    parser.add_argument("--duration-per-shot", type=int, default=5)
    args = parser.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    client = Wan3Client()
    shots = [(args.walking_image, PROMPT_1, "shot-01-walk"),
             (args.seated_image, PROMPT_2, "shot-02-seated")]
    clips = []
    for index, (image, prompt, name) in enumerate(shots, 1):
        task_id = client.submit_image_to_video(
            image, f"{prompt} Negative prompt: {NEGATIVE}",
            duration=args.duration_per_shot, aspect_ratio="9:16",
            resolution=args.resolution, generate_audio=False, seed=7300 + index)
        print(f"Submitted {name}: {task_id}", flush=True)
        raw = out / f"{name}.mp4"
        client.download(client.wait(task_id), str(raw))
        clips.append(raw)
    normalized=[]
    for i, clip in enumerate(clips, 1):
        target=out / f"normalized-{i}.mp4"
        ffmpeg(["-i",str(clip),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,format=yuv420p",
                "-an","-c:v","libx264","-preset","medium","-crf","18","-movflags","+faststart",str(target)])
        normalized.append(target)
    concat=out / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in normalized),encoding="utf-8")
    master=out / "blue-couture-vertical.mp4"
    ffmpeg(["-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(master)])
    print(f"Video master: {master.resolve()}")

if __name__ == "__main__":
    main()
