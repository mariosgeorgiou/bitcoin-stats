from typing import List
import yfinance as yf
import numpy as np


def get_log_returns(tickers, index, start):
    tickers.append(index)
    data = yf.download(tickers, start, threads=4)['Adj Close']
    log_returns = np.log(data/data.shift())
    return log_returns


def generate_betas(tickers: List[str], index: str, start: str):
    log_returns = get_log_returns(tickers, index, start)

    cov = log_returns.cov()
    var = log_returns[index].var()
    
    betas = cov.loc[:, index] / var

    return betas