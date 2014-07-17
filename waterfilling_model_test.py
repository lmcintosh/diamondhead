#! /usr/bin/env python

import datetime
import time
import urllib
import numpy as np
import pandas as pd
from emailing import *


while True:
    d = datetime.date.today()
    yr_num   = d.year
    mon_num  = d.month
    day_num  = d.day
    day_name = d.weekday()
    if day_num < 30 and day_name >= 0:
        # Fetch current price data from Yahoo Finance
        url = 'http://real-chart.finance.yahoo.com/table.csv?s=%%5EGSPC&d=%d&e=%d&f=%d&g=d&a=0&b=3&c=1950&ignore=.csv' % (mon_num,day_num,yr_num)
        urllib.urlretrieve(url,'sp500_history.csv')

        # Open stock price data
        data = pd.read_csv('sp500_history.csv')

        monthly_shareprice = data['Close'][0::30]
        monthly_shareprice = monthly_shareprice[::-1] # time=0 => oldest
        
        
        # CURRENT MODEL
        lam = -0.0039371799019069665
        alpha_d = 1.6387065003802097
        alpha_p = 0.00012930819425967602
        beta_d  = 0.26391542623164571
        beta_p  = -4.866531100483897e-05

        # Fit line that gives the average return
        x_mo  = np.linspace(0,len(monthly_shareprice),len(monthly_shareprice))
        ps_mo = np.polyfit(x_mo,np.log(monthly_shareprice),deg=1)
        fit_line_mo = np.exp(ps_mo[0]*x_mo + ps_mo[1] + lam)

        # Compute current market conditions
        price    = list(monthly_shareprice)[-1]
        discount = (fit_line_mo[-1] - price)/price

        if discount >= 0.0:
            fraction_to_buy = (alpha_d*discount + beta_d)
            market_condition = 'cheap'
	    discount_or_premium = 'discount'
        else:
            fraction_to_buy = (alpha_p*discount + beta_p)
            market_condition = 'expensive'
	    discount_or_premium = 'premium'

        fraction_to_hold = 1.0 - fraction_to_buy

        if fraction_to_buy < 0:
            fraction_to_buy = 0.0
        if fraction_to_hold < 0:
            fraction_to_hold = 0.0
	if fraction_to_hold > 1.0:
	    fraction_to_hold = 1.0

        msg = 'Today is %d-%d-%d and the S&P last closed at %d. Market is currently %s with %s %d%%. Buy %d%% stocks and keep %d%% cash.' % (mon_num,day_num,yr_num,price,market_condition, discount_or_premium, np.abs(100.*discount), 100.*fraction_to_buy, 100.*fraction_to_hold)
        emailMe(msg)

	time.sleep(24*60*60) # Go to sleep after sending the message

    time.sleep(24*60*60) # Sleep for a day before checking again


