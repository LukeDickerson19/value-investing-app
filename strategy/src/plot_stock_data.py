


import argparse
import re
import os
import json
import sys
import pathlib
from datetime import datetime, date, timedelta
parser = argparse.ArgumentParser(
    description='\n'.join([
    	'This script plots the price and fundamental metrics of a specified stock.',
    	'Stocks are specified with their ticker symbol or their CIK number.',
        '    Example:',
        '        python plot_stock.py -x AAPL',
        '        python plot_stock.py -c 320193']),
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose logging')
parser.add_argument('-t', '--test',    action='store_true', default=False, help='use data from data/test_data intead of data/real_data')
parser.add_argument('-x', '--ticker',  action='store',      default='',    help='ticker symbol, example: \"-x AAPL\"')
parser.add_argument('-c', '--cik',     action='store',      default='',    help='CIK,           example: \"-c 320193\"')
args = parser.parse_args()

import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 56)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_colwidth', 20)
pd.set_option('display.width', 100000)
import matplotlib as mpl
import matplotlib.pyplot as plt
import yfinance as yf

# import common utils
REPO_PATH           = str(pathlib.Path(__file__).resolve().parent.parent.parent)
STRATEGY_PATH       = str(pathlib.Path(__file__).resolve().parent)
DATA_SOURCE_PATH    = os.path.join(REPO_PATH, 'database', 'sec', 'financial_statements_data_sets')
# UTILS_REPO_PATH     = os.path.join(str(pathlib.Path(REPO_PATH).resolve().parent.parent.parent),
#                       'tech', 'software', 'projects', 'python-common-utils')
# LOG_UTIL_PATH       = os.path.join(UTILS_REPO_PATH, 'utils', 'logging', 'src')
LOG_UTIL_PATH       = os.path.join(REPO_PATH, 'common_utils')
# print('REPO_PATH       ', REPO_PATH)
# print('STRATEGY_PATH   ', STRATEGY_PATH)
# print('DATA_SOURCE_PATH', DATA_SOURCE_PATH)
# print('UTILS_REPO_PATH ', UTILS_REPO_PATH)
# print('LOG_UTIL_PATH   ', LOG_UTIL_PATH)
# sys.exit()
sys.path.append(LOG_UTIL_PATH); import logging_utils


# local file and directory paths
LOG_FILENAME           = 'log.txt' # 'log_%s' % datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.txt")
LOG_FILEPATH           = os.path.join(
    STRATEGY_PATH.replace('/src', ''), 'logs',
    ('test_log' if args.test else 'real_log'),
    LOG_FILENAME)
log = logging_utils.Log(LOG_FILEPATH)
STRATEGY_CONFIG_PATH   = os.path.join(STRATEGY_PATH, 'strategy_config.json')
with open(STRATEGY_CONFIG_PATH, 'r') as f:
    strategy_config = json.load(f)
DATA_PATH              = \
    os.path.join(DATA_SOURCE_PATH, 'data', 'test_data') if args.test else \
    os.path.join(DATA_SOURCE_PATH, 'data', 'real_data')
DATA_WAREHOUSE_PATH    = os.path.join(DATA_PATH, 'warehouse')
DATA_STOCKS_PATH       = os.path.join(DATA_WAREHOUSE_PATH, 'stocks')

QUERY_YAHOO_FINANCE = True

SIC_CODES_FILEPATH     = os.path.join(DATA_WAREHOUSE_PATH, 'sic_codes.csv')
COUNTRY_CODES_FILEPATH = os.path.join(DATA_WAREHOUSE_PATH, 'state_and_country_codes.csv')
TICKER_CODES_FILEPATH  = os.path.join(DATA_WAREHOUSE_PATH, 'ticker_cik_mapping.csv')
METADATA_FILEPATH      = os.path.join(DATA_WAREHOUSE_PATH, 'metadata.json')
# print('LOG_FILEPATH          ', LOG_FILEPATH)
# print('DATA_PATH             ', DATA_PATH)
# print('DATA_WAREHOUSE_PATH   ', DATA_WAREHOUSE_PATH)
# print('DATA_STOCKS_PATH      ', DATA_STOCKS_PATH)
# print('SIC_CODES_FILEPATH    ', SIC_CODES_FILEPATH)
# print('COUNTRY_CODES_FILEPATH', COUNTRY_CODES_FILEPATH)
# print('TICKER_CODES_FILEPATH ', TICKER_CODES_FILEPATH)
# print('METADATA_FILEPATH     ', METADATA_FILEPATH)
# sys.exit()



