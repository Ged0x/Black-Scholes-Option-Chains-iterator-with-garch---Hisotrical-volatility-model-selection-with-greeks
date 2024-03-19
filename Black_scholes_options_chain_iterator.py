import numpy as np
from scipy.stats import norm
import yfinance as yf
from volatility_Garch_demo import calculate_GARCH_volatility
from historical_volatility import calculate_historical_volatility
#from ticker import symbol
from datetime import date, datetime
import time
import matplotlib.pyplot as plt
import mplcursors

#|-----------------------------ASSUMPTIONS--------------------------------------|
#| Certain assumptions are made by the Black-Scholes model:                     |
#| The Black-Scholes model is exclusively used to price European options        |
#| and does not account for the possibility                                     |
#| of exercising U.S. options before the expiration date.                       |
#| During the option’s life, no dividends are paid.                             |
#| Markets are unpredictable (i.e., market movements cannot be predicted).      |
#| Purchasing the option has no transaction fees.                               |
#| The underlying asset’s risk-free rate and volatility are known and constant. |
#| The underlying asset’s returns are log-normally distributed.                 |
#| The option is European and can only be exercised at expiration.              |
#|------------------------------------------------------------------------------|

#prompt ticker
symbol = input("Enter Ticker : ")
asset = yf.Ticker(symbol)

#initializing variables and parameters
today_date = date.today()
risk_free = yf.Ticker('^TNX').history(period='7d')['Close'].iloc[-1]/100 #risk free bond 10 year yield
garch_volatility  = calculate_GARCH_volatility(symbol)/100 #pass the symbol and calls the volatility function from GARCH
historical_volatility = calculate_historical_volatility(symbol)/100 #pass the symbol and calls the historical volatility function



#----------------------------black-scholes-function---------------------------------------
def black_scholes(S, K, T, r, sigma, option_type = ''):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1)/(S*sigma*np.sqrt(T))
        theta = (-S*norm.pdf(d1)*sigma/ (2*np.sqrt(T))) - r*K*np.exp(-r*T) * norm.cdf(d2)
        vega = S*np.sqrt(T)*norm.pdf(d1)
        rho = K*T*np.exp(-r*T) * norm.cdf(d2)

    elif option_type == 'put':
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1)/(S*sigma*np.sqrt(T))
        theta = (-S*norm.pdf(d1)*sigma/ (2*np.sqrt(T))) - r*K*np.exp(-r*T) * norm.cdf(d2)
        vega = S*np.sqrt(T)*norm.pdf(d1)
        rho = K*T*np.exp(-r*T) * norm.cdf(d2)

    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    
    return option_price, delta, gamma, theta, vega, rho
#-----------------------------------------------------------------------------------------


expiration_dates = asset.options

print("Available expiration dates for options:")
for i, expiration_date in enumerate(expiration_dates, start=1):
    print(f"{i}. {expiration_date}")

selected_index = int(input("Select an expiration date (enter the number corresponding to the date): ")) - 1
selected_date = expiration_dates[selected_index]

options_chain = asset.option_chain(selected_date)

# Prompt the user to choose between call and put options
option_type = input("Enter 'call' or 'put' to view the corresponding options chain: ")

# Display the selected options chain based on the user's choice
if option_type.lower() == 'call' or 'CALL':
    option_data = options_chain.calls
elif option_type.lower() == 'put' or 'PUT':
    option_data = options_chain.puts
else:
    print("Invalid option type. Please enter 'call' or 'put'.")
    exit()

print("\nSelected options chain:")
print(option_data)

#color
GREEN = '\033[92m'
RESET = '\033[0m'

RED = '\033[91m'
RESET = '\033[0m'

BLUE = '\033[94m'
RESET = '\033[0m'

#time
selected_date_str = expiration_dates[selected_index]
selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
t = (selected_date - today_date).days / 365 #time left until maturity in days


#volatility model selection for sigma-----------------------------------------------------------------------
selected_volatility_model = input("Enter 'garch' or 'historical' to select the sigma for black scholes: ")
if selected_volatility_model.lower() == 'garch':
    volatility_model = garch_volatility
elif selected_volatility_model.lower() == 'historical':
    volatility_model = historical_volatility
else:
    print("Invalid option type. Please enter 'garch' or 'historical'.")
    exit()
print(f"\n----------------------------------------------------------------\033[0m")
print(f"{RED}VOLATILITY_MODEL_SELECTED{RESET} : {GREEN}{volatility_model}{RESET}")
print(f"\n----------------------------------------------------------------\033[0m")

loading_chars = "|/-\\"
for i in range(20):  # Print the loading animation 20 times
    print(f"\rLoading {loading_chars[i % len(loading_chars)]}", end='', flush=True)
    time.sleep(0.1)  # Adjust sleep duration
