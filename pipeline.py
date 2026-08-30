import requests
import pandas as pd
from io import StringIO

ECB_url = 'https://data-api.ecb.europa.eu/service/data/EXR/D.NOK+SEK+PLN+RON+DKK+CZK.EUR.SP00.A?startPeriod=2024-01-01&format=csvdata&detail=dataonly'


def fetch_ecb_rates():

    response = requests.get(ECB_url)
    response.raise_for_status()

    raw_rates_df = pd.read_csv(StringIO(response.text))
    raw_rates_df = raw_rates_df["CURRENCY", "TIME_PERIOD", "OBS_VALUE"]

    return raw_rates_df

def main():
    raw_rates_df = fetch_ecb_rates()


if __name__ == '__main__':
    main()