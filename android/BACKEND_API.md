# MATANGI AI Android — Existing Backend Integration

The Android app is a client for this repository's existing FastAPI backend. It does not create a second generation API.

## Backend address and security

Use the public HTTPS origin that serves the existing Studio backend and frontend, for example `https://studio.example.com`.

Set these values on the backend:

- `STUDIO_API_TOKEN`: a long random token.
- `STUDIO_AUTH_DISABLED=false`: keep authentication enabled.
- `CORS_ORIGINS`: include both the web Studio origin and the Android WebView origin:
  `https://studio.example.com,https://appassets.androidplatform.net`.

The Android app sends `Authorization: Bearer <STUDIO_API_TOKEN>` for protected requests. The token is held in app memory only; it is not written to local storage. Enter it again after restarting the app. Do not put provider keys (Gemini, WaveSpeed, Pixabay, YouTube) in the APK.

## Endpoints used by the Android client

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Public backend health check |
| GET | `/api/config` | Verify API token and load masked engine configuration |
| POST | `/api/config` | Save `IMAGE_ENGINE`, `WAVESPEED_IMAGE_MODEL`, `WAVESPEED_VIDEO_MODEL` |
| POST | `/api/generate/quick` | Queue a full creator-pipeline video job |
| GET | `/api/generate/status/{job_id}` | Read job progress, step, result or error |
| POST | `/api/generate/cancel/{job_id}` | Request job cancellation |
| GET | `/api/jobs` | Load persisted job history |
| GET | `/api/generate/media?path={encoded_path}` | Fetch the completed media file |

## Generation payload

The Android client posts the existing `GenerationRequest` schema to `/api/generate/quick`, including:

- `topic`, `style`, `voice`, `aspect_ratio`, `bg_mode`
- `content_style`, `start_point`, `script_length`
- `image_count`, `video_count`
- `bg_music`, `fact_check`, `auto_captions`, `omnichannel`
- `generate_thumbnail`, `generate_seo`, `generate_timestamps`, `generate_snippets`
- `audio_engine`, `video_engine`

The API returns a `job_id`. The Android app polls `/api/generate/status/{job_id}` for `status`, `progress`, `step`, `result` and `error`. When complete, it fetches the `result` path through the protected media endpoint.

## Engines that are actually wired in the current repository

- Image: `Gemini API` or `WaveSpeed AI`. This image stage is part of the full production pipeline; there is no standalone image-generation endpoint in the current API.
- Video: `WaveSpeed AI` or `Vertex AI (Veo)`.
- WaveSpeed model IDs are configurable in `WAVESPEED_IMAGE_MODEL` and `WAVESPEED_VIDEO_MODEL`.

Wan 2.1/2.2, Helios, Qwen Image, SDXL and OmniRoute are not currently exposed by this backend's generation route. The Android interface marks these as future integrations rather than presenting them as working engines. LTX-based video generation can be configured through the WaveSpeed video model ID if the provider supports that model for your account.

## Production checklist

1. Deploy the backend and web frontend behind one HTTPS reverse-proxy origin.
2. Set `STUDIO_API_TOKEN`, `STUDIO_AUTH_DISABLED=false`, and both CORS origins.
3. Configure real Gemini / WaveSpeed / Vertex credentials in the authenticated server Settings page.
4. Enter the HTTPS origin and Studio token in the Android app, then use **Test connection**.
5. Run a short generation test before using longer or higher-cost jobs.

The backend is single-administrator: its provider configuration, job history and media are shared by all authorized users. Protect the API token and do not distribute it inside the APK.
