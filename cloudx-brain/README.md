# CloudX Brain

CloudX is a modular control plane for repositories, agents, GPU services, and creative providers.

## Implemented in this milestone
- FastAPI control plane: health, agent inventory, provider status, Guardian scan, and persistent SQLite event memory.
- Guardian checks repository reachability, latest completed GitHub Actions workflows, and configured HTTP service endpoints.
- Repair Agent converts evidence into actionable repair plans. It never edits source code or deploys.
- Scheduled GitHub Actions workflow runs every 15 minutes and maintains one alert issue in this repository.
- CI workflow runs unit tests.
- Higgsfield REST connector uses the documented server-side Key authentication, model-specific endpoint path, idempotency key, and request-status polling. It does not guess a model schema.

## Run locally
Copy cloudx-brain/.env.example to cloudx-brain/.env, configure tokens, then run:
```bash
docker compose -f cloudx-brain/docker-compose.yml up --build
```
API docs: http://localhost:8000/docs.

## GitHub monitoring setup
In this repository's Settings → Secrets and variables → Actions:
- Secret CLOUDX_GITHUB_TOKEN: fine-grained token with Metadata read and Actions read on each monitored repository.
- Variable CLOUDX_GITHUB_REPOS: comma-separated owner/repo names.
- Optional variable CLOUDX_SERVICE_URLS: comma-separated health endpoints.
- The built-in GITHUB_TOKEN needs Issues write permission to maintain the alert issue in this repository.

The workflow runs from the default branch after the pull request is merged. GitHub Actions scheduling is periodic monitoring, not a continuously running server.

## Higgsfield setup
Create an API key in the Higgsfield Console and store the key ID and secret as server-side environment variables HF_API_KEY_ID and HF_API_KEY_SECRET. Never put them in frontend code or commit them.

Submit a generation:
```http
POST /higgsfield/requests
Content-Type: application/json

{"model_path":"higgsfield-ai/soul/v2/standard","input":{"prompt":"A cinematic mountain landscape"}}
```
Check the returned request ID:
```http
GET /higgsfield/requests/{request_id}
```
Select a model and request fields from its current model-specific API documentation. API usage is pay-as-you-go; generation calls can incur charges.

## Not yet implemented
A general LLM-backed code patcher, sandboxed patch execution and PR creation, semantic knowledge graph, task queue, model router, GPU scheduler, dashboard, external alerts, and live Higgsfield account validation. Source repair remains proposal-only until isolated patching and evaluation gates are implemented.
