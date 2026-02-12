# AI Daily

AI Daily now supports two parallel workflows:
- OpenClaw data workflow (organization, snapshots, image assets, adapters)
- Codex design workflow (Next.js v2 frontend)

## Repository structure

```text
ai-daily/
├── apps/web/                   # Next.js App Router + TypeScript + Tailwind v2 frontend
├── config/
│   ├── cron-config.json
│   ├── x-config.json
│   ├── x-mock-snapshot.json
│   └── workflow-split.json
├── docs/
│   ├── architecture-v2.md
│   └── design-tokens.md
├── scripts/
│   ├── build-site.py
│   ├── fetch-paper-images.py
│   ├── fetch-x-snapshot.py
│   ├── build-issue-data.py
│   ├── run-openclaw-pipeline.sh
│   ├── run-codex-design.sh
│   └── run-daily-pipeline.sh
└── issues/YYYY-MM-DD/
    ├── papers/*.md
    ├── assets/figures/*
    ├── assets/figures/manifest.json
    ├── issue-data.json
    └── index.html (legacy)
```

## OpenClaw workflow (data side)

Run daily data organization with image fallback and adapter output:

```bash
ISSUE_DATE=2026-02-12 X_MODE=mock ./scripts/run-openclaw-pipeline.sh
```

This runs:
1. HF ingest placeholder hook
2. X snapshot fetch (`fetch-x-snapshot.py`)
3. Paper image fetch with fallback (`fetch-paper-images.py`)
4. Frontend adapter generation (`build-issue-data.py`)

## Codex workflow (design side)

Start local design iteration server:

```bash
./scripts/run-codex-design.sh
```

Run typecheck + production build:

```bash
MODE=build ./scripts/run-codex-design.sh
```

Equivalent direct commands:

```bash
cd apps/web
npm install
npm run dev
npm run typecheck
npm run build
```

## Frontend pages

- Index page: `/`
- Article page: `/issues/[date]/[paperId]`

The frontend reads `issues/YYYY-MM-DD/issue-data.json` first.
If adapter is missing, it falls back to existing markdown/json in `issues/`.

## Dark mode + accessibility

- Dark mode supports `prefers-color-scheme` and manual toggle.
- Semantic HTML and keyboard-visible focus styles are built into shared components.
- Design token definitions live in `docs/design-tokens.md` and `apps/web/app/globals.css`.

## Legacy compatibility and migration

Existing static site pipeline still works:

```bash
ISSUE_DATE=2026-02-12 X_MODE=mock ./scripts/run-daily-pipeline.sh
```

`run-daily-pipeline.sh` now includes image + adapter steps before `build-site.py`, so legacy output remains available while v2 frontend is added.
