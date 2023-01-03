import yfinance as yf
import os
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from datetime import datetime

ticker = "BTC-USD"


def download(start, end) -> pd.Series:
    full_data = pd.DataFrame(yf.download(ticker, start=start)["Adj Close"]).loc[:end]
    full_data.to_csv("full_data.csv")
    return full_data


def load_or_download(start, end) -> pd.Series:
    if os.path.exists("full_data.csv"):
        full_data: pd.Series = pd.read_csv("full_data.csv", parse_dates=True, index_col="Date")
        if start in full_data.index and end in full_data.index:
            return full_data.loc[start:end]
        else:
            return download(start, end)
    else:
        return download(start, end)

def get_price(date: str) -> float:
    return float(load_or_download(date, date).loc[date])

def predict_next_day(start_date: str, end_date: str, period: int) -> float:
    full_data = load_or_download(start_date, end_date)

    # compute all rolling windows of size=period
    rolling_windows = full_data.rolling(period, min_periods=period)
    windows = pd.concat([rolling_windows.apply(lambda x: x[i]) for i in range(period)], axis=1).dropna()
    columns = ['Day '+str(i) for i in range(-period+1,1)]
    windows.columns = columns
    target_column = 'Day 0'
    X = windows.drop(target_column, axis=1)
    y = windows[target_column]

    # train model
    model = Ridge(alpha=0.0001)
    model.fit(X, y)

    # predict next day's value
    features = full_data.tail(period-1)
    features1 = features.pivot_table(columns='Date', values='Adj Close')
    features1.columns = ['Day '+str(i) for i in range(-period+1,0)]

    prediction: float = model.predict(features1)[0]
    return prediction

# prediction = predict_next_day('2015-01-01',datetime.today().strftime("%Y-%m-%d"), 120)
# print(prediction)
