# Agent Work Contract — MATANGI Print Design Engine

The work is divided into specialist lanes. Each lane owns its deliverables, tests and handoff notes. The agent titles below are work roles, not GitHub accounts; the current repository connection cannot start or assign autonomous bot identities by itself.

## Agent 0 — Technical Lead / Integrator
**Owns:** module boundaries, API contracts, data model, dependency map, merge order and final acceptance.
**Deliver:** architecture decision record, interface contracts, integration checklist.
**Must not:** invent the source book's 200 commands or expose provider secrets.

## Agent 1 — Product Designer / Figma
**Owns:** responsive product flows, frames, design tokens, editor states and accessibility.
**Deliver:** Figma file or frames, component inventory, interaction notes, implementation handoff.
**References:** Figma MCP server guide and this repository's `DESIGN.md`.
**Blocker:** connect Figma MCP / provide a Figma file before claiming native Figma frames are complete.

## Agent 2 — Command Librarian
**Owns:** typed command schema, command search and validation, category metadata and original 100-command extension.
**Deliver:** versioned command JSON/MD, schema tests and source attribution.
**Blocker:** original book PDF is required to import the actual 200 source commands.

## Agent 3 — Product Board / Image Pipeline
**Owns:** upload flow, product attribute analysis, reference locking, image-generation adapters and variation jobs.
**Deliver:** API adapter, job lifecycle, sample outputs and consistency tests.
**Must:** keep all model/API keys on the server; record image provenance and user rights confirmation.

## Agent 4 — Web Research
**Owns:** public-source discovery, competitor/product/policy research, evidence storage and freshness checks.
**Deliver:** source-cited research records, extraction tests and region filters.
**Must:** respect site terms, robots.txt, rate limits and access controls; no private data, login bypass or paywall circumvention.

## Agent 5 — Print Production / Preflight
**Owns:** canvas sizing, bleed, safe margins, resolution, colour handling and export packages.
**Deliver:** format profiles, preflight report, validation tests and sample export.
**Must:** distinguish RGB previews from any actual CMYK/PDF-X print deliverable.

## Agent 6 — Safety / QA / Release
**Owns:** content classification, age-gate/policy checks, unit/integration tests, security and release gates.
**Deliver:** safety cases, QA matrix, regression report and release checklist.
**Must:** adult-industry designs stay non-explicit and adult-only; block minors, non-consensual intimate content and sexual deepfakes.

## Parallelisation and dependencies

- Agents 1, 2, 4 and 5 can draft independently against the product plan.
- Agent 3 defines its interfaces with Agent 0 before implementation.
- Agent 6 creates test cases early; it reviews all lanes before release.
- Agent 0 integrates after each contract is stable.
- Do not merge directly to `main`; use feature branches and pull requests.

## Definition of done

A lane is done only when its deliverables are committed, tests or review checks are recorded, known limitations are disclosed, and Agent 0 accepts the handoff.
