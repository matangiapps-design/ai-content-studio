"""Video retouch utilities.

Provides a conservative mask-based tattoo cleanup endpoint. The caller supplies
a binary mask for the exact skin region to retouch; no face/body detection or
identity-altering processing is performed. Uses OpenCV temporal inpainting on
the masked region and FFmpeg to preserve the source audio.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import subprocess
import tempfile
import uuid
from pathlib import Path

from server.core.security import copy_upload

router = APIRouter()
OUTPUT_DIR = "workspace/retouch_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@router.post("/remove-mark")
def remove_mark(
    video: UploadFile = File(...),
    mask: UploadFile = File(...),
):
    """Remove a small visible mark from video frames using a user-supplied mask.

    Mask must be a video with the same duration, dimensions and frame rate as
    the source. White pixels are the exact area to inpaint; black pixels remain
    untouched. This is not automatic tattoo detection.
    """
    temp_paths = []
    try:
        def save_upload(upload, suffix):
            handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            handle.close()
            temp_paths.append(handle.name)
            copy_upload(upload.file, handle.name)
            return handle.name

        src = save_upload(video, ".mp4")
        mask_path = save_upload(mask, ".mp4")
        output = os.path.join(OUTPUT_DIR, f"{uuid.uuid4().hex}_retouched.mp4")

        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,r_frame_rate",
             "-of", "json", src],
            check=True, capture_output=True, text=True
        )
        import json
        meta = json.loads(probe.stdout)["streams"][0]
        width, height = int(meta["width"]), int(meta["height"])

        cap_src = cv2.VideoCapture(src)
        cap_mask = cv2.VideoCapture(mask_path)
        if not cap_src.isOpened() or not cap_mask.isOpened():
            raise ValueError("Could not open uploaded video or mask video.")

        fps = cap_src.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap_src.get(cv2.CAP_PROP_FRAME_COUNT))
        mask_count = int(cap_mask.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0 or mask_count != frame_count:
            raise ValueError("Mask video must have the same number of frames as source.")
        if int(cap_mask.get(cv2.CAP_PROP_FRAME_WIDTH)) != width or int(cap_mask.get(cv2.CAP_PROP_FRAME_HEIGHT)) != height:
            raise ValueError("Mask video dimensions must match source video.")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        silent_path = output.replace(".mp4", "_silent.mp4")
        writer = cv2.VideoWriter(silent_path, fourcc, fps, (width, height))
        if not writer.isOpened():
            raise RuntimeError("Could not create output video.")

        try:
            for _ in range(frame_count):
                ok_src, frame = cap_src.read()
                ok_mask, mask_frame = cap_mask.read()
                if not ok_src or not ok_mask:
                    raise ValueError("Video and mask ended unexpectedly.")
                gray = cv2.cvtColor(mask_frame, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                # Slight expansion smooths mask-edge seams; caller controls exact region.
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                binary = cv2.dilate(binary, kernel, iterations=1)
                clean = cv2.inpaint(frame, binary, 3, cv2.INPAINT_TELEA)
                writer.write(clean)
        finally:
            cap_src.release()
            cap_mask.release()
            writer.release()

        subprocess.run(
            ["ffmpeg", "-y", "-i", silent_path, "-i", src,
             "-map", "0:v:0", "-map", "1:a?", "-c:v", "libx264",
             "-preset", "medium", "-crf", "18", "-c:a", "copy",
             "-movflags", "+faststart", output],
            check=True, capture_output=True
        )
        Path(silent_path).unlink(missing_ok=True)
        return {"message": "Retouched video rendered.", "path": output.replace("\\", "/")}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        for path in temp_paths:
            Path(path).unlink(missing_ok=True)


# Lazy import so the existing Studio works without optional OpenCV installed.
import cv2
