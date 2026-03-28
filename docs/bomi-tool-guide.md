# bomi Tool Guide

This project uses [`bomi`](https://github.com/somebox/bomi) to manage JLCPCB/LCSC part research and the project BOM.

## Project Files

- Project config: `.bomi/project.yaml`
- Refreshed BOM docs: `docs/BOM_rgb-spotlight.md` and `docs/BOM_rgb-spotlight.csv`
- Datasheet summaries: `docs/datasheets/*.md`

## Core Commands

```bash
bomi status
bomi fetch --all --force
bomi list --check
bomi list --format markdown
bomi list --format csv
```

## Typical Refresh Flow

Run this from the repository root:

```bash
# 1) Refresh all selected parts from the live catalog
bomi fetch --all --force

# 2) Check BOM entries against current catalog data
bomi list --check

# 3) Export updated docs
bomi list --format markdown > docs/BOM_rgb-spotlight.md
bomi list --format csv > docs/BOM_rgb-spotlight.csv
```

## Managing BOM Entries

```bash
# add or update entries
bomi select C114581 --ref U1 --qty 1 --notes "WS2811 controller"
bomi select C350557 --ref U7 --qty 1 --notes "DIN level shifter"

# remove or rename entries
bomi deselect U7
bomi relabel U7 U8
```

## Datasheets

```bash
# download PDFs for all project parts
bomi datasheet --all --pdf -o docs/datasheets/

# also generate summaries (requires OpenRouter key in bomi config)
bomi datasheet --all --pdf --summary -o docs/datasheets/
```

## Migration Note

This repository previously stored BOM config at `.jlcpcb/project.yaml`. The active config is now `.bomi/project.yaml`.
