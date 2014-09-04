#! /usr/bin/env python

import datetime
import time
import urllib
import numpy as np
import pandas as pd
from emailing import *


def runModel(lam, alpha_d, beta_d, alpha_p, beta_p, monthly_shareprice):
    # Define monthly household income for bank; will need to periodically update this manually
    z = np.linspace(5.993,10.88,len(monthly_shareprice))
    monthly_household_income = np.exp(z)

    # Fit line to S&P500 percentage gains
    x_mo  = np.linspace(0,len(monthly_shareprice),len(monthly_shareprice))
    ps_mo = np.polyfit(x_mo,np.log(monthly_shareprice),deg=1)
    fit_line_mo = np.exp(ps_mo[0]*x_mo + ps_mo[1] + lam)
    
    bank = 0.
    shares = 0.
    for m, price in enumerate(monthly_shareprice):
        # receive your paycheck
        bank = bank + 0.1*monthly_household_income[m]

        # check how expensive/cheap the market is
        # positive if below watermark
        discount = (fit_line_mo[m]- price)/price

        # allocate how much of bank you want to invest
        if discount >= 0.0:
            purchase = (alpha_d*discount + beta_d)*bank
        else:
            purchase = (alpha_p*discount + beta_p)*bank
        if purchase > bank:
            purchase = bank
        elif purchase < 0.0:
            purchase = 0.0

        # buy shares
        shares = shares + purchase/price
        bank   = bank - purchase

        # accrue interest in bank
        bank   = bank + (0.01/12.)*bank

    final_price  = list(monthly_shareprice)[-1]
    fraction     = purchase/(0.1*monthly_household_income[m])
    
    return discount,fraction



while True:
    d = datetime.date.today()
    yr_num   = d.year
    mon_num  = d.month
    day_num  = d.day
    day_name = d.weekday()
    if day_num < 32:
        # Fetch current price data from Yahoo Finance
        url = 'http://real-chart.finance.yahoo.com/table.csv?s=%%5EGSPC&d=%d&e=%d&f=%d&g=d&a=0&b=3&c=1950&ignore=.csv' % (mon_num,day_num,yr_num)
        urllib.urlretrieve(url,'sp500_history.csv')

        # Open stock price data
        data = pd.read_csv('sp500_history.csv')

        monthly_shareprice = np.array(data['Close'])[0::30]
        monthly_shareprice = monthly_shareprice[::-1] # time=0 => oldest
        
        
        # CURRENT MODEL
        lam     = 1.86335669e-01
        alpha_d = 1.20807310e+01
        beta_d  = -3.47832606e-01
        alpha_p = 2.10488221e-04
        beta_p  = -2.27735354e-04

        # RUN MODEL
        discount,fraction_to_buy = runModel(lam,alpha_d,beta_d,alpha_p,beta_p,monthly_shareprice)

        if discount >= 0.0:
            market_condition = 'cheap'
            discount_or_premium = 'discount'
        else:
            market_condition = 'expensive'
            discount_or_premium = 'premium'

        fraction_to_hold = 1.0 - fraction_to_buy

        if fraction_to_buy < 0:
            fraction_to_buy = 0.0
        if fraction_to_hold < 0:
            fraction_to_hold = 0.0
        if fraction_to_hold > 1.0:
            fraction_to_hold = 1.0

        msg = 'Today is %d-%d-%d and the S&P last closed at %d. Market is currently %s with %s %d%%. Buy %d%% stocks and keep %d%% cash.' % (mon_num,day_num,yr_num,monthly_shareprice[-1],market_condition, discount_or_premium, np.abs(100.*discount), 100.*fraction_to_buy, 100.*fraction_to_hold)
        emailMe(msg)
        time.sleep(24*60*60) # Go to sleep after sending message

    time.sleep(24*60*60) # Sleep for a day before checking again

