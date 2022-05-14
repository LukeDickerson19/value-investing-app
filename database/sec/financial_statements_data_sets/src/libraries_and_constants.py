

# parse arguments
import argparse
import re
parser = argparse.ArgumentParser(description='This script scrapes, parses, and saves stock fundamental data from Yahoo Finance and the SEC\'s Financial Statements Data Sets')
parser.add_argument('-v', '--verbose',       action='store_true',   help='verbose logging')
parser.add_argument('-c', '--clear',         action='store_true',   help='clear database before collecting new data')
parser.add_argument('-l', '--lake',          action='store_true',   help='save the raw data downloaded to a data lake')
parser.add_argument('-r', '--replace',       action='store_true',   help='replace database\'s old values with new values if new value != null')
parser.add_argument('-d', '--download',      action='store_true',   help='download new raw data from online, else search for data locally (local search used mostly for testing)')
parser.add_argument('-s', '--last-sub',      action='store_true',   help='continue at the last submission the program parsed') # -s because -l is already taken
parser.add_argument('-t', '--test',          action='store_true',   help='put data in data/test_data instead of data/real_data')
parser.add_argument('-p', '--pause',         action='store_true',   help='pause between submissions (requires user to press enter to parse next submission)')
parser.add_argument('-q', '--quarter-list',  default=[], nargs='*', help='list of quarters to parse, if not specified all new quarters will be parsed, example: \"-q 2021q1 2021q2 2021q3 2021q4\"')
parser.add_argument('-x', '--ticker-list',   default=[], nargs='*', help='list of tickers to parse, if not specified all tickers will be parsed, example: \"-t HRB BARK TRNS\"')
args = parser.parse_args()
for q in args.quarter_list:
    if not re.match(r'^[0-9]{4}q[1-4]$', q):
        print('invalid quarter in -q/--quarter-list arg: %s' % q)
        sys.exit()
for t in args.ticker_list:
    if not re.match(r'^[a-zA-Z]+$', t):
        print('invalid ticker in -x/--ticker-list arg: %s' % t)
        sys.exit()

# LIBRARIES

# import standard libraries
import os
import sys
import json
import time
import copy
import shutil
import pathlib
import requests
from datetime import datetime, date
import zipfile
import io

# import non-standard libraries
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 16)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_colwidth', 20)
pd.set_option('display.width', 100000)
from bs4 import BeautifulSoup
import yfinance as yf
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable

# import common utils
REPO_PATH           = str(pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent)
DATA_SOURCE_PATH    = str(pathlib.Path(__file__).resolve().parent.parent)
# UTILS_REPO_PATH     = os.path.join(str(pathlib.Path(REPO_PATH).resolve().parent.parent.parent),
# 						'tech', 'software', 'projects', 'python-common-utils')
# LOG_UTIL_PATH       = os.path.join(UTILS_REPO_PATH, 'utils', 'logging', 'src')
LOG_UTIL_PATH       = os.path.join(REPO_PATH, 'common_utils')
# print('REPO_PATH       ', REPO_PATH)
# print('DATA_SOURCE_PATH', DATA_SOURCE_PATH)
# # print('UTILS_REPO_PATH ', UTILS_REPO_PATH)
# print('LOG_UTIL_PATH   ', LOG_UTIL_PATH)
# sys.exit()
sys.path.append(LOG_UTIL_PATH); import logging_utils


# CONSTANTS

# local file and directory paths
LOG_FILENAME           = 'log.txt' # 'log_%s' % datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.txt")
LOG_FILEPATH           = os.path.join(
	DATA_SOURCE_PATH, 'logs',
	('test_log' if args.test else 'real_log'),
	LOG_FILENAME)
log = logging_utils.Log(LOG_FILEPATH)
DATA_PATH              = \
	os.path.join(DATA_SOURCE_PATH, 'data', 'test_data') if args.test else \
	os.path.join(DATA_SOURCE_PATH, 'data', 'real_data')
