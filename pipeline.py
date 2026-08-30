import requests
import pandas as pd
from io import StringIO
import duckdb

ECB_url = 'https://data-api.ecb.europa.eu/service/data/EXR/D.NOK+SEK+PLN+RON+DKK+CZK.EUR.SP00.A?startPeriod=2024-01-01&format=csvdata&detail=dataonly'
DATABASE_PATH = "data/fx_rates.duckdb"

def fetch_ecb_rates():

    response = requests.get(ECB_url)
    response.raise_for_status()

    raw_df = pd.read_csv(StringIO(response.text))
    raw_df = raw_df[["CURRENCY", "TIME_PERIOD", "OBS_VALUE"]].copy()
    raw_df = raw_df.rename(columns={"CURRENCY": "currency_code", "TIME_PERIOD": "rate_date","OBS_VALUE": "rate_against_eur"})

    eur_df = (
        raw_df[["rate_date"]]
        .drop_duplicates()
        .assign(
            currency_code="EUR",
            rate_against_eur=1.0,
        )
    )
    
    rates_with_eur_df = pd.concat(
        [raw_df, eur_df],
        ignore_index=True,
    )

    return rates_with_eur_df


def cross_rate_rates(rates_with_eur_df):
    base_df = rates_with_eur_df.rename(columns={
        "currency_code" : "base_currency",
        "rate_against_eur" : "base_rate"
    })

    quote_df = rates_with_eur_df.rename(columns={
            "currency_code" : "quote_currency",
            "rate_against_eur" : "quote_rate"
        })

    cross_rates_df = base_df.merge(
        quote_df,
        on="rate_date",
    )

    cross_rates_df = cross_rates_df[
        cross_rates_df["base_currency"] != cross_rates_df["quote_currency"]
    ].copy()

    cross_rates_df["rate"] = (cross_rates_df["quote_rate"] / cross_rates_df["base_rate"])

    cross_rates_df = cross_rates_df[["rate_date","base_currency","quote_currency","rate"]].copy()

    return cross_rates_df

def load_to_db(cross_rates_df):
    connection = duckdb.connect(DATABASE_PATH)

    connection.execute("""CREATE TABLE IF NOT EXISTS dim_currency (
        currency_code VARCHAR PRIMARY KEY,
        currency_name VARCHAR NOT NULL
    )""")

    connection.execute("""
    INSERT OR IGNORE INTO dim_currency VALUES
            ('NOK', 'Norwegian krone'),
            ('EUR', 'Euro'),
            ('SEK', 'Swedish krona'),
            ('PLN', 'Polish zloty'),
            ('RON', 'Romanian leu'),
            ('DKK', 'Danish krone'),
            ('CZK', 'Czech koruna')
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS fact_fx_rate (
            rate_date DATE NOT NULL,
            base_currency VARCHAR NOT NULL,
            quote_currency VARCHAR NOT NULL,
            rate DOUBLE NOT NULL,
            ingestion_ts TIMESTAMP NOT NULL,

            PRIMARY KEY (
                rate_date,
                base_currency,
                quote_currency
            )
        )
    """)

    connection.register("cross_rates_df",cross_rates_df)

    connection.execute("""INSERT OR REPLACE INTO fact_fx_rate
    SELECT
        CAST(rate_date AS DATE),
        base_currency,
        quote_currency,
        rate,
        CURRENT_TIMESTAMP
    FROM
        cross_rates_df
    """)


def main():
    rates_with_eur_df = fetch_ecb_rates()
    cross_rates_df = cross_rate_rates(rates_with_eur_df)
    load_to_db(cross_rates_df)
    

if __name__ == '__main__':
    main()