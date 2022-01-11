import sys
import json
import yfinance as yf

# pip install yfinance --upgrade --no-cache-dir
# https://aroussi.com/post/python-yahoo-finance


msft = yf.Ticker("MSFT")
# hist = msft.history(period="max")
# print(hist)

# data = yf.download("AAPL", start="2017-01-01", end="2017-04-30")
# print(data)

# get stock info
with open('test.txt', 'w') as f:
    json.dump(msft.info, f, indent=4)

'''
# get historical market data
hist = msft.history(period="max")

# show actions (dividends, splits)
msft.actions

# show dividends
msft.dividends

# show splits
msft.splits

# show financials
msft.financials
msft.quarterly_financials

# show major holders
msft.major_holders

# show institutional holders
msft.institutional_holders

# show balance sheet
msft.balance_sheet
msft.quarterly_balance_sheet

# show cashflow
msft.cashflow
msft.quarterly_cashflow

# show earnings
msft.earnings
msft.quarterly_earnings

# show sustainability
msft.sustainability

# show analysts recommendations
msft.recommendations

# show next event (earnings, etc)
msft.calendar

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
msft.isin

# show options expirations
msft.options

# show news
msft.news

# get option chain for specific expiration
opt = msft.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts

'''


