# Charity Compliance Tracker

A dashboard of UK charity regulation — guidance, enforcement cases and sanctions
— pulled together from eleven regulator sources into one searchable place.

A Python pipeline fetches from each regulator, normalises everything to a common
shape, and writes a single CSV. The Next.js app reads that CSV.

## Pages

| Page | What it shows |
| --- | --- |
| `/` | Overview and headline figures |
| `/explorer` | Searchable, filterable table of every record |
| `/cases` | Enforcement cases |
| `/charity` | Records grouped by charity |
| `/sanctions` | Sanctions designations |
| `/analytics` | Charts and breakdowns |
| `/about` | Background |

## Running it

You need Node.js 18+.

```bash
npm install
npm run dev
```

Open http://localhost:3000. The app reads `data/charity_policies.csv`, which is
already committed, so it works without running the pipeline.

## Refreshing the data

```bash
cd python-scripts
pip install -r requirements.txt
python run_charity_update.py
```

This runs every source adapter, merges the results with what is already in
`data/charity_policies.csv` (updating a record only when the incoming one is
newer), and writes the file back sorted by date. It prints a count per regulator
when it finishes.

Useful flags:

```bash
python run_charity_update.py --dry-run        # fetch and merge, write nothing
python run_charity_update.py --source ico     # one source only
```

Source keys: `cc`, `cc_guidance`, `ico`, `hse`, `hmrc`, `fr`, `safeguarding`,
`data_protection`, `financial_reporting`, `risk_management`, `anti_fraud`.

### The other scripts

| Script | What it does |
| --- | --- |
| `build_analytics.py` | Regenerates `data/analytics.json` for the analytics page |
| `enrich_with_register_api.py` | Adds detail from the Charity Commission register API |
| `remove_duplicates.py` | Clears duplicate records out of the CSV |
| `fix_dates.py` | Normalises inconsistent date formats |

## Sources

Charity Commission (register and guidance), ICO, HSE, HMRC, the Fundraising
Regulator, and sources covering safeguarding, data protection, financial
reporting, risk management and anti-fraud. One adapter each, in
`python-scripts/adapters/`.

## Project layout

```
app/                   Next.js App Router pages and API routes
components/            Shared UI components
lib/                   Data loading and helpers
types/                 TypeScript types
data/
  charity_policies.csv The dataset the app reads
  analytics.json       Pre-computed analytics
  staging/             Raw adapter output
python-scripts/
  run_charity_update.py  Pipeline orchestrator
  adapters/              One adapter per source
```

## Record shape

Each row carries: `id`, `title`, `summary`, `source_url`, `published_date`,
`last_updated`, `regulator`, `domain`, `document_type`, `charity_number`,
`charity_name`, `charity_income_band`, `risk_level`, `case_id`, `case_status`,
`outcome`, `issues_identified`, `sanctions_regime`, `designated_by`,
`fine_amount`, `keywords`.

## Commands

| Command | What it does |
| --- | --- |
| `npm run dev` | Dev server |
| `npm run build` | Production build |
| `npm start` | Serve the production build |
| `npm run lint` | Lint |

Built with Next.js 13 (App Router), TypeScript, Tailwind CSS, Recharts and D3.
