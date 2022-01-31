
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
import re
import zipfile
import io
import argparse
# import non-standard libraries
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 16)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_colwidth', 20)
pd.set_option('display.width', 100000)
from bs4 import BeautifulSoup
import yfinance as yf
import colored_traceback
colored_traceback.add_hook()

# import common utils
REPO_PATH           = str(pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent)
DATA_SOURCE_PATH    = str(pathlib.Path(__file__).resolve().parent.parent)
UTILS_REPO_PATH     = os.path.join(str(pathlib.Path(REPO_PATH).resolve().parent.parent.parent),
						'tech', 'software', 'projects', 'python-common-utils')
LOG_UTIL_PATH       = os.path.join(UTILS_REPO_PATH, 'utils', 'logging', 'src')
# print('REPO_PATH       ', REPO_PATH)
# print('DATA_SOURCE_PATH', DATA_SOURCE_PATH)
# print('UTILS_REPO_PATH ', UTILS_REPO_PATH)
# print('LOG_UTIL_PATH   ', LOG_UTIL_PATH)
# sys.exit()
sys.path.append(LOG_UTIL_PATH); import logging_utils


# CONSTANTS

# local file and directory paths
LOG_FILENAME           = 'log.txt' # 'log_%s' % datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.txt")
LOG_FILEPATH           = os.path.join(DATA_SOURCE_PATH, 'logs', LOG_FILENAME)
DATA_PATH              = os.path.join(DATA_SOURCE_PATH, 'data')
TMP_FILINGS_PATH       = os.path.join(DATA_PATH, 'lake')
DATA_WAREHOUSE_PATH    = os.path.join(DATA_PATH, 'warehouse')
DATA_STOCKS_PATH       = os.path.join(DATA_WAREHOUSE_PATH, 'stocks')
SIC_CODES_FILEPATH     = os.path.join(DATA_WAREHOUSE_PATH, 'sic_codes.csv')
COUNTRY_CODES_FILEPATH = os.path.join(DATA_WAREHOUSE_PATH, 'state_and_country_codes.csv')
TICKER_CODES_FILEPATH  = os.path.join(DATA_WAREHOUSE_PATH, 'ticker_list.csv')
METADATA_FILEPATH      = os.path.join(DATA_WAREHOUSE_PATH, 'metadata.json')
QUALITY_REPORT_PATH    = os.path.join(DATA_PATH, 'quality_report')
x = {
	chart : [
		os.path.join(QUALITY_REPORT_PATH, chart),
		os.path.join(QUALITY_REPORT_PATH, chart, 'variable_metrics.csv'),
		os.path.join(QUALITY_REPORT_PATH, chart, 'constant_metrics.json')
	] for chart in [
		'stock_vs_quarter',
		'metric_vs_quarter',
		'stock_vs_metric',
		'price_data_stock_vs_day']}
QUALITY_REPORT_PATHS   = pd.DataFrame({
	chart : [
		os.path.join(QUALITY_REPORT_PATH, chart),
		os.path.join(QUALITY_REPORT_PATH, chart, 'variable_metrics.csv'),
		os.path.join(QUALITY_REPORT_PATH, chart, 'constant_metrics.json')
	] for chart in [
		'stock_vs_quarter',
		'metric_vs_quarter',
		'stock_vs_metric',
		'price_data_stock_vs_day']},
	index=[
		'chart',
		'variable',
		'constant'])
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

# other constants
DESCRIPTION = 'This script scrapes, parses, and saves stock fundamental data from Yahoo Finance and the SEC\'s Financial Statements Data Sets'
VALID_FORM_TYPES = ['10-K', '10-Q']
DATA_TAGS = { # key = local database's column_names, value = list of possible tags in submission
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
    	'RevenueFromContractWithCustomerExcludingAssessedTax'],
	'shares_outstanding' : [
		'SharesOutstanding',
		'CommonStockSharesOutstanding',
		'WeightedAverageNumberOfShareOutstandingBasicAndDiluted',
		'WeightedAverageNumberOfSharesOutstandingBasic'],
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
		'total_revenue',
		'total_expenses',
		'net_income',
		'earnings_per_share',
		'dividends_paid',
		'sec_urls_all_files',
		'sec_urls_filing_details',
		'sec_urls_XML',
		'sec_urls_HTML',
		'sec_urls_TXT'
	] # this list of fundamental metrics needs to be equal to or a subset of the metrics the program actually searches for and puts in the data['fundamentals'] dict in the function SubmissionParser.parse_submissions()
}


