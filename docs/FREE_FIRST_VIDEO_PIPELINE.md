# MATANGI Free-First Video Pipeline

## Decision

Use **OpenShorts** as a separate, self-hosted clip-production service alongside MATANGI Creator Studio. Do not copy its source into this repository or bundle its Python/Docker stack inside the Android APK.

- Upstream: https://github.com/mutonby/openshorts
- Core license: MIT. The upstream `cloud/` directory has a separate commercial license; MATANGI does not need that directory for self-hosting.
- Main functions: long-video clipping, 9:16 reframing, transcript-based moment selection, subtitles, clip editing and optional social publishing.
- The Android app remains a client; video processing runs on a computer/server with Docker and adequate memory.

## Cost and requirements

- OpenShorts self-hosting software: free under its MIT core license.
- Minimum practical setup from upstream docs: Docker + Docker Compose and 8 GB+ RAM. Model downloads and CPU processing use local disk, memory and compute.
- Clip selection can use a local OpenAI-compatible LLM (for example Ollama/LM Studio) through `LLM_BASE_URL`, avoiding a Gemini key for transcript-based moment selection. Gemini is still needed for some visual-layout and silent-video paths.
- AI actor/video generation, dubbing and social publishing are optional and may require separate API keys or paid services. Keep them disabled until explicitly configured.
- No Render deployment, paid hosting, paid GPU, or paid API is required for the self-hosted clip workflow.

## Safe setup (run on a PC/server, not on Android)

1. Install Docker Engine/Desktop and Docker Compose.
2. Clone the upstream repository:
   ```bash
   git clone https://github.com/mutonby/openshorts.git
   cd openshorts
   ```
3. Review upstream `.env.example` and `docker-compose.yml`. Do not add cloud billing components or commit API keys.
4. Start the upstream stack:
   ```bash
   docker compose up --build
   ```
5. Open the local dashboard at `http://localhost:5175` as documented upstream.
6. Configure a local LLM if available; otherwise configure a Gemini key directly in the local OpenShorts settings. Never paste secrets into GitHub or ChatGPT.
7. Test with a short video you own or have permission to process. Export a vertical clip and check captions, crop, audio and output quality.

## MATANGI integration boundary

The upstream project documents a REST API, OpenAPI docs at `/docs`, an MCP endpoint at `/mcp`, and completion webhooks. Its documented processing request is `POST /api/process`. A future MATANGI backend adapter can submit a source URL, record the returned job ID, receive the completion webhook, and expose the resulting clip links to the app.

**Not yet implemented:** this repository does not currently contain an OpenShorts API adapter, Android UI, webhook receiver, or automated social publishing integration. This document is the integration plan only. Do not display OpenShorts as a connected engine until an actual instance has been configured and health-tested.

## Security

- Keep a self-hosted instance bound to localhost or a private network until authentication and HTTPS are configured.
- Never expose an unauthenticated local processing API to the public internet.
- Never commit `.env`, API keys, YouTube cookies, session tokens or user media.
- Use only media you own or are authorized to process.
- Keep social publishing disconnected until each destination account is intentionally connected and tested.

## Upstream references

- https://github.com/mutonby/openshorts
- https://github.com/mutonby/openshorts#run-without-a-google-key-local-llm-optional
- https://github.com/mutonby/openshorts#rest-api--api-keys
