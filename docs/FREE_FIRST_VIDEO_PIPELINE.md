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

## Self-host OpenShorts alongside MATANGI

OpenShorts' core repository is MIT-licensed. The integration can use a local Docker installation with no OpenShorts subscription. The OpenShorts API itself still needs either a Gemini key or an OpenAI-compatible local LLM for its AI moment-selection stage.

### 1. Prepare MATANGI

1. Install Docker Engine and Docker Compose v2.24 or newer on a PC/server. This is a local/server setup; it does not deploy anything to Render or another cloud.
2. Clone the MATANGI repository and enter it:
   ```bash
   git clone https://github.com/matangiapps-design/ai-content-studio.git
   cd ai-content-studio
   cp .env.example .env
   ```
3. Edit `.env`: set a strong `STUDIO_API_TOKEN`, your MATANGI `STUDIO_PUBLIC_ORIGIN`, and `OPENSHORTS_API_URL=http://openshorts-backend:8000`. Leave `OPENSHORTS_ALLOW_HOSTED=false`. If using Gemini, set `OPENSHORTS_GEMINI_API_KEY` in this local file. Do not commit it.
4. Start MATANGI's backend once so Docker creates the shared private network:
   ```bash
   docker compose up -d backend
   ```

### 2. Start OpenShorts on the same private network

From the MATANGI repository root:
```bash
git clone https://github.com/mutonby/openshorts.git
docker compose -p openshorts -f openshorts/docker-compose.yml -f ops/openshorts-network.override.yml up --build -d backend renderer
``

The override attaches OpenShorts to MATANGI's private `matangi_shared` Docker network and removes the upstream API/renderer host port mappings. The OpenShorts API remains reachable by the MATANGI backend at `http://openshorts-backend:8000` without exposing port 8000 publicly. The upstream renderer stays on OpenShorts' private default network with its backend.

### 3. Start MATANGI and verify

```bash
docker compose up -d
docker compose ps
``

Open MATANGI's **OpenShorts AI** page or Android app section and select **Test connection**. It should report OpenShorts as reachable before submitting any clipping job.

### 4. AI key choice

- **Gemini:** put the key in MATANGI's local `.env` as `OPENSHORTS_GEMINI_API_KEY`. MATANGI forwards it to the private OpenShorts API as `X-Gemini-Key`; it is not placed in the job body or committed to Git.
- **Local model:** configure `LLM_BASE_URL` and `LLM_MODEL` in OpenShorts' own `.env` for an OpenAI-compatible local model (Ollama, LM Studio, vLLM, llama.cpp, or LocalAI). Leave `OPENSHORTS_GEMINI_API_KEY` blank. The local model host must be reachable from the OpenShorts container.

OpenShorts' own `.env.example` documents additional optional settings. Keep AWS/S3, Google OAuth, hosted billing and social publishing credentials blank unless you deliberately need those features. MATANGI's integration does not use or activate those features.

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
