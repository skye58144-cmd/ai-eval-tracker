# AI Eval Tracker

This repository tracks key AI evaluation metrics and publishes a static dashboard via GitHub Pages. A scheduled GitHub Actions workflow fetches data from public sources, parses metrics, appends them to a history JSONL file, and keeps a latest snapshot for the dashboard.

## Tracked metrics
- **METR time horizon**: 50% and 80% success horizons (minutes) with confidence intervals when available.
- **GDPval win rate**: Table 2 model win rates from the GDPval arXiv HTML.
- **ARC-AGI-2 private SOTA**: Latest percent and cost-per-task from the ARC Prize results analysis.

## Repository structure
- `src/`: Data fetching, parsing, and storage utilities.
- `docs/`: Static site served by GitHub Pages (historical data in `docs/data/`).
- `state/cache.json`: Cached ETag/Last-Modified/content hashes for conditional requests.
- `.github/workflows/update.yml`: Scheduled updater that commits refreshed data.

## Setup
1. Install Python 3.11+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the tracker locally:
   ```bash
   python -m src.run
   ```
4. Serve the dashboard locally (optional):
   ```bash
   python -m http.server --directory docs 8000
   ```
   Then visit http://localhost:8000.

## GitHub Pages
Enable GitHub Pages to serve from the `docs/` folder. The dashboard reads `docs/data/latest.json` and `docs/data/metrics.jsonl` directly from this directory.

## Workflow schedule
The updater runs every six hours and on manual dispatch. It commits updated data files back to the repository using a bot identity.
