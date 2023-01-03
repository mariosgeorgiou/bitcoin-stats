import json
from coinbase.wallet.client import Client
import logging
from predict import predict_next_day, get_price
from datetime import datetime
import yfinance as yf
from data import generate_betas

# configure the logging module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_all_crypto_tickers():

    # Open the keys file
    with open(".keys", "r") as f:
        keys = json.load(f)["coinbase"]

    api_key = keys["COINBASE_API_KEY"]
    api_secret = keys["COINBASE_API_SECRET"]

    client = Client(api_key, api_secret)

    accounts = client.get_accounts()["data"]
    yahoo_tickers = []
    unavailable = {
        "PAX",
        "COMP",
        "CGLD",
        "MASK",
        "GMT",
        "GRT",
        "SYN",
        "SYN",
        "IMX",
        "SUPER",
        "USD",
    }
    for account in accounts:
        currency = account["currency"]
        if currency not in unavailable and 'USD' not in currency:
            yahoo_tickers.append(currency + "-USD")

    return yahoo_tickers

def main():
    # TODO: Load the keys to the docker container as environment variables using --build-arg
    # api_key = os.getenv("COINBASE_API_KEY")
    # api_secret = os.getenv("COINBASE_API_SECRET")

    # Open the keys file
    with open(".keys", "r") as f:
        keys = json.load(f)["coinbase"]

    api_key = keys["COINBASE_API_KEY"]
    api_secret = keys["COINBASE_API_SECRET"]

    client = Client(api_key, api_secret)

    accounts = client.get_accounts()["data"]
    yahoo_tickers = []
    unavailable = {
        "PAX",
        "COMP",
        "CGLD",
        "MASK",
        "GMT",
        "GRT",
        "SYN",
        "SYN",
        "IMX",
        "SUPER",
        "USD",
    }
    for account in accounts:
        currency = account["currency"]
        if currency not in unavailable and 'USD' not in currency:
            yahoo_tickers.append(currency + "-USD")

    index = 'BTC-USD'

    betas = generate_betas(yahoo_tickers, index, '2020-10-17')

    betas.to_csv('betas.csv')


if __name__ == "__main__":
    main()
