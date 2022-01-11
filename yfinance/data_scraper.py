from libraries_and_constants import *

# global variables
log = logging_utils.Log(LOG_FILEPATH)



def parse_ticker_list_from_sec(
    num_indents=0,
    new_line_start=True):

    log.print('parsing ticker list from SEC',
        num_indents=num_indents,
        new_line_start=new_line_start)
    log.print('TICKER_URL: %s' % TICKER_URL, num_indents=num_indents+1)
    response = requests.get(TICKER_URL, headers={'User-Agent' : USER_AGENT})
    data = json.loads(response.text)
    df = pd.DataFrame(data['data'], columns=data['fields'])
    log.print('done. parsed %d tickers' % df.shape[0], num_indents=num_indents)
    return df
def parse_ticker_list_from_sec_old(
    num_indents=0,
    new_line_start=True):

    log.print('parsing ticker list from SEC',
        num_indents=num_indents,
        new_line_start=new_line_start)
    log.print('TICKER_CIK_URL: %s' % TICKER_CIK_URL, num_indents=num_indents+1)
    response = requests.get(TICKER_CIK_URL, headers={'User-Agent' : USER_AGENT})
    df = pd.DataFrame(columns=['ticker', 'cik'])
    num_lines = len(response.text.split('\n'))
    for i, line in enumerate(response.text.split('\n')):
        ticker, cik = tuple(line.split('\t'))
        df = df.append(pd.DataFrame({
            'ticker' : [ticker],
            'cik'    : [cik]
        }))
        log.print_same_line(
            'ticker %d of %d: %s' % (i+1, num_lines, ticker),
            num_indents=num_indents+1)
    df.reset_index(inplace=True, drop=True)
    log.print('done.', num_indents=num_indents)
    return df

def scrape_yahoo_finance(
    ticker,
    num_indents=0,
    new_line_start=False):

    log.print('scraping yahoo finance ... ',
        num_indents=num_indents,
        new_line_start=new_line_start)

    company = yf.Ticker(ticker)
    raw, processed, success = parse_data(company, num_indents=num_indents+1)
    data = {
        'raw'       : raw,
        'processed' : processed
    }
    if success:
        log.continue_prev_line('done')
    else:
        log.print('done', num_indents=num_indents)
    return data    