# get ticker and CIK of stock
def get_ticker_mapping_from_sec(
    download=False,
    verbose=False):

    if verbose:
        print('getting ticker mapping from %s' % \
            ('SEC' if download else 'local database'))

    # get tickers from local csv file
    if not download:
        try:
            df = pd.read_csv(TICKER_CODES_FILEPATH, index_col=0, dtype=str)
        except:
            df = pd.DataFrame()
        repo_filepath = TICKER_CODES_FILEPATH[TICKER_CODES_FILEPATH.index('value-investing-app'):]
        if df.shape[0] > 0:
            if verbose:
                print('    found ticker mapping locally at:')
                print('        ', repo_filepath)
            return df
        else:
            if verbose:
                print('    failed to find ticker mapping locally at:')
                print('        ', repo_filepath)
    else:
        if verbose:
            print('    URL: %s' % TICKER_URL)
        response = requests.get(TICKER_URL, headers={'User-Agent' : USER_AGENT})
        data = json.loads(response.text)
        df = pd.DataFrame(data['data'], columns=data['fields'], dtype=str)
        df.to_csv(TICKER_CODES_FILEPATH)
    if verbose:
        print('done, parsed %d tickers' % df.shape[0])
    return df
ticker_df = get_ticker_mapping_from_sec()
if args.ticker == '' and args.cik == '':
    print('\nmust enter ticker symbol or CIK number')
    print('    example ticker argument: \"-x AAPL\"')
    print('    example CIK argument:    \"-c 320193\"')
    print()
    sys.exit()
elif args.ticker != '':
    ticker = args.ticker
    if ticker not in ticker_df['ticker'].tolist():
        print('\nticker not found: %s\n' % ticker)
        sys.exit()
    possible_ciks = ticker_df[ticker_df['ticker'] == ticker]['cik'].tolist()
    if possible_ciks != []:
        cik = possible_ciks[0]
    else:
        print('\nno CIK found for ticker: %s' % ticker)
        print()
        sys.exit()
elif args.cik != '':
    cik = args.cik
    if cik not in ticker_df['cik'].tolist():
        print('\nCIK not found: %s\n' % cik)
        sys.exit()
    possible_tickers = ticker_df[ticker_df['cik'] == cik]['ticker'].tolist()
    if possible_tickers != []:
        ticker = possible_tickers[0]
    else:
        print('\nno ticker found for CIK: %s\n' % args.cik)
        sys.exit()
print('\nticker: %s' % ticker)
print('CIK:    %s\n' % cik)

# get data for stock
def get_qtr_str(df):
    return df[['year','quarter']].apply(
        lambda x : '{}q{}'.format(x[0],x[1]), axis=1)
def get_datetime_str(d):
    # remove zero padding of day of month
    day = int(datetime.strftime(d, '%d'))
    d_str = '%s %d %s' % (
        datetime.strftime(d, '%a %b'),
        day,
        datetime.strftime(d, '%Y'))
    return d_str
def get_dividend_yield(
    df,
    current_price,
    current_date):

    current_date_minus_one_year = '%s%s' % (
        int(current_date[:4]) - 1,
        current_date[4:])
    # print(current_date_minus_one_year)
    # print(current_date)
    # print(df)
    df = df[df['Date'].between(
        current_date_minus_one_year, current_date)]
    # print(df)
    # print(current_price)
    dividends_of_past_year = df['Dividends'].sum()
    # print(dividends_of_past_year)
    dividend_yield = dividends_of_past_year / current_price
    # print(dividend_yield)
    return dividend_yield
cik_path = os.path.join(DATA_STOCKS_PATH, cik)
if not os.path.exists(cik_path):
    print('no data owned for this stock\n')
    sys.exit()
with open(os.path.join(cik_path, 'info.json')) as f:
    info = json.load(f)
