# PCMI Research

Python utilities for ingesting PCMI warranty datasets and running rule-based fraud and anomaly analyses on claims, contracts, sellers, servicers, VINs, invoices, and loss codes.

The repository intentionally tracks source code and lightweight project metadata only. Raw data, generated SQLite databases, parquet exports, model artifacts, virtual environments, and analysis outputs are ignored so the GitHub repository stays clean and reproducible.

## Project Layout

```text
.
|-- data/                 # local input data, not committed
|-- out/                  # generated outputs, not committed
|-- scripts/              # helper scripts
|-- src/                  # ingestion and analysis modules
|-- .env.example          # optional environment template
|-- requirements.txt      # Python dependencies
`-- README.md
```

## Environment

Recommended runtime:

- Python 3.10 or newer
- Git
- A local virtual environment named `.venv`

Python packages are listed in `requirements.txt`:

- `pandas>=2.0.0`
- `pyarrow>=14.0.0`
- `SQLAlchemy>=2.0.0`
- `python-dotenv>=1.0.1`

Optional local configuration can be copied from `.env.example`:

```text
DATA_DIR=./data
OUT_DIR=./out
SQLITE_PATH=./out/data.sqlite
CSV_SEP=,
CSV_ENCODING=utf-8
```

CLI flags override these environment values.

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Basic Ingestion

Place CSV or Excel files in `data/`, then run:

```bash
python -m src.main --data-dir ./data --out-dir ./out --db ./out/data.sqlite
```

This creates parquet files under `out/parquet/`, a SQLite database at `out/data.sqlite`, and schema summaries in `out/summaries.json`.

You can also run the helper script on macOS or Linux:

```bash
bash scripts/run_ingest.sh
```

## Expected Local Files

Put source datasets in `data/`. The current analysis scripts expect PCMI-style CSV tables such as claims, contracts, contract vehicles, coverage plans, sellers, servicers, product components, product loss codes, and product types.

Generated files are written to `out/`. These outputs are local artifacts and are not committed to GitHub.

## Analysis Scripts

- `src/fraud_p1_p4_sqlite.py`: rule-based fraud indicators for early pattern groups.
- `src/patterns_v2_p5to8.py`: additional claim, VIN, shop, cluster, and invoice pattern checks.
- `src/make_in_claims_tables.py`: builds claim-intersection tables.
- `src/map_6way_to_claims.py`: maps multi-pattern outputs back to claim records.
- `src/add_seller_to_intersections.py`, `src/attach_seller_to_p3p4p5p6p7p8.py`, and `src/join_p3p4p5p6p7p8_sellers.py`: attach seller context to flagged claim outputs.
- `src/import_overlap_csv_to_sqlite.py`, `src/load_overlap_to_sqlite.py`, `src/load_p3to8_to_sqlite.py`, and `src/load_contracts_table_quick.py`: SQLite loading helpers.
- `src/export_in_claims_csv.py`: exports filtered claim outputs.
- `scripts/peek_contracts.py`: quick SQLite inspection helper for contract tables.

## Data Policy

The following are excluded from Git:

- Raw input files in `data/`
- Generated files in `out/`
- SQLite databases, parquet files, model weights, archives, and cache files
- Local virtual environments and editor settings

If a collaborator needs to reproduce the outputs, share the required input data through an approved private data channel, install dependencies, and rerun the scripts locally.
