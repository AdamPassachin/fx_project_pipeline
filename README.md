# FX Rates Pipeline

A small Python pipeline that fetches daily foreign-exchange rates from the European Central Bank (ECB) from 2018 and onwards, calculates all currency cross-rates, and stores the results in DuckDB.

Currencies: `NOK`, `EUR`, `SEK`, `PLN`, `RON`, `DKK`, `CZK`.

## What it does

1. Fetches daily EUR-based rates from the ECB API.
2. Keeps the requested currencies and adds EUR with a value of `1.0`.
3. Calculates all 42 directed currency pairs for each complete observation date.
4. Loads the results into a persistent DuckDB database.

ECB publishes rates on working days, so weekends and some holidays are not included.

## Requirements

- Python 3.11 or newer
- Git

No API key is required.

## Setup

Clone the repository:

```bash
git clone https://github.com/AdamPassachin/fx_project.git
cd fx_project
```

Create and activate a virtual environment.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the pipeline

```bash
python pipeline.py
```

On macOS/Linux, `python3 pipeline.py` also works.

The pipeline creates:

```text
data/fx_rates.duckdb
```

It is safe to run the pipeline again. Existing rows with the same date and currency pair are replaced instead of duplicated.

## Database model

`dim_currency` contains the currency codes and names.

`fact_fx_rate` contains:

```text
rate_date
base_currency
quote_currency
rate
source
loaded_at
```

The rate means:

```text
1 base_currency = rate quote_currency
```

For example, `base_currency = SEK`, `quote_currency = DKK`, and `rate = 0.68` means `1 SEK = 0.68 DKK`.

## Query the database

If the DuckDB command-line client is installed:

```bash
duckdb data/fx_rates.duckdb
```

Inside DuckDB:

```text
.tables
.schema fact_fx_rate
.read queries.sql
.quit
```

Example query:

```sql
SELECT
    rate_date,
    base_currency,
    quote_currency,
    rate
FROM fact_fx_rate
WHERE base_currency = 'SEK'
  AND quote_currency = 'EUR'
ORDER BY rate_date DESC
LIMIT 10;
```

## Validate the output

Check the row count and date range:

```sql
SELECT
    COUNT(*) AS row_count,
    MIN(rate_date) AS first_date,
    MAX(rate_date) AS last_date
FROM fact_fx_rate;
```

Check that every retained date has all 42 directed currency pairs:

```sql
SELECT
    rate_date,
    COUNT(*) AS pair_count
FROM fact_fx_rate
GROUP BY rate_date
HAVING COUNT(*) <> 42;
```

A valid load returns no rows from the second query.

## Project files

```text
pipeline.py       Fetches, transforms, and loads the rates
queries.sql       Example and validation queries
requirements.txt  Python dependencies
data/             Generated DuckDB database
```

The database file is generated locally and is not required in Git. Another user can recreate it by running `pipeline.py`.
