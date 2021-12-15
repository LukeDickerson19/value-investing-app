
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

# import non-standard libraries
import pandas as pd
pd.set_option('display.max_rows', 1111)
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_colwidth', 2000)
pd.set_option('display.width', 100000)
import edgar
from bs4 import BeautifulSoup


# import common utils
REPO_PATH       = str(pathlib.Path(__file__).resolve().parent.parent)
DATA_PATH       = os.path.join(REPO_PATH, 'data')
UTILS_REPO_PATH = os.path.join(str(pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent),
	'tech', 'software', 'projects', 'python-common-utils')
LOG_UTIL_PATH   = os.path.join(UTILS_REPO_PATH, 'utils', 'logging', 'src')
# print('REPO_PATH\t', REPO_PATH)
# print('DATA_PATH\t', DATA_PATH)
# print('UTILS_REPO_PATH\t', UTILS_REPO_PATH)
# print('LOG_UTIL_PATH\t', LOG_UTIL_PATH)
# sys.exit()
sys.path.append(LOG_UTIL_PATH); import logging_utils


# CONSTANTS
LOG_FILENAME = 'log.txt' # 'log_%s' % datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.txt")
LOG_FILEPATH = os.path.join(REPO_PATH, 'logs', LOG_FILENAME)
# print('LOG_FILEPATH\t', LOG_FILEPATH)

# SEC EDGAR API
METADATA_FILENAME = 'metadata.json'
METADATA_FILEPATH = os.path.join(DATA_PATH, METADATA_FILENAME)
TMP_FILINGS_PATH  = os.path.join(DATA_PATH, 'quarterly_filings')
USER_AGENT = 'Norman Lucius Dickerson (lucius.dickerson@gmail.com)'
EARLIEST_YEAR_EDGAR_OFFERS = 1993
VALID_FORM_NAMES=['10-Q', '10-K']
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
			'us-gaap:NetIncomeLoss'])),
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