daily_price_history        = pd.read_csv(os.path.join(cik_path, 'daily_price_data.csv'))
dividend_per_share_history = pd.read_csv(os.path.join(cik_path, 'dividend_per_share_history.csv'))
stock_split_history        = pd.read_csv(os.path.join(cik_path, 'stock_split_history.csv'))
fundamental_history        = pd.read_csv(os.path.join(cik_path, 'fundamentals.csv'))
fundamental_history['qtr_str'] = get_qtr_str(fundamental_history)
fundamental_history['book_value'] = fundamental_history['total_assets'] - fundamental_history['total_liabilities']
if QUERY_YAHOO_FINANCE:
    try:
        yf_company = yf.Ticker(ticker)
        try:
            yf_info = yf_company.info
        except:
            print('\nfailed to query yahoo finance for yf_info\n')
            sys.exit()
    except:
        print('\nfailed to query yahoo finance for yf_company\n')
        sys.exit()
    # print(json.dumps(yf_info, indent=4))
    ex_date = 'None' if yf_info['exDividendDate'] in [None] else \
        get_datetime_str(datetime.fromtimestamp(yf_info['exDividendDate']))
    dividend_yield = 'None' if yf_info['dividendYield'] in [None, 0] else \
        ('%.2f %%' % (100 * yf_info['dividendYield']))
    country = yf_info['country']
else:
    ex_date = info['ex_dividend_date']
    current_price = daily_price_history['Close'].iloc[-1]
    current_date = daily_price_history['Date'].iloc[-1]
    dividend_yield = get_dividend_yield(
        dividend_per_share_history, current_price, current_date)
    dividend_yield = ('%.2f %%' % (100 * dividend_yield)) if dividend_yield != 0.0 else 'None'
    country = info['country']

# plot data for stock
def plot_stock_data():
    fig, ax = plt.subplots(2, 2)
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    window_title = '%s (CIK=%s)' % (ticker, cik)
    mng.set_window_title(window_title)
    write_basic_info()
    plot_price_and_dividends(ax[0][1])
    plot_shares_outstanding(ax[1][1])
    plot_book_value_and_net_income(ax[0][0])
    plot_total_assets_and_total_liabilities(ax[1][0])
    # plt.tight_layout()
    plt.subplots_adjust(
        left=0.05,
        bottom=0.13,
        right=0.93,
        top=0.70,
        wspace=0.2,
        hspace=0.3)
    plt.show()
def write_basic_info():
    x0, y0 = 0, 0.62
    title = ticker
    plt.gcf().text(x0+0.06, y0+0.33, title, fontsize=17)
    text1 = '\n'.join([
        'Dividend Yield:',
        'Ex-Date:',
        'Sector:',
        'Industry:',
        'Country:',
        'SEC CIK ID:'
    ])
    text2 = '\n'.join([
        str(dividend_yield),
        str(ex_date),
        info['industry_classification']['gics']['sector'],
        info['industry_classification']['gics']['industry'],
        country,
        info['cik']
    ])
    plt.gcf().text(x0+0.06, y0+0.15, text1, fontsize=11)
    plt.gcf().text(x0+0.16, y0+0.15, text2, fontsize=11)

    url = info['website']
    description_max_characters = 300
    description = info['description']
    if len(description) > description_max_characters:
        description = description[:description_max_characters] + '...'
    else:
        description = description + ' '*(description_max_characters - len(description))
    text3 = '\n'.join([
        'Company Name:',
        'Website:',
        'Description:'
    ])
    text4 = '\n'.join([
        info['name'],
        url,
        description,
    ])
    plt.gcf().text(x0+0.33, y0+0.235, text3, fontsize=11, wrap=True)#url, url=url)#, bbox = dict(color='w', alpha=0.01, url=url))
    plt.gcf().text(x0+0.43, y0+0.155, text4, fontsize=11, wrap=True)#url, url=url)#, bbox = dict(color='w', alpha=0.01, url=url))
    # text = plt.annotate(
    #     'Link', xy=(15, 15), xytext=(15, 15),
    #     url='http://matplotlib.org')
    #     # bbox=dict(color='w', alpha=1e-6, url='http://matplotlib.org'))
