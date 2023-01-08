import json
from coinbase.wallet.client import Client
import coinbase.wallet.error
import logging
from predict import predict_next_day, get_price
from datetime import datetime
import yfinance as yf
from data import generate_betas

# configure the logging module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_client():
    # Open the keys file
    with open(".keys", "r") as f:
        keys = json.load(f)["coinbase"]

    api_key = keys["COINBASE_API_KEY"]
    api_secret = keys["COINBASE_API_SECRET"]

    client = Client(api_key, api_secret)
    return client


client = get_client()


def get_all_crypto_tickers():

    client = get_client()

    currencies = client.get_exchange_rates()["rates"].keys()
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
    unwanted = {
        "00",
    }

    for ticker in currencies:
        if ticker not in unavailable and ticker not in unwanted:
            yahoo_tickers.append(ticker + "-USD")

    return yahoo_tickers


def main():

    client = get_client()

    yahoo_tickers = get_all_crypto_tickers()

    index = "BTC-USD"

    betas = generate_betas(yahoo_tickers, index, "2020-10-17")

    betas.to_csv("betas.csv")

    low_betas = betas[(betas < 0.7) & (betas > 0.6)].dropna()
    low_betas.to_csv("lows.csv")
    high_betas = betas[(betas > 1.1)].dropna()
    high_betas.to_csv("highs.csv")

    for ticker in low_betas.index:
        coinbase_ticker = ticker.split("-")[0]
        try:
            account = client.get_account(coinbase_ticker)
        except coinbase.wallet.error.NotFoundError:
            logging.info(f'Cannot trade {coinbase_ticker}')
        else:
            logging.info(f'Buying {coinbase_ticker}')
            order = account.buy(amount="1", currency="USD")
            logging.info(f"order details: {order}")

    for ticker in high_betas.index:
        coinbase_ticker = ticker.split("-")[0]        
        try:
            account = client.get_account(coinbase_ticker)
        except coinbase.wallet.error.NotFoundError:
            logging.info(f'Cannot trade {coinbase_ticker}')
        else:
            balance = float(account["native_balance"]["amount"])
            if balance > 1.0:
                logging.info(f'Selling {coinbase_ticker}')
                order = account.sell(amount="1", currency="USD")
                logging.info(f"order details: {order}")


if __name__ == "__main__":
    main()
