"""Low-cost Wan 3.0 test runner for ODIA HERO.

Usage:
  WAVESPEED_API_KEY=... python scripts/odia_hero_wan3_test.py docs/ODIA_HERO/film-01.json
  Add --all-scenes only after approving the provider cost estimate.
"""
from __future__ import annotations
import argparse, json, sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services"))
from wan3_client import Wan3Client

CHARACTER = "Biku, same small white stickman, round white head, black expressive eyes, thin black arms and legs, bright red cape. Preserve exact design."
STYLE = "Cinematic 3D animated family film, Puri Odisha Jagannath Rath Yatra, respectful devotional atmosphere, colourful decorated chariot and flags, smooth cinematic camera, expressive animation, 16:9, no live-action actors, no text, no watermark."

def sec(tc):
    m,s=tc.split(":")
    return int(m)*60+int(s)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--resolution",choices=["480p","720p","1080p"],default="720p")
    ap.add_argument("--all-scenes",action="store_true",help="Submit every scene; incurs provider charges for every clip")
    ap.add_argument("--submit-only",action="store_true")
    args=ap.parse_args()
    data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    scenes=data["scenes"] if args.all_scenes else data["scenes"][:1]
    out=Path("outputs/odia_hero")/data["film_id"]
    clips=out/"clips"; clips.mkdir(parents=True,exist_ok=True)
    client=Wan3Client()
    jobs=[]
    for i,sc in enumerate(scenes,1):
        duration=max(2,min(30,sec(sc["end"])-sec(sc["start"])))
        prompt=f"{CHARACTER} {STYLE} Action: {sc['beat']}. Keep the character family-friendly and safe. No dangerous crowd behaviour."
        task=client.submit(prompt,duration=duration,aspect_ratio="16:9",resolution=args.resolution,enable_audio=False,enable_prompt_expansion=False,seed=7100+i)
        jobs.append({"scene":i,"task_id":task,"beat":sc["beat"]})
        out.mkdir(parents=True,exist_ok=True)
        (out/"wan_tasks.json").write_text(json.dumps(jobs,indent=2),encoding="utf-8")
        print(f"Submitted scene {i}/{len(scenes)}: {task}",flush=True)
    if args.submit_only:
        print(f"Task IDs saved in {out/'wan_tasks.json'}")
        return
    files=[]
    for job in jobs:
        url=client.wait(job["task_id"])
        dest=clips/f"scene-{job['scene']:02d}.mp4"
        client.download(url,str(dest)); files.append(dest)
        print(f"Downloaded {dest}",flush=True)
    if len(files)==1:
        print(f"Test clip ready: {files[0]}")
        return
    concat=out/"concat.txt"
    concat.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in files),encoding="utf-8")
    target=out/"rough-assembly.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c:v","libx264","-pix_fmt","yuv420p","-an",str(target)],check=True)
    print(f"Rough assembly: {target}. Trim to 04:04, add Odia audio/subtitles, QA and upscale separately.")

if __name__=="__main__":
    main()
