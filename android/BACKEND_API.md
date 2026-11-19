# MATANGI AI Backend API Contract

This document defines the HTTP API expected by the MATANGI AI Android app (version 1.1.0). The Android app is a client; model weights and provider credentials must remain on your backend/GPU workers.

## 1. Deployment requirements

- Serve the API over HTTPS in production.
- Expose a valid TLS certificate.
- Configure CORS for the WebView origin `https://appassets.androidplatform.net`.
- Allow methods `GET, POST, OPTIONS` and request headers `Accept, Content-Type`.
- Return JSON with the `Content-Type: application/json` header.
- Keep provider API keys and worker credentials on the server. Do not embed them in the APK.

## 2. Health check

`GET /health`

Example response:

```json
{
  "status": "ok",
  "message": "MATANGI generation API is ready"
}
```

The app marks the backend online only when this endpoint returns a successful HTTP status and valid JSON.

## 3. Submit a generation job

`POST /api/v1/generations`

Image example:

```json
{
  "type": "image",
  "prompt": "Cinematic product photo of an electric supercar at night",
  "engine": "qwen-image",
  "settings": {
    "aspect_ratio": "16:9"
  }
}
```

Video example:

```json
{
  "type": "video",
  "prompt": "An astronaut crosses a red desert at sunset",
  "engine": "wan2.2",
  "settings": {
    "duration_seconds": 10,
    "aspect_ratio": "16:9",
    "mode": "text-to-video"
  }
}
```

Supported engine identifiers exposed by the client:

- Image: `auto`, `qwen-image`, `flux`, `sdxl`
- Video: `auto`, `wan2.2`, `wan2.1`, `helios`, `ltx-video`

The server must validate availability and return a clear error when a selected route is not installed or enabled. Do not silently claim a model ran when no worker accepted the job.

Successful submission should return HTTP 202 (or another 2xx status) and:

```json
{
  "job_id": "job_123456",
  "status": "queued"
}
```

The client also accepts an optional `output_url` when a job completes immediately.

## 4. Poll job status

`GET /api/v1/generations/{job_id}`

Example response while running:

```json
{
  "job_id": "job_123456",
  "status": "running"
}
```

Example completed response:

```json
{
  "job_id": "job_123456",
  "status": "completed",
  "output_url": "https://cdn.example.com/generated/job_123456.png"
}
```

Example failed response:

```json
{
  "job_id": "job_123456",
  "status": "failed",
  "error": "The selected model worker is unavailable"
}
```

Use these status values: `queued`, `running`, `completed`, `failed`, `cancelled`. Output URLs must be absolute HTTP(S) URLs reachable by the device.

## 5. Model routing guidance

The app exposes engine selectors; it does not bundle or install any model. Configure workers separately and map each engine identifier to a real inference backend:

| Engine | Suggested worker |
|---|---|
| `qwen-image` | ComfyUI workflow with Qwen Image |
| `flux` | FLUX-compatible inference worker |
| `sdxl` | SDXL-compatible inference worker |
| `wan2.1` / `wan2.2` | Wan video inference worker |
| `helios` | Helios video worker |
| `ltx-video` | LTX-Video worker |
| `auto` | Server-side router that selects only healthy, configured workers |

The server should expose a capability/health monitor internally, enforce queue limits, validate input sizes, and report actionable errors. Add authentication/rate limits before public deployment; the current client does not embed a secret API key.

## 6. Current limitations

- Agent tiles are workflow placeholders; they do not execute autonomous agents yet.
- Image/video generation requires this API and functioning model workers.
- Job history is stored locally on the device. It is not synced across devices.
- The app checks `/health`, submits generation jobs and polls job status. It does not provision GPU instances or install model weights.
