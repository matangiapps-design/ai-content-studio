# CloudX Brain — bootstrap

CloudX is the control plane for the user's connected repositories, agents, GPU services, and creative providers.

## Bootstrap scope
- Read-only Guardian scans selected GitHub repositories and optional HTTP health endpoints.
- FastAPI control plane exposes health, agent inventory, provider status, and scan endpoints.
- Higgsfield connector boundary is included, but generation is intentionally disabled until the current account API contract is verified.
- CI runs tests. A scheduled GitHub Actions watchdog checks repository reachability every 15 minutes.

## Safety
Guardian is observe → diagnose → propose → test → approval → merge/deploy. This bootstrap does not write to repositories, merge PRs, or deploy. Automated repair remains disabled until a sandboxed branch/PR workflow and test gates are implemented.

## Run
Copy `cloudx-brain/.env.example` to `cloudx-brain/.env`, configure a read-only GitHub token and repository list, then run:
```bash
docker compose -f cloudx-brain/docker-compose.yml up --build
```
API docs: `http://localhost:8000/docs`.

## Next milestones
1. Persistent event/memory store and knowledge graph.
2. Task queue and orchestrator.
3. Model router and local/cloud GPU adapters.
4. Sandboxed repair agent that creates branches and PRs only.
5. Higgsfield image/video job adapter with verified API schema.
6. Dashboard, alerts, metrics, backup and recovery.
