print()

# parse arguments
import argparse
import pathlib
import pandas as pd
import re
import os
import sys


VALID_METRICS = [
    'sub_qtr_enddate',
    'quarter',
    'year',
    'shares_outstanding',
    'total_assets',
    'total_liabilities',
    'net_income',
    'earnings_per_share',
    'dividends_paid',
    'sec_urls_all_files',
    'sec_urls_filing_details',
    'sec_urls_XML',
    'sec_urls_HTML',
    'sec_urls_TXT'
]
parser = argparse.ArgumentParser(
    description='This script prints the specified fundamental metrics of the specified stock tickers.\n\n    example command:\n        %s\n\n    valid metric values:\n        %s%s' % (
        'python print_fundamentals_of_specific_stocks.py -m year quarter net_income shares_outstanding earnings_per_share -x AAPL MSFT AMZN TSLA',
        '\n        '.join(VALID_METRICS),
        '\n\nThe other metric files can simply be printed with the "cat" command.\n\n    example:\n        cat value-investing-app/database/sec/financial_statements_data_sets/data/real_data/warehouse/stocks/1724344/stock_split_history.csv'),
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test',          action='store_true',   help='put data in data/test_data instead of data/real_data')
parser.add_argument('-x', '--ticker-list',   default=[], nargs='*', help='list of tickers to parse, if not specified all tickers will be parsed, example: \"-x AAPL MSFT AMZN TSLA\"')
parser.add_argument('-c', '--cik-list',      default=[], nargs='*', help='list of CIKs to parse, if not specified all CIKs will be parsed, example: \"-c 320193 789019 1018724 1318605\"')
parser.add_argument('-m', '--metrics-list',  default=[], nargs='*', help='list of metrics to display (defaults to all)')
parser.add_argument('-q', '--quarter-list',  default=[], nargs='*', help='list of quarters to parse, if not specified all new quarters will be parsed, example: \"-q 2021q1 2021q2 2021q3 2021q4\"')
args = parser.parse_args()
for q in args.quarter_list:
    if not re.match(r'^[0-9]{4}q[1-4]$', q):
        print('invalid quarter in -q/--quarter-list arg: %s' % q)
        sys.exit()
if args.metrics_list == []:
    print('must enter metrics_list')
    print('    example argument: \"-m quarter year net_income shares_outstanding earnings_per_share\"')
    print('\n    all valid metrics:')
    for m in VALID_METRICS: print('        ', m)
    print()
    sys.exit()
if args.ticker_list == [] and args.cik_list == []:
    print('must enter ticker_list or cik_list')
    print('    example ticker_list argument: \"-x AAPL MSFT AMZN TSLA\"')
    print('    example cik_list argument:    \"-c 320193 789019 1018724 1318605\"')
    print()
    sys.exit()
DATA_SOURCE_PATH       = str(pathlib.Path(__file__).resolve().parent.parent)
DATA_PATH              = \
    os.path.join(DATA_SOURCE_PATH, 'data', 'test_data') if args.test else \
    os.path.join(DATA_SOURCE_PATH, 'data', 'real_data')
DATA_WAREHOUSE_PATH    = os.path.join(DATA_PATH, 'warehouse')
DATA_STOCKS_PATH       = os.path.join(DATA_WAREHOUSE_PATH, 'stocks')
TICKER_CODES_FILEPATH  = os.path.join(DATA_WAREHOUSE_PATH, 'ticker_cik_mapping.csv')


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

def print_fundaments(cik):
    filepath = os.path.join(DATA_STOCKS_PATH, cik, 'fundamentals.csv')
    df = pd.read_csv(filepath)
    if args.quarter_list != []:
        df['qtr_str'] = df[['year', 'quarter']].apply(lambda s : 'q'.join(
            list(map(lambda x : str(x), s))), axis=1)
        df = df[df['qtr_str'].isin(args.quarter_list)]
    df = df[args.metrics_list]
    print(df)


ticker_df = get_ticker_mapping_from_sec()
print()
if args.ticker_list != []:
    ticker_cik_mapping = {}
    for ticker in args.ticker_list:
        cik = ticker_df[ticker_df['ticker'] == ticker]['cik'].tolist()
        if cik != []:
            ticker_cik_mapping[ticker] = cik[0]
    if len(args.ticker_list) > len(ticker_cik_mapping.keys()):
        missing_tickers = list(set(args.ticker_list) - set(ticker_cik_mapping.keys()))
        print('missing ticker CIK mapping for %d of the %d ticker value(s) requested: %s' % (
            len(missing_tickers),
            len(args.ticker_list),
            ' '.join(missing_tickers)))
elif args.cik_list != []:
    ticker_cik_mapping = {}
    for cik in args.cik_list:
        ticker = ticker_df[ticker_df['cik'] == cik]['ticker'].tolist()
        if ticker != []:
            ticker_cik_mapping[ticker[0]] = cik
    if len(args.cik_list) > len(ticker_cik_mapping.keys()):
        missing_ciks = list(set(args.cik_list) - set(ticker_cik_mapping.values()))
        print('missing ticker CIK mapping for %d of the %d CIK value(s) requested: %s' % (
            len(missing_ciks),
            len(args.cik_list),
            ' '.join(missing_ciks)))

print('%d stocks to display fundamental data for:\n    ticker  cik' % len(ticker_cik_mapping.keys()))
for ticker, cik in ticker_cik_mapping.items():
    print('    %s%s' % (ticker.ljust(8, ' '), cik))
# print(' '.join(map(lambda , ticker_cik_mapping))))
# print('%d\ttickers  to display fundamental data for: %s' % (len(ticker_list), ' '.join(ticker_list)))
# print('%d\tCIKs     to display fundamental data for: %s' % (len(cik_list), ' '.join(cik_list)))
if args.quarter_list != []:
    print('%d\tquarters to display fundamental data for: %s' % (len(args.quarter_list), args.quarter_list))

print()
for i, (ticker, cik) in enumerate(ticker_cik_mapping.items()):
    print('\npress enter to view fundamental data for stock %d of %d: ticker=%s CIK=%s' % (
        i+1, len(ticker_cik_mapping.keys()), ticker, cik))
    input()
    print_fundaments(cik)

print()