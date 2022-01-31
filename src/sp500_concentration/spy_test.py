import sys
import json
import yfinance as yf
import pandas as pd
import requests
import matplotlib.pyplot as plt



''' Notes

    S&P 500 Hypothesis:

        The weights (aka portfolio percentages) of each stock in the S&P 500 is its
        market cap divided by the sum of the market cap of every stock in portfolio.
        https://www.investopedia.com/ask/answers/05/sp500calculation.asp

        And the portfolio is rebalanced quarterly
        https://money.stackexchange.com/questions/115679/how-often-do-the-sp-500-components-change

        This means that each time the portfolio rebalances, the stocks that increased
        in market cap will get bought up more by everyone invested in the S&P500 (which
        is most investors), thus increasing the price further, and the stocks that
        decreased in market cap will get sold more, thus decreasing the price further.
        This creates a reflexive loop that will exponentially concentrate wealth in
        various stocks in the S&P500 by taking that wealth from the other stocks in the
        S&P500.

    TO DO:

        test this theory by
            getting the quarterly list of stocks and sectors in the S&P500 and their weights over time
            see if the concentration is happening


    Sources:

        "The Standard & Poor's 500 Composite Stock Price Index is a capitalization-weighted index of 500
        stocks intended to be a representative sample of leading companies in leading industries within
        the U.S. economy."
        https://www.sec.gov/fast-answers/answersindiceshtm.html

        https://thetradable.com/stocks/apple-aapl-weight-in-sp500-has-become-the-biggest-in-40-years-with-2-trillion-market-cap-in-future

    '''

# get a list of current stock tickers in the S&P 500 and their weighting
# also do sectors
spy = yf.Ticker('SPY')
info = spy.info
# with open('spy_info.json', 'w') as f:
#     json.dump(info, f, indent=4)
sector_weights = {
    list(dct.values())[0] : list(dct.keys())[0] \
    for dct in info['sectorWeightings']}
# print('\nSector Weights:')
# for weight, ticker in sector_weights.items():
#     print(weight, '\t', ticker)

# stock_weights = {
#     dct['symbol'] : dct['holdingPercent'] \
#     for dct in info['holdings']}
# print(stock_weights)
# print(sum(stock_weights.keys()))
url = 'https://www.slickcharts.com/sp500'
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
} # HTTP Error 403 - https://stackoverflow.com/questions/43590153/http-error-403-forbidden-when-reading-html
r = requests.get(url, headers=header)
df = pd.read_html(r.text)[0]
stock_weights = {
    row['Symbol'] : row['Weight'] \
    for i, row in df.iterrows()
}
# print('\nStock Weights:')
# for ticker, weight in stock_weights.items():
#     print(ticker, '\t', weight)



# get price data of all tickers in the S&P500
start_date = '2010-01-01'
end_date   = '2021-01-01'
def get_stock_price_data(i, ticker):
    stock = yf.Ticker(ticker)
    # https://aroussi.com/post/python-yahoo-finance
    #     Ctrl + F: "history"
    print(i, '\t', ticker, '\t', start_date, end_date)
    try:
        # hist = stock.history(period="max")
        hist = stock.history(start=start_date, end=end_date)
    except:
        hist = None
    return hist
price_data = {ticker : get_stock_price_data(i, ticker) \
    for i, ticker in enumerate(stock_weights.keys())}
# for i, (ticker, price_df) in enumerate(price_data.items()):
#     print(i, ticker)
#     print(price_df)
#     input()


# sort the stocks by their weighting in the S&P500
sorted_stock_weights = sorted(list(stock_weights.items()), key=lambda x : x[1])
# print(sorted_stock_weights)
# sys.exit()

# plot the percent change in price data of these stocks over a given time period
# and use a color gradient to color code the heavier weighted stocks to be red
# and the lighter weighted stocks to be blue, and put a legend of the weighting
# at both ends of the color spectrum
for i, (ticker, weight) in enumerate(sorted_stock_weights):
    df = price_data[ticker]
    if df is None or df.empty: continue
    dates  = df.index.values.tolist()
    prices = df['Close'].tolist()
    pct_chng = (100.0 * ((df['Close'] / df['Close'].iloc[0]) - 1.0)).tolist()
    # for i in range(len(prices)):
    #     print(dates[i], prices[i], pct_chng[i])
    # input()
    print(i, '\t', ticker, '\t', weight, '\t', pct_chng[-1])
    plt.plot(dates, pct_chng)#, c=color)
plt.show()





# msft = yf.Ticker("MSFT")
# hist = msft.history(period="max")
# print(hist)
# data = yf.download("AAPL", start="2017-01-01", end="2017-04-30")
# print(data)


