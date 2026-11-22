# MATANGI Free-First Video Pipeline

## Integration status

MATANGI now contains an optional OpenShorts adapter, exposed to the web and Android clients through the authenticated backend:

- `GET /api/openshorts/status` — checks whether the configured OpenShorts API is reachable.
- `POST /api/openshorts/generate` — submits a public HTTPS video URL for vertical clipping.
- `GET /api/openshorts/jobs/{job_id}` — checks asynchronous job status and returns completed clips.

The adapter uses OpenShorts' documented REST contract: `POST /api/process` and `GET /api/status/{job_id}`. It submits only clipping jobs. It does **not** publish to social media, create AI actors, dub audio, or invoke paid video-generation models.

Upstream: https://github.com/mutonby/openshorts

## Free-first safety defaults

- `OPENSHORTS_API_URL` is empty by default, so the integration stays disabled until a self-hosted service is configured.
- Public/hosted OpenShorts URLs are blocked by default. Do not set `OPENSHORTS_ALLOW_HOSTED=true` unless hosted quota/billing use is deliberately intended.
- Self-hosted OpenShorts uses no OpenShorts API key. Its AI moment-selection stage still needs either a Gemini key or an OpenAI-compatible local LLM. MATANGI can forward `OPENSHORTS_GEMINI_API_KEY` as `X-Gemini-Key`; alternatively configure `LLM_BASE_URL` and `LLM_MODEL` in the OpenShorts service environment. `OPENSHORTS_API_KEY` is optional for a private instance that has an additional auth proxy.
- No automatic low-quality retry occurs. If OpenShorts returns `needs_confirmation`, MATANGI returns a quality warning without submitting a forced low-quality job.
- Processing requires a positive rights acknowledgement. Only submit videos you own or have permission to process.
- Social publishing is intentionally not exposed in this adapter.

## Self-host OpenShorts

OpenShorts' core repository is MIT-licensed. Its self-hosted stack uses Docker Compose, Python/FFmpeg and local model resources. The upstream Docker Compose file starts an API service on port 8000 and a dashboard on port 5175; the API itself is sufficient for MATANGI.

1. On a PC or server with Docker Engine and Docker Compose, clone and start the upstream project:
   ```bash
   git clone https://github.com/mutonby/openshorts.git
   cd openshorts
   docker compose up --build -d
   ```
2. Keep the unauthenticated self-hosted API on a private interface/network. Do not expose port 8000 to the public internet.
3. Make port 8000 reachable from the MATANGI backend over a private network. When both stacks share a Docker network, use the OpenShorts service DNS name (for example `http://openshorts-backend:8000`). For a backend running directly on the same machine, use `http://127.0.0.1:8000`.
4. Add these variables to the MATANGI backend environment (or its local `.env`), then restart the MATANGI backend:
   ```dotenv
   OPENSHORTS_API_URL=http://openshorts-backend:8000
   OPENSHORTS_API_KEY=
   OPENSHORTS_ALLOW_HOSTED=false
   ```
   Replace the URL with the private address reachable from the MATANGI backend. The MATANGI Docker Compose configuration now reads these variables from `.env` and keeps hosted mode disabled. A Docker container's `127.0.0.1` is the container itself, not the host or another container. If you use Gemini, keep the key only in MATANGI's local `.env`; the adapter forwards it to the private OpenShorts API in the `X-Gemini-Key` header. If you use a local LLM, configure `LLM_BASE_URL` and `LLM_MODEL` in the OpenShorts service `.env` instead and leave `OPENSHORTS_GEMINI_API_KEY` blank.
5. Open MATANGI's **OpenShorts AI** page or Android app section and run **Test connection**. It should report the OpenShorts API as ready before any clipping job is submitted.

### Local model option

The upstream project supports an OpenAI-compatible local language model through `LLM_BASE_URL` and `LLM_MODEL` for transcript-based moment selection. For example, an Ollama instance can be used on the same host. Model downloads and CPU/GPU processing still consume local disk, memory, electricity and hardware; “free” means no OpenShorts subscription, not zero resource cost. Some visual-layout and silent-video workflows may still use Gemini unless the relevant stages are disabled or locally supported.

## API behaviour

- Source URL must be public HTTPS.
- The user must confirm rights to process the source.
- Default output is vertical; clip duration defaults to 15–60 seconds.
- OpenShorts returns a job ID immediately. Processing can take minutes; MATANGI polls its job status endpoint.
- A 402 quota response or 429 concurrency response is surfaced; MATANGI does not retry the job automatically.
- A low-source-quality response is surfaced as a confirmation requirement; MATANGI does not bypass it.

## What is deliberately not included

- No Render deployment or cloud service is created.
- No paid OpenShorts cloud usage is enabled by default.
- No WaveSpeed API is used by this integration.
- No social accounts are connected or posts published.
- No third-party OpenShorts source code is copied into MATANGI; the integration calls the separately self-hosted API.

## Security

- Keep the self-hosted OpenShorts API private; it is unauthenticated by default.
- Never commit `.env`, API keys, cookies, session tokens, or user videos.
- Optional hosted mode is disabled by default to prevent surprise metered use.
- Only process media for which you hold the required rights.

## Upstream references

- https://github.com/mutonby/openshorts
- https://github.com/mutonby/openshorts/blob/main/skills/openshorts/reference.md
- https://github.com/mutonby/openshorts/blob/main/LICENSE
