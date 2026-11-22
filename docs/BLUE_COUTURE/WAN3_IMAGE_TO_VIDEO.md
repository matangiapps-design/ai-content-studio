# Blue Couture — Wan 3.0 Image-to-Video

The current WaveSpeed account-independent public API documentation lists the exact model ID `alibaba/wan-3.0/image-to-video`. Its documented inputs include a required first-frame `image` (URL or Base64 data), prompt, 2–30 second duration, 9:16 aspect ratio, 480p/720p/1080p resolution, and optional generated audio. See the [official model API documentation](https://wavespeed.ai/docs/docs-api/alibaba/wan-3.0/image-to-video).

## Render the two supplied reference images

Place the first full-length walking reference and second seated reference on the render machine, then run:

```bash
python scripts/blue_couture_wan3_render.py \\
  --walking-image /path/to/walking-reference.jpg \\
  --seated-image /path/to/seated-reference.jpg \\
  --resolution 1080p \\
  --duration-per-shot 5
```

The script sends each local JPG/PNG as a Base64 data URL to the documented image-to-video endpoint, waits for both jobs, normalizes them to 1080×1920 at 24 fps, and concatenates the two shots. The output is a vertical MP4. Set `WAVESPEED_API_KEY` privately in the environment. FFmpeg must be installed.

## Cost and safety

The published model page lists 1080p at approximately $0.19/second, so two 5-second shots are approximately $1.90 before any taxes or pricing changes. Verify the live estimate in WaveSpeed before submitting. Generation is paid; do not auto-retry an uncertain submission. The renderer disables generated audio and produces a silent picture master. No video has been rendered by committing this code.

The image-to-video endpoint uses each photo as its own first frame. It does not guarantee exact identity continuity across separate jobs; review both clips before publishing. No claim of native 4K is made.
