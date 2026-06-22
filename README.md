# Kaleidoscope

> An automated pipeline that generates original geometric/kaleidoscopic patterns every day and ships them to print-on-demand.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI Generation](https://img.shields.io/badge/AI-Image%20Generation-8b5cf6?style=for-the-badge)
![Automation](https://img.shields.io/badge/Automation-Daily%20Pipeline-22c55e?style=for-the-badge)

Kaleidoscope runs a fully automated daily workflow: analyze trends, generate new patterns with AI, apply geometric transforms, and deploy the results to print-on-demand (POD) platforms.

## Pipeline

```
trend analysis → AI generation → geometric transforms → POD deployment
```

- **Prompt engine** — driven by curated word lists (`data/word_lists/`): colors, cultural styles, nature elements, flora, fauna, psychedelic motifs, and more.
- **Geometric masks** — kaleidoscopic symmetry via `data/masks/` (hexagon, rhombus 36°/72°, triangle).
- **Agent-orchestrated** — spec-workflow agents under `.claude/` coordinate requirements → design → implementation → test.
- **Scheduled** — `daily_generation` workflow runs at a configured time each day.

## Docs

Full design lives in [`docs/`](docs/):

`00_executive_summary` · `01_prd` · `02_mathematical_foundations` · `03_project_structure` · `04_agent_architecture` · `07_cultural_styles_reference` — plus a `future/` set covering adversarial validation, monetization, and roadmap.

## Prerequisites

- API keys in `config/api_keys.yaml`
- A database connection
- At least one POD platform enabled

## Tech stack

Python · AI image generation · agent orchestration (spec-workflow)
