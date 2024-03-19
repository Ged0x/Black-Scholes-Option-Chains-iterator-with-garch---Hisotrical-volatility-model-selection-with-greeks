import yfinance as yf
import numpy as np
import pandas as pd


trading_days_daily = 252
trading_days_monthly = 12

def calculate_historical_volatility(symbol):
    trading_days_monthly = 12
    annual_volatility_data = yf.download(symbol, period = '1y', interval = '1mo')[['Open', 'Close']]
    percentage_returns_daily = (annual_volatility_data['Close'] - annual_volatility_data['Open'])/ (annual_volatility_data['Open']) * 100
    annual_volatility_calculated = percentage_returns_daily.std()
    annualized_volatility = annual_volatility_calculated*np.sqrt(trading_days_monthly)
    return annualized_volatility