print("\nLoading complete.")
#-----------------------------------------------------------------------------------------------------------
#parameter check debugger
print(f"{BLUE}-----------P-A-R-A-M-E-T-E-R-S-----------{RESET}")
print("                          ")
print(f"t{BLUE} = {RESET}{t}")
print(f"sigma{BLUE} = {RESET}{volatility_model}")
print(f"r{BLUE} = {RESET}{risk_free}")
print(f"S{BLUE} = {RESET}{asset.history(period='1d').iloc[-1]['Close']}")
print("                          ")
print(f"{BLUE}-----------------------------------------{RESET}")

loading_chars = "|/-\\"
for i in range(20):  # Print the loading animation 20 times
    print(f"\rLoading {loading_chars[i % len(loading_chars)]}", end='', flush=True)
    time.sleep(0.1)  # Adjust sleep duration
print("\nLoading complete.")

# loop calculate theoretical prices using Black-Scholes model------------------------------------------------
for index, row in option_data.iterrows():

    option_price, delta, gamma, theta, vega, rho = black_scholes(asset.history(period="1d").iloc[-1]['Close'], row['strike'], selected_index + t, risk_free, volatility_model, option_type)
    print(f"\033[92mTheoretical price for {option_type} option {BLUE}{row['contractSymbol']}{RESET} {GREEN}with strike \033[35m{row['strike']}{RESET}: {option_price:.2f}\033[0m (In The Money:{RESET} {BLUE if row['inTheMoney'] else RED}{row['inTheMoney']}{RESET})")
    print(f"Delta: {delta:.2f}, Gamma: {gamma:.2f}, Theta: {theta:.2f}, Vega: {vega:.2f}, Rho: {rho:.2f}")
    print("-----------------------------------------------------------------------------------------------------------")



#----------------------------------------------GREEKS-GRAPH---------------------------------------------------------------------------------

user_input = input("Do you want to plot the Greeks? (yes/no): ").lower()

if user_input == 'yes':
    
    theoretical_prices = []
    deltas = []
    gammas = []
    thetas = []
    vegas = []
    rhos = []

    for index, row in option_data.iterrows():
        option_price, delta, gamma, theta, vega, rho = black_scholes(asset.history(period="1d").iloc[-1]['Close'], row['strike'], selected_index + t, risk_free, volatility_model, option_type)
        theoretical_prices.append(option_price)
        deltas.append(delta)
        gammas.append(gamma)
        thetas.append(theta)
        vegas.append(vega)
        rhos.append(rho)

        print(f"Plotting {option_type} option {row['contractSymbol']} with strike {row['strike']}: {option_price:.2f} (In The Money: {'Yes' if row['inTheMoney'] else 'No'})")

    # Plotting the Greeks
    strikes = option_data['strike']

    fig, axes = plt.subplots(3, 2, figsize=(12, 10))

    ax1 = axes[0, 0]
    ax1.plot(strikes, deltas, label='Delta')
    ax1.set_title('Delta vs. Strike Price')
    ax1.set_xlabel('Strike Price')
    ax1.set_ylabel('Delta Value')
    ax1.legend()
    ax1.grid(True)

    ax2 = axes[0, 1]
    ax2.plot(strikes, gammas, label='Gamma')
    ax2.set_title('Gamma vs. Strike Price')
    ax2.set_xlabel('Strike Price')
    ax2.set_ylabel('Gamma Value')
    ax2.legend()
    ax2.grid(True)

    ax3 = axes[1, 0]
    ax3.plot(strikes, thetas, label='Theta')
    ax3.set_title('Theta vs. Strike Price')
    ax3.set_xlabel('Strike Price')
    ax3.set_ylabel('Theta Value')
    ax3.legend()
    ax3.grid(True)

    ax4 = axes[1, 1]
    ax4.plot(strikes, vegas, label='Vega')
    ax4.set_title('Vega vs. Strike Price')
    ax4.set_xlabel('Strike Price')
    ax4.set_ylabel('Vega Value')
    ax4.legend()
    ax4.grid(True)

    ax5 = axes[2, 0]
    ax5.plot(strikes, rhos, label='Rho')
    ax5.set_title('Rho vs. Strike Price')
    ax5.set_xlabel('Strike Price')
    ax5.set_ylabel('Rho Value')
    ax5.legend()
    ax5.grid(True)

    plt.tight_layout()

    # Add cursor annotations
    mplcursors.cursor(hover=True)

    plt.show()
elif user_input == 'no':
    print("Exiting without plotting.")
else:
    print("Invalid input. Please enter 'yes' or 'no'.")
