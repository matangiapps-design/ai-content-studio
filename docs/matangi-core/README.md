# MATANGI CORE — Integration Blueprint

Status: **Architecture starter / not yet deployed**

This directory defines the first integration contract for the MATANGI product ecosystem. It does not claim that the listed products are already connected.

## Goals
- One authenticated entry point for MATANGI web and Android clients.
- Aadi request router that dispatches work to specialist product adapters.
- Provider-neutral model and GPU worker interfaces.
- Shared project/job metadata and observable job status.
- Keep each product independently deployable and fault-isolated.

## Proposed topology

```text
Android / Web / Desktop
        |
        v
MATANGI CORE API  ---- Identity / Sessions
        |
        +---- Aadi Router ---- Qwen / other LLM adapters
        |
        +---- Job Service ---- Queue ---- GPU worker adapters
        |                          |---- image generation
        |                          |---- video generation
        |                          |---- voice / audio
        |
        +---- Product adapters
        |       |---- AI Content Studio
        |       |---- MusicVision
        |       |---- Seed-VC
        |       |---- Cloudphone
        |
        +---- Project / Asset metadata
        +---- Usage, billing and audit events
```

## Repository roles (proposed; validate before wiring)
| Repository | Intended responsibility | Integration state |
|---|---|---|
| ai-content-studio | Primary creative application and gateway | Existing repository; inspect before changing runtime |
| Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash | Language-model weights/code | Model-serving endpoint not verified |
| keggelGPU | GPU/CUDA starter and worker host | Production worker integration not verified |
| musicvision | Music/video workflow | Adapter contract required; checkout is not part of this scope |
| seed-vc | Voice conversion capability | Service interface and runtime not verified |
| infinite-brain-os | Knowledge and agent context | Runtime connection not verified |
| cloudphone | Cloud Android/device management | Runtime connection not verified |
| ultimate-supercar-garage-android | Separate consumer Android app | Keep separate; integrate identity only if product owner approves |

## Integration rules
1. No provider API keys in source control, client apps, logs, or this repository.
2. All provider calls run server-side through adapters.
3. Every long-running task receives a unique `job_id`, project ID, provider, state and timestamps.
4. Use idempotency keys for job creation and payment events.
5. Do not mark a job complete until the provider output is stored and verified.
6. Keep user assets private by default; use scoped, expiring upload/download URLs.
7. Record provider, model, duration, GPU type and estimated/actual cost per job.
8. Use explicit capability and license allowlists before enabling a model commercially.
9. Product adapters must fail independently; one provider outage must not take down the gateway.
10. Do not expose a product capability in the UI until its adapter passes integration tests.

## Initial implementation sequence
- [ ] Confirm repository owners, default branches, runtime stacks and license files.
- [ ] Add API service skeleton and health/readiness endpoints.
- [ ] Add authentication/session contract.
- [ ] Add job lifecycle and event schema.
- [ ] Add model/provider adapter interface and mock adapter.
- [ ] Add one real integration at a time, beginning with the existing AI Content Studio gateway.
- [ ] Add staging deployment, secrets management and end-to-end tests.
- [ ] Only then connect MusicVision, Seed-VC, GPU workers and other products.

## Acceptance criteria for first milestone
- API starts locally and in CI.
- Health and readiness endpoints return correct status.
- Mock job can be submitted, queried, cancelled and completed.
- Job events are persisted and correlate with a project.
- No secrets are committed.
- Tests cover invalid input, duplicate idempotency key, provider timeout and provider failure.

## Out of scope for this starter
- Production deployment.
- Live Qwen inference.
- GPU provisioning.
- Unified billing or payment collection.
- Cross-app single sign-on.
- Claims that any unverified product is operational.
