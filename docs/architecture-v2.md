# V2 Workflow Split

## Responsibilities
- OpenClaw side (`scripts/run-openclaw-pipeline.sh`):
  - Fetch/organize daily data
  - Fetch X snapshot
  - Fetch paper images with robust fallback
  - Build frontend adapter (`issue-data.json`)
- Codex side (`scripts/run-codex-design.sh`):
  - Iterate and build Next.js design frontend
  - Validate TypeScript/build output

## Data flow
1. Inputs are maintained in `issues/YYYY-MM-DD/papers/*.md` (+ optional `digest.md` / `x-snapshot.json`).
2. `scripts/fetch-paper-images.py` writes image assets to `issues/YYYY-MM-DD/assets/figures/` with `manifest.json`.
3. `scripts/build-issue-data.py` writes `issues/YYYY-MM-DD/issue-data.json`.
4. Next frontend loads `issue-data.json` when present, else falls back to raw markdown parsing.

## Image fallback strategy
For each paper:
1. Resolve Hugging Face paper page URL from front matter / paper ID.
2. Parse OG/Twitter image metadata from HF page HTML.
3. Download image if valid metadata exists.
4. If unavailable or download fails, generate SVG placeholder thumb.
5. Store final image path and source in `assets/figures/manifest.json`.

## Compatibility
- Legacy static HTML generator (`scripts/build-site.py`) remains intact.
- Existing command `scripts/run-daily-pipeline.sh` now also runs image + adapter steps before building legacy pages.
