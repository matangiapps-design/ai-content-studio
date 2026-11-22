# ODIA HERO Wan 3.0 integration

## Studio video-engine integration

Select `WaveSpeed AI (Wan 3.0)` under Platform Settings → Active Engine Selection. Choose 480p, 720p, or 1080p. The existing WaveSpeed model-ID and Vertex AI (Veo) choices remain available. The video settings are stored in the server configuration.

## Setup
1. Create a WaveSpeedAI account and generate an API key.
2. Put `WAVESPEED_API_KEY=...` in the server-side `.env` file. Do not commit the key or expose it in frontend code.
3. Install the existing project requirements (`requests` is already included).
4. Install FFmpeg and ensure `ffmpeg` is on PATH.
5. Run a small test scene first; generation is paid and each scene incurs provider charges.

## First test
```bash
python scripts/odia_hero_wan3_render.py docs/ODIA_HERO/film-01.json --resolution 720p --submit-only
```
Remove `--submit-only` to submit and wait for scene downloads and rough assembly.

The film manifests use twelve 20–24 second beats. Wan 3.0 supports 2–30 second clips; scene outputs may not exactly match the planned timeline. The edit must be trimmed and assembled to exactly 04:04.

## Quality and 4K
WaveSpeed's Wan 3.0 route supports up to 1080p. The final 3840×2160 export therefore requires a separate upscale pass; do not describe it as native 4K. Use image/reference-to-video rather than text-only generation if a supported endpoint and Biku reference-image upload are configured, to improve identity consistency.

## Limits
This integration is not a live service until the user supplies a valid WaveSpeed API key in the local/server environment. This chat does not have access to that secret and will not ask the user to paste it here. Check provider pricing and billing before generating all scenes.
