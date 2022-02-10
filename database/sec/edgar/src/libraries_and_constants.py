

# parse arguments
import argparse
import re
parser = argparse.ArgumentParser(description='This script scrapes, parses, and saves stock fundamental data from Yahoo Finance and the SEC\'s EDGAR database')
# parser.add_argument('-v', '--verbose',       action='store_true',   help='verbose logging')
# parser.add_argument('-c', '--clear',         action='store_true',   help='clear database before collecting new data')
# parser.add_argument('-l', '--lake',          action='store_true',   help='save the raw data downloaded to a data lake')
# parser.add_argument('-r', '--replace',       action='store_true',   help='replace database\'s old values with new values if new value != null')
# parser.add_argument('-d', '--download',      action='store_true',   help='download new raw data from online, else search for data locally (local search used mostly for testing)')
# parser.add_argument('-s', '--last-sub',      action='store_true',   help='continue at the last submission the program parsed') # -s because -l is already taken
parser.add_argument('-t', '--test',          action='store_true',   help='put data in data/test_data intead of data/real_data')
# parser.add_argument('-p', '--pause',         action='store_true',   help='pause between submissions (requires user to press enter to parse next submission')
# parser.add_argument('-q', '--quarter-list',  default=[], nargs='*', help='list of quarters to parse, if not specified all new quarters will be parsed, example: \"-q 2021q1 2021q2 2021q3 2021q4\"')
# parser.add_argument('-x', '--ticker-list',   default=[], nargs='*', help='list of tickers to parse, if not specified all tickers will be parsed, example: \"-t HRB BARK TRNS\"')
args = parser.parse_args()
# for q in args.quarter_list:
#     if not re.match(r'^[0-9]{4}q[1-4]$', q):
#         print('invalid quarter in -q/--quarter-list arg: %s' % q)
#         sys.exit()
# for t in args.ticker_list:
#     if not re.match(r'^[a-zA-Z]+$', t):
#         print('invalid ticker in -x/--ticker-list arg: %s' % t)
#         sys.exit()


# LIBRARIES

# import standard libraries
import os
import sys
import json
import time
import shutil
import pathlib
import requests
from datetime import datetime, date
import re

# import non-standard libraries
import pandas as pd
pd.set_option('display.max_rows', 1111)
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_colwidth', 2000)
pd.set_option('display.width', 100000)
import edgar # https://pypi.org/project/python-edgar/
from bs4 import BeautifulSoup


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
LOG_FILENAME = 'log.txt' # 'log_%s' % datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.txt")
LOG_FILEPATH = os.path.join(
	DATA_SOURCE_PATH, 'logs',
	('test_log' if args.test else 'real_log'),
	LOG_FILENAME)
log = logging_utils.Log(LOG_FILEPATH)
DATA_PATH    = \
	os.path.join(DATA_SOURCE_PATH, 'data', 'test_data') if args.test else \
	os.path.join(DATA_SOURCE_PATH, 'data', 'real_data')
# print('LOG_FILEPATH\t', LOG_FILEPATH)
# print('DATA_PATH\t', DATA_PATH)

# SEC EDGAR API
METADATA_FILENAME = 'metadata.json'
METADATA_FILEPATH = os.path.join(DATA_PATH, METADATA_FILENAME)
TMP_FILINGS_PATH  = os.path.join(DATA_PATH, 'quarterly_filings')
USER_AGENT = 'Norman Lucius Dickerson (lucius.dickerson@gmail.com)'
EARLIEST_YEAR_EDGAR_OFFERS = 1993
VALID_FORM_NAMES=['10-K']#, '10-Q']
SEC_ARCHIVES_BASE_URL = 'https://www.sec.gov/Archives/'
XML_DATA_TAGS = {
	'cik' : {
		'tags' : [
			'identifier'],
		'attributes' : {
			'scheme' : 'http://www.sec.gov/CIK'}},
	'company_name' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'dei:EntityRegistrantName'])),
		'attributes' : {}},
	'dividends_paid' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:PaymentsOfDividends',
			'us-gaap:Dividends'])),
		'attributes' : {}},
	'dividend_per_share' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:CommonStockDividendsPerShareDeclared',
			'us-gaap:CommonStockDividendsPerShareCashPaid'])),
		'attributes' : {}},
	'net_income' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:NetIncomeLoss',
			'us-gaap:ProfitLoss',
			'us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic'])),
		'attributes' : {}},
	'shares_outstanding' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			# 'dei:EntityCommonStockSharesOutstanding', # this tag does not always representing shares outstanding at the exact end of the quarter
			'us-gaap:SharesOutstanding',
			'us-gaap:CommonStockSharesOutstanding'])),
		'attributes' : {}},
	'state_or_country_code' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'dei:EntityIncorporationStateCountryCode'])),
		'attributes' : {}},
	'stock_split' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:StockholdersEquityNoteStockSplitConversionRatio1'])),
		'attributes' : {}},
	'ticker' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'dei:TradingSymbol'])),
		'attributes' : {}},
	'total_assets' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:Assets'])),
		'attributes' : {}},
	'total_equity' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'])),
		'attributes' : {}},
	'total_liabilities'  : {
		'tags' : [
			'us-gaap:liabilities'],
		'attributes' : {}},
	'total_liabilities_and_equity' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:LiabilitiesAndStockholdersEquity'])),
		'attributes' : {}},
	'total_revenue' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'])),
		'attributes' : {}},
	'tbd' : {
		'tags' : list(map(lambda tag : tag.lower(), [
			'tbd'])),
		'attributes' : {}},
}


