

# parse arguments
import argparse
import re
parser = argparse.ArgumentParser(description='This script scrapes, parses, and saves stock fundamental data from Yahoo Finance and the SEC\'s Financial Statements Data Sets')
parser.add_argument('-v', '--verbose',       action='store_true',     help='verbose logging')
parser.add_argument('-t', '--test',          action='store_true',     help='put data in data/test_data intead of data/real_data')
parser.add_argument('-p', '--plot',          action='store_true',     help='show plots of line of best fit for price and dividend of each stock')
# parser.add_argument('-q', '--quarter-list',  default=[], nargs='*', help='list of quarters to parse, if not specified all new quarters will be parsed, example: \"-q 2021q1 2021q2 2021q3 2021q4\"')
args = parser.parse_args()
# for q in args.quarter_list:
#     if not re.match(r'^[0-9]{4}q[1-4]$', q):
#         print('invalid quarter in -q/--quarter-list arg: %s' % q)
#         sys.exit()

# LIBRARIES

# import standard libraries
import os
import sys
import json
import time
import copy
import shutil
import pathlib
from datetime import datetime, date, timedelta

# import non-standard libraries
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 56)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_colwidth', 20)
pd.set_option('display.width', 100000)
import matplotlib.pyplot as plt

# import common utils
REPO_PATH           = str(pathlib.Path(__file__).resolve().parent.parent.parent)
STRATEGY_PATH       = str(pathlib.Path(__file__).resolve().parent)
DATA_SOURCE_PATH    = os.path.join(REPO_PATH, 'database', 'sec', 'financial_statements_data_sets')
UTILS_REPO_PATH     = os.path.join(str(pathlib.Path(REPO_PATH).resolve().parent.parent.parent),
						'tech', 'software', 'projects', 'python-common-utils')
LOG_UTIL_PATH       = os.path.join(UTILS_REPO_PATH, 'utils', 'logging', 'src')
# print('REPO_PATH       ', REPO_PATH)
# print('STRATEGY_PATH   ', STRATEGY_PATH)
# print('DATA_SOURCE_PATH', DATA_SOURCE_PATH)
# print('UTILS_REPO_PATH ', UTILS_REPO_PATH)
# print('LOG_UTIL_PATH   ', LOG_UTIL_PATH)
# sys.exit()
sys.path.append(LOG_UTIL_PATH); import logging_utils


# CONSTANTS

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

SIC_CODES_FILEPATH     = os.path.join(DATA_WAREHOUSE_PATH, 'sic_codes.csv')
COUNTRY_CODES_FILEPATH = os.path.join(DATA_WAREHOUSE_PATH, 'state_and_country_codes.csv')
TICKER_CODES_FILEPATH  = os.path.join(DATA_WAREHOUSE_PATH, 'ticker_list.csv')
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

# other constants
