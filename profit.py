import enum
import os
from typing import List
import pandas as pd
import yfinance as yf
import random
import datetime

class Asset:
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
        return Asset(self.value * other.value)


class Dollar(Asset):
    def __str__(self):
        return f"${self.value:.2f}"

class Bitcoin(Asset):
    def __str__(self):
        return f"{self.value:.2f} BTC"

class OrderType(enum.Enum):
    BUY = 'Buy'
    SELL = 'Sell'

def random_order_type() -> OrderType:

    orders = list(OrderType)

    random_order = random.choice(orders)

    return random_order

class Order:

    type: OrderType
    amount: Asset
    date: str

class BuyOrder(Order):

    def __init__(self, amount: float, date: str):
        self.type = OrderType.BUY
        self.amount = Dollar(amount)
        self.date = date


class SellOrder(Order):

    def __init__(self, amount: float, date: str):
        self.type = OrderType.SELL
        self.amount = Bitcoin(amount)
        self.date = date

def random_date() -> str:

    # define the start and end dates
    start_date = datetime.date(2015, 1, 1)
    end_date = datetime.date(2021, 12, 31)

    # calculate the number of days between the start and end dates
    num_days = (end_date - start_date).days + 1

    # generate a random number of days
    random_days = random.randint(0, num_days)

    # add the random number of days to the start date
    random_date = start_date + datetime.timedelta(days=random_days)

    # return the random date
    return random_date.strftime("%Y-%m-%d")

def random_order() -> Order:
    order_type = random_order_type()
    date = random_date()
    
    if order_type == OrderType.BUY:
        amount = random.uniform(20, 100)
        return BuyOrder(amount, date)
    else:
        amount = random.uniform(0.001, 0.1)
        return SellOrder(amount, date)

class Portfolio:

    def __init__(self, amount: float):
        self.usd = Dollar(amount)
        self.btc = Bitcoin(0.0)

    def can_buy(self, amount: Asset):
        return self.usd >= amount

    def can_sell(self, amount: Asset):
        return self.btc >= amount

def load_data():
    if os.path.exists('data.csv'):
        data = pd.read_csv('data.csv', parse_dates=True, index_col='Date')
    else:
        start_date = "2010-01-01"
        ticker = "BTC-USD"
        data = yf.download(ticker, start=start_date)
        data.to_csv('data.csv')
    return data

data = load_data()

def profit(buy_date: str, sell_date: str, fee: float = 0.006) -> float:
    buy_price = data.loc[buy_date, 'High']
    sell_price = data.loc[sell_date, 'Low']
    absolute_rate = (sell_price-buy_price)/buy_price
    real_price = absolute_rate*(1-2*fee)
    return real_price

def simulate(p: Portfolio, orders: List[Order], fee: float = 0.006) -> Portfolio:
    for order in orders:
        if type(order) == BuyOrder:
            if not p.can_buy(order.amount):
                ValueError("Not enough money to buy")
            price = data.loc[order.date, 'High']
            p.btc += order.amount * (1/price)*(1-fee) # we buy a little less
            p.usd -= order.amount
        elif type(order) == SellOrder:
            if not p.can_sell(order.amount):
                ValueError("Not enough BTC to sell")
            price = data.loc[order.date, 'Low']
            p.usd += order.amount*(1-fee)
            p.btc -= order.amount * (1/price)
    return p




def random_orders() -> List[Order]:
    orders = []
    for i in range(100):
        orders.append(random_order())

    return orders