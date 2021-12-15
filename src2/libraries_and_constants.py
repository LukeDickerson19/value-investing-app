
# LIBRARIES

# import standard libraries
import os
import sys
import json
import time
import shutil
import pathlib
from datetime import datetime

# import non-standard libraries
from bs4 import BeautifulSoup

# import common utils
REPO_PATH       = str(pathlib.Path(__file__).resolve().parent.parent)
DATA_PATH       = os.path.join(REPO_PATH, 'data')
UTILS_REPO_PATH = os.path.join(str(pathlib.Path(__file__).resolve().parent.parent.parent), 'python-common-utils')
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
USER_AGENT = 'Norman Lucius Dickerson (lucius.dickerson@gmail.com)'
EARLIEST_YEAR_EDGAR_OFFERS = 1993
VALID_FORM_NAMES=['10-Q', '10-K']
SEC_ARCHIVES_BASE_URL = 'https://www.sec.gov/Archives/'
