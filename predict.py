import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools import add_constant
from sklearn.linear_model import LinearRegression, Ridge, Lasso

start_date = "2010-01-01"
ticker = "BTC-USD"


def download(start, end) -> pd.Series:
    full_data: pd.Series = yf.download(ticker, start=start, end=end)["Adj Close"]
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
    model = LinearRegression()
    model.fit(X, y)

    # predict next day's value
    features = full_data.tail(period-1)
    features = features.pivot_table(columns='Date', values='Adj Close')
    features.columns = ['Day '+str(i) for i in range(-period+1,0)]

    prediction: float = model.predict(features)[0]
    return prediction

# prediction = predict_next_day('2015-01-01','2018-01-01', 120)
# print(prediction)