TMP_FILINGS_PATH       = os.path.join(DATA_PATH, 'lake')
DATA_WAREHOUSE_PATH    = os.path.join(DATA_PATH, 'warehouse')
DATA_STOCKS_PATH       = os.path.join(DATA_WAREHOUSE_PATH, 'stocks')
SIC_CODES_FILEPATH     = os.path.join(DATA_WAREHOUSE_PATH, 'sic_codes.csv')
COUNTRY_CODES_FILEPATH = os.path.join(DATA_WAREHOUSE_PATH, 'state_and_country_codes.csv')
TICKER_CODES_FILEPATH  = os.path.join(DATA_WAREHOUSE_PATH, 'ticker_list.csv')
METADATA_FILEPATH      = os.path.join(DATA_WAREHOUSE_PATH, 'metadata.json')
METADATA_TEMPLATE      = {
    "quarters_downloaded"    : [],
    "quarters_parsed"        : {
        "quarters" : [],
        "count"    : 0,
    },
    "last_sub_parsed"        : {
        "qtr"       : None,
        "cik"       : None,
        "form_type" : None
    },
    "total_number_of_stocks" : 0,
    "number_of_metrics" : {
        "total"    : 0,
        "variable" : 0,
        "constant" : 0
    },
    "price_data" : {
        "min_date" : np.nan,
        "max_date" : np.nan,
        "num_stocks_with_price_data" : 0
    }
}
QUALITY_REPORT_PATH    = os.path.join(DATA_PATH, 'quality_report')
QUALITY_REPORT_PATHS   = {
	'stock_vs_quarter' : {
		'chart'    : os.path.join(QUALITY_REPORT_PATH, 'stock_vs_quarter'),
		'variable' : os.path.join(QUALITY_REPORT_PATH, 'stock_vs_quarter', 'variable_metrics.csv'),
		'constant' : os.path.join(QUALITY_REPORT_PATH, 'stock_vs_quarter', 'constant_metrics.json')
	},
	'metric_vs_quarter' : {
		'chart'    : os.path.join(QUALITY_REPORT_PATH, 'metric_vs_quarter'),
		'variable' : os.path.join(QUALITY_REPORT_PATH, 'metric_vs_quarter', 'variable_metrics.csv'),
		'constant' : os.path.join(QUALITY_REPORT_PATH, 'metric_vs_quarter', 'constant_metrics.json')
	},
	'stock_vs_metric' : {
		'chart'    : os.path.join(QUALITY_REPORT_PATH, 'stock_vs_metric'),
		'variable' : os.path.join(QUALITY_REPORT_PATH, 'stock_vs_metric', 'variable_metrics.csv'),
		'constant' : os.path.join(QUALITY_REPORT_PATH, 'stock_vs_metric', 'constant_metrics.csv')
	},
	'price_data_stock_vs_day' : {
		'chart'    : os.path.join(QUALITY_REPORT_PATH, 'price_data_stock_vs_day'),
		'variable' : os.path.join(QUALITY_REPORT_PATH, 'price_data_stock_vs_day', 'price_data_coverage.csv')
	}
}
# print('LOG_FILEPATH       ', LOG_FILEPATH)
# print('DATA_PATH          ', DATA_PATH)
# print('TMP_FILINGS_PATH   ', TMP_FILINGS_PATH)
# print('DATA_WAREHOUSE_PATH', DATA_WAREHOUSE_PATH)
# print('QUALITY_REPORT_PATH', QUALITY_REPORT_PATH)
# print('METADATA_FILEPATH  ', METADATA_FILEPATH)

# URL paths
TICKER_URL = 'https://www.sec.gov/files/company_tickers_exchange.json'
USER_AGENT = 'Norman Lucius Dickerson (lucius.dickerson@gmail.com)'
FINANCIAL_STATEMENTS_DATA_SETS_URL = 'https://www.sec.gov/dera/data/financial-statement-data-sets.html'
FINANCIAL_STATEMENTS_DATA_SETS_BASE_DOWNLOAD_URL = \
	'https://www.sec.gov/files/dera/data/financial-statement-data-sets/{year}q{quarter}.zip' # format = "YYYYqQ.zip", ex: "2021q4.zip"
ALL_FILES_BASE_URL = 'http://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/'
SEC_ARCHIVES_BASE_URL = 'https://www.sec.gov/Archives/'
SEC_COMPANY_INFO_URL = 'https://data.sec.gov/submissions/CIK{zero_padded_cik}.json'

# other constants
VALID_FORM_TYPES = ['10-Q', '10-K'] # parse 10-Qs first so the 10-Ks will likely have more data to work with
DATA_TAGS = { # key = local database's column_names, value = list of possible tags in submission
	'cash_flow' : [
		'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect'
	],
	'company_name' : [
		'EntityRegistrantName'],
	'dividends_paid' : [
		'PaymentsOfDividends',
		'Dividends'],
	# 'dividends_per_share' : [
	# 	'CommonStockDividendsPerShareDeclared',
	# 	'CommonStockDividendsPerShareCashPaid'],
	'earnings_per_share' : [
		'EarningsPerShareBasic',
		'EarningsPerShareBasicAndDiluted'],
	'net_income' : [
		'NetIncomeLoss',
		'NetIncomeLossAvailableToCommonStockholdersBasic',
		'ProfitLoss'],
	'ticker' : [
		'TradingSymbol'],
	'total_assets' : [
		'Assets',
		'Totalassets',
		'AssetsNet'],
	'total_equity' : [
		'StockholdersEquity'],
	'total_expenses' : [
		'TotalExpenses'],
	'total_liabilities' : [
		'Liabilities'],
	'total_liabilities_and_equity' : [
		'LiabilitiesAndStockholdersEquity'],
    'total_revenue' : [
    	'Revenues',
    	'RevenueFromContractWithCustomerIncludingAssessedTax'],
	'shares_outstanding' : [
		'WeightedAverageNumberOfSharesOutstandingBasic',
		'SharesOutstanding',
		'CommonStockSharesOutstanding',
		'WeightedAverageNumberOfShareOutstandingBasicAndDiluted'],
	'state_or_country_code' : [
		'EntityIncorporationStateCountryCode']
}
DATA_COLUMNS = {
	'daily_price_data'           : ['Close', 'Volume'],
	'dividend_per_share_history' : ['Dividends'],
	'stock_split_history'        : ['Stock Splits'],
	'fundamentals'               : [
		'quarter',
		'year',
		'shares_outstanding',
		'total_assets',
		'total_liabilities',
		'net_income',
		# 'cash_flow',
		'earnings_per_share',
		'dividends_paid',
		'sec_urls_all_files',
		'sec_urls_filing_details',
		'sec_urls_XML',
		'sec_urls_HTML',
		'sec_urls_TXT'
	]
}
# note: 
# the list of fundamental metrics in DATA_COLUMNS needs to be equal to the list metrics the program actually searches for
# and puts in the data['fundamentals'] dict in the function SubmissionParser.parse_submissions().
# DATA_COLUMNS is used by the SubmissionParser.save_fundamentals() function