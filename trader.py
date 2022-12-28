from coinbase.wallet.client import Client
import os
import logging

# configure the logging module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    api_key = os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_SECRET")

    client = Client(api_key, api_secret)

    rates = client.get_exchange_rates()["rates"]
    logging.info(f"Bitcoin's price is {rates['BTC']}")

    # payment_method = client.get_payment_methods()[0]
    # logging.info(payment_method)

    # account = client.get_primary_account()
    # logging.info(account)

    # accounts = client.get_accounts()
    # print(accounts)

    # usd_account = client.get_account('881be368-8c5a-58d3-aa25-515a5763c51b')
    # print(usd_account['id'])

    primary = client.get_primary_account()
    print(primary['id'])

    order = primary.buy(
        amount="2",
        currency="USD",
    )

    print(order)

    # order = client.buy(
    #     amount="0.0001",
    #     account_id="881be368-8c5a-58d3-aa25-515a5763c51b",
    #     paymemt_method="d9627fbb-333e-583e-b2f5-efcfeeab6c95",
    #     currency="BTC",
    # )
    # logging.info(f"order is {order}")


if __name__ == "__main__":
    main()
