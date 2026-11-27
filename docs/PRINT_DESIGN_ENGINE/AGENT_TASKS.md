# MATANGI Print Design Engine — Agent Task Board

**Repository:** matangiapps-design/ai-content-studio  
**Working branch:** feat/matangi-print-design-engine-20261126  
**Status:** Planning handoff committed; implementation agents not yet connected.

> GitHub Issues are disabled for this repository (GitHub API returned HTTP 410). This file is the task board until Issues/Projects are enabled. Agent labels describe specialist roles; they are not assigned GitHub bot accounts.

## Parallel workstreams

| ID | Specialist | Primary output | Depends on | Status |
|---|---|---|---|---|
| A0 | Technical Lead / Integrator | Architecture, schema, API contracts, merge plan | None | Ready |
| A1 | Product Designer / Figma | Figma pages, responsive frames, component handoff | Figma MCP connection | Blocked: no Figma connection yet |
| A2 | Command Librarian | Typed schema + command search + command catalog | Original book PDF for source 200 | Partially blocked: PDF missing |
| A3 | Product Board / Image Pipeline | Product Board, reference lock, generation adapter | A0 API contracts | Ready after A0 |
| A4 | Web Research | Source-cited public market/policy research | Evidence schema from A0 | Ready after A0 |
| A5 | Print Production | Format presets, preflight and export | A0 data model | Ready after A0 |
| A6 | Safety / QA / Release | Safety gates, test matrix, regression and release report | Can start test design immediately | Ready |

## A0 — Technical Lead / Integrator
- [ ] Inspect existing Next.js and FastAPI modules and map safe integration points.
- [ ] Define data entities for Campaign, ProductBoard, Command, ResearchEvidence, GenerationJob, PreflightReport and Export.
- [ ] Define API contracts and error states.
- [ ] Add a feature flag; preserve existing video workflows.
- [ ] Publish interface contracts for A1–A6.

**Acceptance:** architecture decision record, API examples, integration map, no regression to existing content pipelines.

## A1 — Product Designer / Figma
- [ ] Create Figma file: MATANGI Print Studio.
- [ ] Pages: Foundations, Overview, Campaign Editor, Product Board, Command Library, Research, Preflight & Export, Mobile.
- [ ] Design desktop 1440×900 and mobile 390×844.
- [ ] Cover empty, loading, error, blocked and completed states.
- [ ] Deliver components, tokens and implementation notes.
- [ ] Add Figma frame links to the design handoff.

**Acceptance:** coherent, responsive design system consistent with DESIGN.md; accessible contrast, keyboard focus and readable type.

**Blocker:** connect the official Figma MCP server or provide a Figma file. The GitHub Figma repositories are implementation references only; they do not grant access to the user's Figma workspace.

## A2 — Command Librarian
- [ ] Implement typed command schema and validation.
- [ ] Build search, category and output-format filters.
- [ ] Import the actual 200 source commands only after receiving the PDF and reviewing reuse/licensing terms.
- [ ] Author a separate 100-command extension for non-explicit, adult-only commercial campaigns.
- [ ] Record source attribution, page, version and content classification.

**Acceptance:** every active command has a full prompt template, typed inputs, format constraints and provenance.

**Blocker:** source PDF not uploaded. Do not fabricate the source 200.

## A3 — Product Board / Image Pipeline
- [ ] Implement reference image upload and storage with user-rights confirmation.
- [ ] Extract product shape, proportions, packaging, materials, colours, logo placement and angles.
- [ ] Add versioned Product Boards and identity lock.
- [ ] Add provider adapter and generation job lifecycle.
- [ ] Persist prompts, model/provider, source asset IDs, outputs, status, errors and cost metadata.

**Acceptance:** same Product Board can be reused across at least three command runs while preserving product identity.

## A4 — Web Research
- [ ] Discover public competitor, product, pricing, trend and official policy pages.
- [ ] Store URL, page title, captured date, publish date (when available), region, factual note, confidence and review status.
- [ ] Separate observed facts from model-generated recommendations.
- [ ] Flag stale and unverifiable data.
- [ ] Respect site terms, robots.txt, rate limits and access restrictions; no login/paywall bypass or private personal-data collection.

**Acceptance:** every displayed factual finding has a source URL and retrieval date.

## A5 — Print Production
- [ ] Add A4, A3, poster, banner and social output presets.
- [ ] Store physical dimensions, bleed, safe margin, target resolution and colour profile per format.
- [ ] Validate dimensions, aspect ratio, image resolution, text-safe area and bleed.
- [ ] Separate RGB proof previews from true CMYK/PDF-X output.
- [ ] Package approved export with preflight report and version metadata.

**Acceptance:** automated tests catch wrong dimensions, inadequate resolution, missing bleed and unsafe margins; export clearly identifies colour mode.

## A6 — Safety / QA / Release
- [ ] Build classification for general and adult-industry design prompts.
- [ ] Keep adult-industry work non-explicit and strictly adult-only.
- [ ] Block minors, apparent minors, age-ambiguous depictions, non-consensual intimate imagery and sexual deepfakes.
- [ ] Add region/platform policy-check records with source and last-checked date.
- [ ] Test schema validation, prompt building, image jobs, research provenance, print preflight and video regression.
- [ ] Publish regression report and release checklist.

**Acceptance:** blocking safety/preflight failures cannot be bypassed silently; tests and known limitations are documented.

## Recommended 24-hour sequence
- **Hours 0–3:** A0 architecture and A1 design foundations; A6 starts test matrix.
- **Hours 3–7:** A1 core screens; A2 command schema; A4 evidence schema.
- **Hours 7–12:** A3 Product Board; A4 research connectors; A5 print profiles.
- **Hours 12–18:** connect APIs and UI; command catalog work; generation/preflight integration.
- **Hours 18–22:** safety gates, integration tests and responsive QA.
- **Hours 22–24:** fix blockers, build, review, release report.

The schedule is a target for a staffed execution sprint, not a claim that autonomous agents are running now.

## Required inputs to unblock
1. Original PDF: 200 AI Print Design Command Proposals.
2. Figma workspace/file access and Figma MCP connection, if native Figma output is required.
3. Selected image-generation provider and server-side credentials.
4. Required export targets (PNG/PDF, bleed requirements, whether CMYK/PDF-X is mandatory).