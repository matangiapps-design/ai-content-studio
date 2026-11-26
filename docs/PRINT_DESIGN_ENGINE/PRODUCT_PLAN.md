# MATANGI AI Print Design Engine

## Purpose

Add a print-focused design workspace to MATANGI Creator Studio. The user supplies a product image or brand assets, the engine builds a reusable Product Board, then generates campaign artwork from structured commands. Outputs must be reviewed and preflighted before print or publication.

## Scope

- Product Board: analyse uploaded product images for shape, proportions, packaging, materials, colours, logo placement and approved viewpoints.
- Command library: import the source book's 200 commands only after the original PDF is supplied and checked. Preserve source wording and attribution as permitted by the book's licence.
- Additional library: author 100 original adult-industry campaign commands for non-explicit, age-gated, adult-only commercial contexts. These are new commands, not claims about the source book.
- Campaign builder: brand, product, price, offer, location, website, language, CTA, audience and output format.
- Website intelligence: public-page research with source URLs, dates, confidence and human review.
- Image generation: provider adapter, reference-image control and variation generation.
- Print production: format presets, safe area, bleed, resolution, colour-space guidance and export validation.
- Compliance: content classification, age-gating, consent/licensing checks and destination-platform policy checks.

## User workflow

1. **Create project** — select brand, campaign and output channel.
2. **Build Product Board** — upload authorised reference images; extract visual attributes and approved camera views.
3. **Choose command** — search/filter by category, intent, format and platform.
4. **Complete campaign brief** — fill required metadata; validate missing fields.
5. **Research (optional)** — collect public competitor/product/trend evidence; cite every fact with URL and capture date.
6. **Generate** — create one or more drafts with reference consistency.
7. **Review** — inspect copy, brand accuracy, visual quality, safety and platform constraints.
8. **Preflight and export** — validate canvas dimensions, bleed, safe margins, resolution and file format.
9. **Archive** — save the prompt, source references, output version and review record.

## Command record schema

Each command should be structured data rather than a free-form slash-command string alone.

- `id`: stable slug, e.g. `business-flyer`
- `name`: display name
- `category`: controlled category
- `prompt_template`: full generation instructions with named placeholders
- `required_inputs` / `optional_inputs`: typed fields and validation rules
- `supported_formats`: A4, A3, poster, banner, social ratios, etc.
- `print_profile`: dimensions, bleed, safe area, resolution and colour-space defaults
- `content_classification`: general, adult-non-explicit, restricted, disallowed
- `platform_constraints`: destination-specific restrictions and last-checked date
- `source`: book/page/licence or original-author metadata
- `version`, `created_at`, `updated_at`

Do not mark the source 200 commands as imported until the original book file has been provided and reviewed.

## Suggested service boundaries

- `/api/print/projects` — campaign projects and metadata
- `/api/print/product-boards` — product reference analysis and board versions
- `/api/print/commands` — command search, validation and versioning
- `/api/print/research` — public source research and evidence records
- `/api/print/generations` — generation jobs, status and output assets
- `/api/print/preflight` — print validation report
- `/api/print/exports` — approved export packages

Keep provider credentials server-side. Add request IDs, timeouts, retry limits, cost ceilings and audit logging.

## Research evidence record

For each finding store: `source_url`, `page_title`, `retrieved_at`, `published_at` (when available), `quoted_or_observed_fact`, `summary`, `confidence`, `region`, and `review_status`. Prefer official pricing, product and policy pages. Respect robots.txt, terms, access controls and rate limits; do not bypass logins or paywalls, or collect private personal data.

## Safety and compliance gates

- Adult-industry commands are limited to lawful, non-explicit promotional design for adults and adult-only services/products.
- Do not generate sexual imagery involving minors, apparent minors, or age-ambiguous people.
- Do not create non-consensual intimate imagery, sexual deepfakes, coercive material or content using a real person's likeness without documented permission.
- Do not treat a design as legally cleared merely because an AI classifier passed it.
- Verify applicable law and each destination platform's current rules before a campaign is marked publishable.
- For age-restricted products/services, require age-gating and a region/platform policy check.
- Keep research factual, sourced and clearly separated from model-generated recommendations.

## Acceptance criteria

- A Product Board can be created, versioned and reused across at least three commands without changing the product's essential appearance.
- Commands have validated required fields and format-specific output instructions.
- The source 200-command collection is traceable to the supplied book; missing source material is a visible blocker, not silently fabricated.
- The 100 additional commands are original, non-explicit and content-classified.
- Research findings include working source URLs and capture dates.
- Preflight catches wrong dimensions, insufficient resolution, unsafe margins and missing bleed where applicable.
- UI supports desktop and mobile layouts, keyboard navigation and readable contrast.
- Tests cover prompt assembly, schema validation, job failures, safety gates and print preflight.

## Dependencies / open decisions

- Original book PDF and its reuse/licensing terms are required to import the first 200 commands.
- Choose the image-generation provider(s) and confirm available model/API credentials.
- Confirm supported export formats and whether CMYK/PDF/X conversion will be server-side.
- Connect Figma MCP in the user's IDE to read/write native Figma frames; this chat currently has GitHub and Canva access, not a live Figma canvas connection.
