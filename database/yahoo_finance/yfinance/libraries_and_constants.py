
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
import yfinance as yf # pip install yfinance --upgrade --no-cache-dir
#               source: https://aroussi.com/post/python-yahoo-finance

# import common utils
REPO_PATH       = str(pathlib.Path(__file__).resolve().parent.parent.parent)
DATA_PATH       = os.path.join(REPO_PATH, 'data')
UTILS_REPO_PATH = os.path.join(str(pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent.parent),
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

# SEC
# https://quant.stackexchange.com/questions/8099/central-index-key-cik-of-all-traded-stocks
TICKER_URL     = 'https://www.sec.gov/files/company_tickers_exchange.json'
TICKER_CIK_URL = 'https://www.sec.gov/include/ticker.txt'
USER_AGENT     = 'Norman Lucius Dickerson (lucius.dickerson@gmail.com)'

# Yahoo Finance
YAHOO_FINANCE_DATA_PATH = os.path.join(DATA_PATH, 'yahoo_finance')
