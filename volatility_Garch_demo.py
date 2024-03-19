import yfinance as yf
import pandas as pd
import numpy as np
from ticker import symbol
import arch
import math





def calculate_GARCH_volatility(symbol):
    data_volatility = yf.download(symbol, period='1y', interval='1mo')[['Open', 'Close']]
    percentage_difference = ((data_volatility['Close'] - data_volatility['Open']) / data_volatility['Open']) * 100
    model = arch.arch_model(percentage_difference)
    result = model.fit()
    conditional_volatility = result.conditional_volatility
    actual_volatility = np.sqrt(conditional_volatility)
    actual_volatility_pd = pd.DataFrame(actual_volatility)
    actual_volatility_pd = actual_volatility_pd.rename(columns={'cond_vol': 'Actual_Volatility'})
    black_scholes_volatility = actual_volatility_pd.mean() * math.sqrt(252)
    return np.float64(black_scholes_volatility)
