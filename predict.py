import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools import add_constant

start_date = "2010-01-01"
ticker = "BTC-USD"


if os.path.exists('full_data.csv'):
    full_data = pd.read_csv('full_data.csv', parse_dates=True, index_col='Date')
else:
    full_data = yf.download(ticker, start=start_date)["Adj Close"]
    full_data.to_csv('full_data.csv')


full_data['Time'] = np.arange(len(full_data.index))
full_data.plot(x='Time', y='Adj Close', kind='scatter')
plt.show()

log_data = np.log(full_data)
log_data['Time'] = np.arange(len(log_data.index))

X = log_data.loc[:, 'Time']
# X = add_constant(X)
y = log_data.loc[:, 'Adj Close']

sns.regplot(data=log_data, x='Time', y='Adj Close', ci=99.9999, scatter_kws={'s':1})

plt.show()

# model = sm.OLS(y, X)

# results = model.fit()

# print(results.params)