def parse_data(
    company,
    num_indents=0,
    new_line_start=False):

    raw, processed = {}, {}
    success = True

    try:
        dct = company.info
        raw['info'] = dct
        sector    = dct['sector']   if 'sector'   in dct.keys() else None
        industry  = dct['industry'] if 'industry' in dct.keys() else None
        country   = dct['country']  if 'country'  in dct.keys() else None
        cur_yield = None if 'dividendYield' not in dct.keys() or dct['dividendYield'] == None else \
            '%.1f %%' % (100.0 * float(dct['dividendYield']))
        ex_dividend_date = None if 'exDividendDate' not in dct.keys() or dct['exDividendDate'] == None else \
            datetime.utcfromtimestamp(dct['exDividendDate']).strftime('%Y-%m-%d')
        processed['info'] = {
            'name'             : dct['longName'],
            'ticker'           : dct['symbol'],
            'asset_type'       : dct['quoteType'],
            'sector'           : sector,
            'industry'         : industry,
            'country'          : country,
            'current_yield'    : cur_yield,
            'ex_dividend_date' : ex_dividend_date
        }
    except Exception as e:
        log.print('failed to parse \'info\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    try:
        df = company.history(period="max")
        raw['daily_price_data'] = df.copy()
        df = df[['Close']]
        df.rename(columns={'Close' : 'Closing Price'}, inplace=True)
        processed['daily_price_data'] = df
    except Exception as e:
        log.print('failed to parse \'price_history\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    if dct['quoteType'] != 'EQUITY':
        return raw, processed, success

    try:
        df = company.dividends
        raw['dividends_per_share'] = df
        processed['dividends_per_share'] = df
    except Exception as e:
        log.print('failed to parse \'dividends_per_share\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    try:
        df = company.splits
        raw['stock_splits'] = df
        processed['stock_splits'] = df
    except Exception as e:
        log.print('failed to parse \'stock_splits\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    try:
        df = company.quarterly_financials
        raw['quarterly_financials'] = df.copy()
        # df            = df.T
        # df['Year']    = df.index.year
        # df['Quarter'] = df.index.quarter
        # df            = df[['Year', 'Quarter', 'Total Revenue']]
        # df.sort_values(by=['Year', 'Quarter'], inplace=True)
        # df.reset_index(drop=True, inplace=True)
        # print(df)
    except Exception as e:
        log.print('failed to parse \'quarterly_financials\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    try:
        df = company.quarterly_balance_sheet
        raw['quarterly_balance_sheet'] = df.copy()
        df = df.T
        if not df.empty:
            df['Year'] = df.index.year
            df['Quarter'] = df.index.quarter
            df.rename(columns={'Total Liab' : 'Total Liabilities'}, inplace=True)
            cols = ['Year', 'Quarter', 'Total Assets', 'Total Liabilities', 'Common Stock']
            for col in cols:
                if col not in df.columns.tolist():
                    df[col] = 0
            df = df[cols]
            df.sort_values(by=['Year', 'Quarter'], inplace=True)
            df.reset_index(drop=True, inplace=True)
        processed['quarterly_fundamentals'] = df
        # print(processed['quarterly_fundamentals'])
    except Exception as e:
        log.print('failed to parse \'quarterly_balance_sheet\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    try:
        df = company.quarterly_cashflow
        raw['quarterly_cashflow'] = df.copy()
        df = df.T
        # print(df)
        df['Year'] = df.index.year
        df['Quarter'] = df.index.quarter
        if 'Dividends Paid' not in df.columns.tolist():
            df['Dividends Paid'] = 0
        df['Dividends Paid'] = -df['Dividends Paid']
        df = df[[
            'Year',
            'Quarter',
            'Dividends Paid']]#,
            # 'Issuance Of Stock',
            # 'Repurchase Of Stock',
            # 'Capital Expenditures']]
        df.sort_values(by=['Year', 'Quarter'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        processed['quarterly_fundamentals'] = \
            processed['quarterly_fundamentals'].merge(
                df, how='outer', on=['Year', 'Quarter'])
        # print(processed['quarterly_fundamentals'])
    except Exception as e:
        log.print('failed to parse \'quarterly_cashflow\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    try:
        df = company.quarterly_earnings
        raw['quarterly_earnings'] = df.copy()
        df.reset_index(inplace=True) # make index a column
        if df.empty:
            processed['quarterly_fundamentals']['Total Cash Inflow']  = 0
            processed['quarterly_fundamentals']['Total Cash Outflow'] = 0
        else:
            df['Year']    = df['Quarter'].apply(lambda q : int(q.split('Q')[1]))
            df['Quarter'] = df['Quarter'].apply(lambda q : int(q.split('Q')[0]))
            df['Total Cash Inflow']  = df['Revenue']
            df['Total Cash Outflow'] = df['Revenue'] - df['Earnings']
            df = df[['Year', 'Quarter', 'Total Cash Inflow', 'Total Cash Outflow']].copy()
            df.sort_values(by=['Year', 'Quarter'], inplace=True)
            df.reset_index(drop=True, inplace=True)
            processed['quarterly_fundamentals'] = \
                processed['quarterly_fundamentals'].merge(
                    df, how='outer', on=['Year', 'Quarter'])
        # print(processed['quarterly_fundamentals'])

        processed['quarterly_fundamentals'].fillna(0, inplace=True)
        processed['quarterly_fundamentals'] = \
            processed['quarterly_fundamentals'].astype('int64')
    except Exception as e:
        log.print('failed to parse \'quarterly_earnings\'', num_indents=num_indents)
        log.print('exception:', num_indents=num_indents+1)
        log.print(e.message, num_indents=num_indents+2)
        success = False

    return raw, processed, success
def save_data(
    data,
    num_indents=0,
    new_line_start=False):

    log.print(
        'saving data ..............',
        num_indents=num_indents,
        new_line_start=new_line_start)

    ticker = data['processed']['info']['ticker']

    raw_ticker_dir = os.path.join(YAHOO_FINANCE_DATA_PATH, 'raw', ticker)
    if not os.path.exists(raw_ticker_dir): os.mkdir(raw_ticker_dir)
    for filename, x in data['raw'].items():
        filepath = os.path.join(raw_ticker_dir, filename)
        if filename == 'info':
            with open(filepath+'.json', 'w') as f:
                json.dump(x, f, indent=4)
        else: x.to_csv(filepath+'.csv')

    processed_ticker_dir = os.path.join(YAHOO_FINANCE_DATA_PATH, 'processed', ticker)
    if not os.path.exists(processed_ticker_dir): os.mkdir(processed_ticker_dir)
    for filename, x in data['processed'].items():
        filepath = os.path.join(processed_ticker_dir, filename)
        if filename == 'info':
            with open(filepath+'.json', 'w') as f:
                json.dump(x, f, indent=4)
        else: x.to_csv(filepath+'.csv')

    log.continue_prev_line(' done')



if __name__ == '__main__':
    df = parse_ticker_list_from_sec()
    log.print('scraping data for %d tickers' % df.shape[0], new_line_start=True)
    for i, row in df.iterrows():
        if i < 677: continue # for testing purposes only
        ticker = row['ticker']
        log.print('ticker %d of %d: %s' % (i+1, df.shape[0], ticker),
            num_indents=1, new_line_start=True)
        data = scrape_yahoo_finance(ticker, num_indents=2)
        save_data(data, num_indents=2)

        # rate limit of 2k requests per hour
        # https://www.google.com/search?q=yahoo+finance+api+rate+limit&oq=yahoo+finance+api+rate+limit&aqs=chrome..69i57j69i64.8611j0j7&sourceid=chrome&ie=UTF-8
        # or is it? https://github.com/ranaroussi/yfinance/issues/862
        time.sleep(20)
        # input()


