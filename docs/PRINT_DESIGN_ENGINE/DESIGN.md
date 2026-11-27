# MATANGI Print Studio — Design System

## Product feel

A premium, focused creative workstation: cinematic dark canvas, precise editor controls, generous spacing and clear production status. The interface should feel like a professional design application, not a generic admin dashboard. Avoid childish illustrations, oversized gradients, cluttered cards and tiny low-contrast text.

## Design tokens

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0B0D12` | App background |
| `--surface-1` | `#111722` | Sidebar and primary panels |
| `--surface-2` | `#182231` | Cards, editor rails and inputs |
| `--surface-3` | `#202C3D` | Hover/selected surfaces |
| `--text` | `#F4F6FA` | Primary text |
| `--muted` | `#A4AFBE` | Secondary text |
| `--border` | `#2B3748` | Dividers and outlines |
| `--accent` | `#A78BFA` | Primary creative action |
| `--accent-2` | `#56D6B5` | Success and completed states |
| `--warning` | `#F4B860` | Warnings |
| `--danger` | `#F07178` | Errors and blocked states |

Use colour intentionally. Status must also have an icon and text label; never rely on colour alone.

## Typography

- Primary family: Inter or a close system sans-serif fallback.
- Display headings: 28–36 px, medium/semibold, tight line-height.
- Section headings: 18–22 px, semibold.
- Body: 14–16 px with comfortable line-height.
- Metadata and helper labels: minimum 12 px; do not use tiny text for essential details.
- Use tabular numerals for prices, dimensions and generation counts.
- Keep campaign copy short and preview exact line breaks.

## Desktop workspace (1440 × 900 reference frame)

### 1. App shell
- Fixed left navigation rail: 232 px wide.
- Top bar: 64 px high with workspace breadcrumb, project switcher, help and account controls.
- Main content uses a 12-column grid, 24 px gutters and 32 px outer padding.
- Keep the editor canvas as the visual centre of gravity.

### 2. Navigation
- MATANGI mark and “Print Studio” label.
- Main links: Overview, Projects, Product Boards, Command Library, Research, Exports.
- Bottom area: Usage, Settings and support.
- Active item uses a restrained accent bar and tinted surface, not a large glowing pill.

### 3. Overview
- Title: “Print Studio”.
- Primary CTA: “New campaign”.
- Four compact metric panels: active campaigns, saved Product Boards, generated drafts and exports awaiting review.
- Recent projects in a clean table/list with thumbnail, project name, output format, updated time and status.
- A “Continue where you left off” section should be more prominent than decorative analytics.

### 4. Campaign editor
Three-column layout:
- Left rail (260 px): campaign inputs, brand/product metadata, CTA, location, website and language.
- Centre canvas (flex): selected artwork preview on a neutral checker/bleed frame; zoom and fit controls; toggle safe area and bleed.
- Right rail (300 px): command details, generation settings, Product Board selector, variants and quality checks.
- On narrow screens, rails become drawers; canvas remains full width.

### 5. Product Board
- Large reference-image gallery with approved angle chips.
- Product attributes shown as editable tags: primary colours, materials, packaging, shape, logo position and locked features.
- “Lock product identity” toggle must be visible and explain what is protected.
- Show source image provenance and whether the user has rights to use it.

### 6. Command library
- Search-first layout with category filters and format chips.
- Each command card shows purpose, required fields, supported formats and an example thumbnail.
- Command detail view displays the complete prompt template, inputs and source attribution.
- Adult-industry commands are separated by an explicit “Adult / 18+” category gate and use non-explicit preview imagery only.

### 7. Research panel
- Findings are rows with source favicon, source title, capture date, region and confidence.
- Provide “Open source” and “Use in brief” actions.
- Separate observed facts from AI-generated suggestions.
- Show stale or unverified findings as such.

### 8. Preflight / export
- Clear pass / warning / blocked groups for dimensions, resolution, colour, bleed, safe margin, copy and policy.
- Export button remains disabled while a blocking issue exists.
- Show exact output dimensions and format before download.
- Preserve a review/audit summary with the export.

## Components and interaction rules

- Buttons: primary filled accent, secondary outline, quiet text action; use consistent 40–44 px control height.
- Inputs: visible labels above fields; do not rely on placeholder-only labels.
- Cards: 12–16 px radius, 1 px border, subtle depth only.
- Tables: aligned columns, row hover, meaningful empty/loading/error states.
- Command palette: keyboard searchable, category-aware, exact command names.
- Generation jobs: show queued/running/failed/completed state, elapsed time and retry action.
- Toasts: concise and actionable; avoid success-only colour with no text.
- Confirmation required before replacing a Product Board, deleting a saved command or overwriting an approved export.

## Responsive behaviour

- Desktop ≥ 1200 px: persistent sidebar and three-column editor.
- Tablet 768–1199 px: compact sidebar; right settings in a drawer.
- Mobile < 768 px: bottom navigation or collapsible menu; single-column campaign flow; sticky Generate/Review action bar.
- Preview presets include 9:16, 4:5, 1:1, 16:9, A4 and A3. Print sizes must show physical dimensions in addition to aspect ratio.

## Accessibility

- WCAG AA contrast for normal text.
- Full keyboard access, visible focus, labelled controls and semantic headings.
- Do not convey statuses using colour alone.
- Reduced-motion preference respected.
- Screen-reader labels for preview zoom, crop, safe-area and bleed controls.

## Visual QA checklist

- No clipped labels, overlapping controls or horizontal page overflow at 360 px width.
- Text is readable at 100% zoom; essential labels are at least 12 px.
- Product preview is large enough to inspect packaging and logo placement.
- Safe-area/bleed guides are clearly distinguished.
- All loading, empty, error, blocked and success states are designed.
- Use real project/product thumbnails when available; otherwise use neutral, clearly labelled placeholders.

## Reference reading

These are implementation references, not assets to copy:
- Figma's official MCP server guide: https://github.com/figma/mcp-server-guide
- Figma Context MCP: https://github.com/GLips/Figma-Context-MCP
- AI-readable DESIGN.md examples: https://github.com/VoltAgent/awesome-design-md