def plot_price_and_dividends(ax1):
    ax1.set_title('Price & Dividends')
    clipped_price_data = get_clipped_data(daily_price_history, 'week')#, verbose=True)
    clipped_dividend_data = get_clipped_data(dividend_per_share_history, 'day')#, verbose=True)
    ax2 = ax1.twinx()
    ax1.plot(
        clipped_price_data['Date'],
        clipped_price_data['Close'],
        color='black')
    ax2.bar(
        clipped_dividend_data['Date'],
        clipped_dividend_data['Dividends'],
        width=20.0,
        color='blue')
    ax1.set_zorder(1)
    ax1.set_frame_on(False)
    ax1.set_ylabel('Price')
    ax2.set_ylabel('Dividend per Share')
    ax1.set_xticks([])

    # TO DO: fix this, uncomment to see how its broken
    # # format labels appear when hoving over a point
    # # source: https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib
    # def format_coord(x, y):
    #     # return '%s %s' % (x, y)

    #     start_date = daily_price_history['Date'].iloc[0]
    #     end_date = daily_price_history['Date'].iloc[-1]

    #     d1 = datetime.strptime(start_date, "%Y-%m-%d")
    #     d2 = datetime.strptime(end_date,   "%Y-%m-%d")

    #     # difference between dates in timedelta
    #     delta = d2 - d1
    #     print(f'Difference is {delta.days} days')

    #     n = clipped_price_data.shape[0]
    #     print(0, int(x), int(x)-n, n)
    #     # return ''
    #     if 0 <= int(x)-n <= n:
    #         date = clipped_price_data['Date'].iloc[int(x)-n]
    #         price = float(clipped_price_data['Close'].iloc[int(x)-n])
    #         dividend = ''#float(clipped_dividend_data['Dividends'].iloc[int(x)-n])
    #         return 'date:%s\tprice:%s\tdividend:%s' % (date, price, dividend)
    #     else:
    #         print('bye')
    #         return ''
    # ax1.format_coord = format_coord
def plot_shares_outstanding(ax):
    ax.set_title('Shares Outstanding')
    ax.bar(
        fundamental_history['qtr_str'],
        fundamental_history['shares_outstanding'],
        bottom=0,
        label='shares outstanding',
        color='lightgrey')
    for i, row in stock_split_history.iterrows():
        qtr_str = get_qtr_str_from_date(row['Date'])
        color = 'red'
        if qtr_str in fundamental_history['qtr_str'].tolist():
            ax.plot([qtr_str, qtr_str], ax.get_ylim(), color=color)
            if row['Stock Splits'] > 1.0:
                split_str = '%d:1 Split' % int(row['Stock Splits'])
            else:
                split_str = '1:%d Split' % int(1/row['Stock Splits'])
            ax.annotate(
                split_str,
                (qtr_str, int(ax.get_ylim()[1] / 2)),
                ha='right',
                rotation=90,
                color=color)
    # quarter_labels = fundamental_history['qtr_str'].apply(lambda s : s[4:]).tolist()
    # year_labels    = fundamental_history['qtr_str'].apply(lambda s : s[:4]).tolist()
    # print(quarter_labels)
    # ax.set_xticklabels(quarter_labels, minor=False)
    plt.setp(ax.get_xticklabels(), rotation=90)
    ax.set_xlabel('Quarter')
    # ax.set_xticklabels(year_labels,    minor=True)
    ax.set_ylabel('Num. of Shares')
    ax.tick_params(axis='x', which='major', labelsize=6)
    # ax.legend(loc='upper left')

    # format labels appear when hoving over a point
    # source: https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib
    def format_coord(x, y):
        if 0 <= int(x) < fundamental_history.shape[0]:
            quarter = fundamental_history['qtr_str'].iloc[int(x)]
            shares_outstanding = int(fundamental_history['shares_outstanding'].iloc[int(x)])
            total_liabilities = int(fundamental_history['total_liabilities'].iloc[int(x)])
            return 'quarter:%s\tshares_outstanding:%s\t' % (quarter, shares_outstanding)
        else:
            return ''
    ax.format_coord = format_coord
def plot_book_value_and_net_income(ax):
    ax.set_title('Book Value & Net Income')
    ax.bar(
        fundamental_history['qtr_str'],
        fundamental_history['net_income'],
        bottom=fundamental_history['book_value'],
        label='net income',
        color=(fundamental_history['net_income']>0).map({True: 'limegreen', False: 'red'}),
        zorder=2.0)
    ax.bar(
        fundamental_history['qtr_str'],
        fundamental_history['book_value'],
        bottom=0,
        label='book value',
        color='lightgrey',
        zorder=1.0)
    # plt.setp(ax.get_xticklabels(), rotation=90)
    ax.set_xticklabels([])
    ax.set_ylabel('USD Value')
    ax.legend(loc='upper left')

    # format labels appear when hoving over a point
    # source: https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib
    def format_coord(x, y):
        if 0 <= int(x) < fundamental_history.shape[0]:
            quarter = fundamental_history['qtr_str'].iloc[int(x)]
            net_income = int(fundamental_history['net_income'].iloc[int(x)])
            book_value = int(fundamental_history['book_value'].iloc[int(x)])
            return 'quarter:%s\tbook value:%s\tnet income%s\t' % (quarter, book_value, net_income)
        else:
            return ''
    ax.format_coord = format_coord
