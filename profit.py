from copy import copy
import enum
import os
from typing import List
import pandas as pd
import yfinance as yf
import random
from datetime import datetime, timedelta, date
import dateutil.rrule as rrule
from predict import predict_next_day, load_or_download, get_price
import time


def show_loading_bar(
    iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="")
    # Print New Line on Complete
    if iteration == total:
        print()


class Asset:

    value: float

    def __init__(self, value: float):
        self.value = value

    def __add__(self, other):
        return Asset(self.value + other.value)

    def __sub__(self, other):
        return Asset(self.value - other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __mul__(self, other):
        return Asset(self.value * other)


class Dollar(Asset):
    def __str__(self):
        return f"${self.value:.2f}"


class Bitcoin(Asset):
    def __str__(self):
        return f"{self.value:.2f}BTC"


class OrderType(enum.Enum):
    BUY = "Buy"
    SELL = "Sell"


def random_order_type() -> OrderType:

    orders = list(OrderType)

    random_order = random.choice(orders)

    return random_order


class Order:

    type: OrderType
    amount: Dollar | Bitcoin
    date: str

    def __str__(self) -> str:
        return str(self.type.value) + " " + str(self.amount) + " " + str(self.date)


class BuyOrder(Order):
    def __init__(self, amount: Dollar, date: str):
        self.type = OrderType.BUY
        self.amount = amount
        self.date = date


class SellOrder(Order):
    def __init__(self, amount: Bitcoin, date: str):
        self.type = OrderType.SELL
        self.amount = amount
        self.date = date


def random_date() -> str:

    # define the start and end dates
    start_date = date(2015, 1, 1)
    end_date = date(2021, 12, 31)

    # calculate the number of days between the start and end dates
    num_days = (end_date - start_date).days + 1

    # generate a random number of days
    random_days = random.randint(0, num_days)

    # add the random number of days to the start date
    random_date = start_date + timedelta(days=random_days)

    # return the random date
    return random_date.strftime("%Y-%m-%d")


def random_order() -> Order:
    order_type = random_order_type()
    date = random_date()

    if order_type == OrderType.BUY:
        amount = random.uniform(20, 100)  # random amount of USD
        return BuyOrder(Dollar(amount), date)
    else:
        amount = random.uniform(0.001, 0.1)  # random amount of BTC
        return SellOrder(Bitcoin(amount), date)


def random_orders() -> List[Order]:
    orders = []
    for i in range(10):
        orders.append(random_order())

    return orders


class Portfolio:
    def __init__(self, dollars: Dollar, bitcoins: Bitcoin):
        self.usd = dollars
        self.btc = bitcoins

    def can_buy(self, amount: Dollar):
        return self.usd >= amount

    def can_sell(self, amount: Bitcoin):
        return self.btc >= amount

    def __str__(self) -> str:
        return "USD:" + str(self.usd.value) + " BTC:" + str(self.btc.value)


def load_data():
    if os.path.exists("data.csv"):
        data = pd.read_csv("data.csv", parse_dates=True, index_col="Date")
    else:
        start_date = "2010-01-01"
        ticker = "BTC-USD"
        data = yf.download(ticker, start=start_date)
        data.to_csv("data.csv")
    return data


def single_order_profit(
    data: pd.DataFrame, buy_date: str, sell_date: str, fee: float = 0.006
) -> float:
    buy_price: float = data.loc[buy_date, "High"]
    sell_price: float = data.loc[sell_date, "Low"]
    absolute_rate: float = (sell_price - buy_price) / buy_price
    real_price = absolute_rate * (1 - 2 * fee)
    return real_price


def simulate(
    data: pd.DataFrame,
    p: Portfolio,
    orders: List[BuyOrder | SellOrder],
    fee: float = 0.006,
) -> Portfolio:
    p = copy(p)
    for order in orders:
        print(p)
        amount = order.amount.value
        if type(order.amount) == Dollar:
            if not p.can_buy(order.amount):
                print(
                    "Not enough USD to buy order amount! Buying with max USD available"
                )
                amount = p.usd.value
            price = data.loc[order.date, "High"]
            p.btc += Bitcoin(amount * (1 / price) * (1 - fee))  # we buy a little less
            p.usd -= Dollar(amount)
        elif type(order.amount) == Bitcoin:
            if not p.can_sell(order.amount):
                print("Not enough BTC to sell order amount! Selling max BTC available")
                amount = p.btc.value
            price = data.loc[order.date, "Low"]
            p.usd += Dollar(amount * price * (1 - fee))
            p.btc -= Bitcoin(amount)
    return p


def create_order(start: str, today: str, fee: float = 0.00):
    todays_price = get_price(today)
    tomorrow = get_next_date(today, 1)
    tomorrows_price = get_price(tomorrow)
    tomorrows_prediction = float(predict_next_day(start, today, 120))
    print(today, "price", todays_price)
    print(tomorrow, "price", tomorrows_price)
    print(tomorrow, "prediction", tomorrows_prediction)
    if todays_price + 400 < tomorrows_prediction:
        amount = tomorrows_prediction - todays_price
        return BuyOrder(Dollar(amount), today)
    elif todays_price > tomorrows_prediction + 400:
        amount = 1 / (todays_price - tomorrows_prediction)
        return SellOrder(Bitcoin(amount), today)


def get_next_date(date_string: str, time_inteval: int) -> str:
    date: datetime = datetime.strptime(date_string, "%Y-%m-%d")
    next_date = date + timedelta(days=time_inteval)
    return next_date.strftime("%Y-%m-%d")


def create_daily_orders(start: str, end: str, number_of_orders: int) -> List[Order]:
    orders: List[Order] = []
    last_order_date = end
    first_order_date = get_next_date(end, -number_of_orders)
    order_dates = pd.date_range(first_order_date, last_order_date)

    i = 0
    l = len(order_dates)
    show_loading_bar(i, l, prefix="Progress:", suffix="Complete", length=50)

    for order_date in order_dates:

        i += 1
        show_loading_bar(i, l, prefix="Progress:", suffix="Complete", length=50)

        order = create_order(start, order_date.strftime("%Y-%m-%d"))
        if order is not None:
            orders.append(order)
    last_order = SellOrder(Bitcoin(1), last_order_date)
    orders.append(last_order)
    return orders


def main():
    initial_portfolio = Portfolio(Dollar(10000.0), Bitcoin(0.0))
    print(initial_portfolio)
    orders = create_daily_orders("2015-01-01", "2021-05-30", 5)
    # for order in orders:
    #     print(order)
    data = load_data()
    final_portfolio = simulate(data, initial_portfolio, orders)
    print(final_portfolio)


if __name__ == "__main__":
    main()
