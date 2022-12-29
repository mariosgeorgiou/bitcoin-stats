import json
from coinbase.wallet.client import Client
import os
import logging

# configure the logging module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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

    account = client.get_primary_account()

    order = account.buy(
        amount="2",
        currency="USD",
    )

    logging.info(f"order details: {order['status']}")


if __name__ == "__main__":
    main()