def plot_total_assets_and_total_liabilities(ax):
    ax.set_title('Total Assets & Total Total Liabilities')
    ax.bar(
        fundamental_history['qtr_str'],
        fundamental_history['total_assets'],
        label='total assets',
        color='limegreen')
    ax.bar(
        fundamental_history['qtr_str'],
        -fundamental_history['total_liabilities'],
        label='total liabilities',
        color='red')
    plt.setp(ax.get_xticklabels(), rotation=90)
    ax.set_ylabel('USD Value')
    ax.set_xlabel('Quarter')
    ax.legend(loc='upper left')
    ax.tick_params(axis='x', which='major', labelsize=6)

    # format labels appear when hoving over a point
    # source: https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib
    def format_coord(x, y):
        if 0 <= int(x) < fundamental_history.shape[0]:
            quarter = fundamental_history['qtr_str'].iloc[int(x)]
            total_assets = int(fundamental_history['total_assets'].iloc[int(x)])
            total_liabilities = int(fundamental_history['total_liabilities'].iloc[int(x)])
            return 'quarter:%s\ttotal_assets:%s\ttotal_liabilities%s\t' % (quarter, total_assets, total_liabilities)
        else:
            return ''
    ax.format_coord = format_coord
def get_qtr_str_from_date(date_str):
    y, m, d = tuple(date_str.split('-'))
    q = str((int(m)-1)//3 + 1)
    qtr_str = y+'q'+q
    return qtr_str
def get_clipped_data(df, interval, verbose=False):
    start_quarter, end_quarter = \
        fundamental_history.iloc[0], \
        fundamental_history.iloc[-1]
    start_date, end_date = \
        get_qtr_start_date(start_quarter['year'], start_quarter['quarter']), \
        get_qtr_end_date(end_quarter['year'], end_quarter['quarter'])
    df = df.copy()
    if not df.empty:
        df = df[df['Date'] >= start_date]
        df = df[df['Date'] <= end_date]
        df = get_data_on_interval(df, interval)
    df.reset_index(inplace=True, drop=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    if verbose:
        print(df)
    return df
def get_data_on_interval(
    df,
    interval):

    most_recent_date_str = df['Date'].iloc[-1]
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    if interval == 'day':
        pass
    elif interval == 'week':
        df['datetime'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        df['weekday'] = df['datetime'].dt.weekday
        df = df[df['weekday'] == most_recent_date.weekday()].copy()
        df.drop(columns=['datetime', 'weekday'], inplace=True)
    elif interval == 'month':
        df = closest_month_day(df, most_recent_date)
    elif interval == 'quarter':
        df = closest_quarter_day(df, most_recent_date)
    elif interval == 'year':
        df = closest_year_day(df, most_recent_date)
    return df
def closest_month_day(df, most_recent_date):
    # this function will get a value for each month in the data thats closest to the current day of the month of today
    # this is required because the data is often not on daily intervals (ex: price data is only on workdays)
    df2 = pd.DataFrame(columns=df.columns)
    years = list(set(map(lambda d : d[:4], df['Date'].tolist())))
    years.sort()
    def get_current_day(y, m, most_recent_date):
        d = most_recent_date.day
        m = int(m)
        y = int(y)
        days_in_months = {
            1  : 31,
            2  : 28,
            3  : 31,
            4  : 30,
            5  : 31,
            6  : 30,
            7  : 31,
            8  : 31,
            9  : 30,
            10 : 31,
            11 : 30,
            12 : 31
        }
        if d > days_in_months[m]:
            d = days_in_months[m]
        return datetime(y, m, d)
    for y in years:
        df_of_y = df[df['Date'].str[:4] == y]
        months = list(set(map(lambda d : d[5:7], df_of_y['Date'].tolist())))
        months.sort()
        for m in months:
            df_of_m = df[df['Date'].str[:7] == '%s-%s' % (y, m)]
            current_day = get_current_day(y, m, most_recent_date)
            i = 1
            max_i = 30 # only add a row for this month if it has data thats within max_i of the current day, this is only used on the first month/year
            b = True
            while True:

                # days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                # print(days[current_day.weekday()], current_day.strftime('%Y-%m-%d'))
                x = df_of_m[df_of_m['Date'] == current_day.strftime('%Y-%m-%d')]
                # print(x)
                # input()

                if not x.empty:
                    df2 = df2.append(x)
                    break
                else:
                    current_day += timedelta(days=((1 if b else -1) * i))
                    b = not b
                    i += 1
                    if i > max_i: break
    return df2
def closest_quarter_day(df, most_recent_date):
    # this function will get a value for each quarter in the data thats closest to the current day of the quarter of today
    # this is required because the data is often not on daily intervals (ex: price data is only on workdays)
    df['quarter'] = df['Date'].apply(lambda d : ((int(d[5:7])-1)//3)+1)
    df2 = pd.DataFrame(columns=df.columns)
    years = list(set(map(lambda d : d[:4], df['Date'].tolist())))
    years.sort()
    def get_current_day(y, q, most_recent_date):
        d = most_recent_date.day
        m = int(3*(q-1) + ((most_recent_date.month - 1) % 3) + 1)
        y = int(y)
        # print('get_current_day')
        # print('q', q)
        # print('d', d)
        # print('m', m)
        # print('y', y)
        # print('most_recent_date', most_recent_date, '\n')
        days_in_months = {
            1  : 31,
            2  : 28,
            3  : 31,
            4  : 30,
            5  : 31,
            6  : 30,
            7  : 31,
            8  : 31,
            9  : 30,
            10 : 31,
            11 : 30,
            12 : 31
        }
        if d > days_in_months[m]:
            d = days_in_months[m]
        return datetime(y, m, d)
    # print('most_recent_date', most_recent_date)
    for y in years:
        df_of_y = df[df['Date'].str[:4] == y]
        # print('\ny', y)
        # print('df_of_y')
        # print(df_of_y)
        quarters = list(set(df_of_y['quarter'].tolist()))
        for q in quarters:
            # print('\nq', q)
            df_of_q = df_of_y[df_of_y['quarter'] == q]
            # print('df_of_q')
            # print(df_of_q)
            current_day = get_current_day(y, q, most_recent_date)
            # print('current_day', current_day)
            i = 1
            max_i = 90 # only add a row for this month if it has data thats within max_i of the current day, this is only used on the first month/year
            b = True
            while True:

                # days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                # print(days[current_day.weekday()], current_day.strftime('%Y-%m-%d'))
                # print('cday', current_day)
                x = df_of_q[df_of_q['Date'] == current_day.strftime('%Y-%m-%d')]
                # print(x)
                # input()

                if not x.empty:
                    df2 = df2.append(x)
                    break
                else:
                    current_day += timedelta(days=((1 if b else -1) * i))
                    b = not b
                    i += 1
                    if i > max_i: break
            # print('df2')
            # print(df2)
    return df2
def closest_year_day(df, most_recent_date):
    # this function will get a value for each year in the data thats closest to the current day and month of today
    # this is required because the data is often not on daily intervals (ex: price data is only on workdays)
    df2 = pd.DataFrame(columns=df.columns)
    years = list(set(map(lambda d : d[:4], df['Date'].tolist())))
    years.sort()
    for y in years:
        df_of_y = df[df['Date'].str[:4] == y]
        # print('\ndf_of_y')
        # print(df_of_y)
        current_day = datetime(int(y), most_recent_date.month, most_recent_date.day)
        i = 1
        max_i = 365 # only add a row for this year if it has data thats within max_i of the current month and day, this is only used on the first year
        b = True
        while True:

            # days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # print(days[current_day.weekday()], current_day.strftime('%Y-%m-%d'))
            x = df_of_y[df_of_y['Date'] == current_day.strftime('%Y-%m-%d')]
            # print('current_day', current_day)
            # print(x)
            # input()

            if not x.empty:
                df2 = df2.append(x)
                break
            else:
                current_day += timedelta(days=((1 if b else -1) * i))
                b = not b
                i += 1
                if i > max_i: break
        # print('\ndf2')
        # print(df2)
    return df2
def get_qtr_start_date(y, q):
    y, q = str(int(y)), int(q)
    if q == 1: return y+'-01-01'
    if q == 2: return y+'-04-01'
    if q == 3: return y+'-07-01'
    if q == 4: return y+'-10-01'
def get_qtr_end_date(y, q):
    y, q = str(str(y)), int(q)
    if q == 1: return y+'-03-31'
    if q == 2: return y+'-06-30'
    if q == 3: return y+'-09-30'
    if q == 4: return y+'-12-31'
plot_stock_data()


