from libraries_and_constants import *

# global variables
log = logging_utils.Log(LOG_FILEPATH)



def clear_and_reset_database(
    num_indents=0,
    new_line_start=True):

    log.print('clearing and reseting database at:',
        num_indents=num_indents,
        new_line_start=new_line_start)
    repo_data_path = DATA_PATH[DATA_PATH.index('value-investing-app'):]
    log.print(repo_data_path, num_indents=num_indents+1)
    if os.path.exists(DATA_PATH):
        shutil.rmtree(DATA_PATH)
    os.mkdir(DATA_PATH)
    os.mkdir(DATA_WAREHOUSE_PATH)
    os.mkdir(DATA_STOCKS_PATH)
    os.mkdir(QUALITY_REPORT_PATH)
    for c in QUALITY_REPORT_PATHS.columns.values:
        os.mkdir(QUALITY_REPORT_PATHS[c]['chart'])

    metadata_template = {
        "quarters_downloaded" : [],
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
    with open(METADATA_FILEPATH, 'w') as f:
        json.dump(metadata_template, f, indent=4, sort_keys=True)
    log.print('done', num_indents=num_indents)
def get_standard_industrial_codes(
    download=False,
    verbose=False,
    num_indents=0,
    new_line_start=True):

    log.print('getting SIC codes:',
        num_indents=num_indents,
        new_line_start=new_line_start)

    # get codes from local csv file
    if not download:
        try:
            df = pd.read_csv(SIC_CODES_FILEPATH, index_col=0, dtype=str)
        except:
            df = pd.DataFrame()
        repo_filepath = SIC_CODES_FILEPATH[SIC_CODES_FILEPATH.index('value-investing-app'):]
        if df.shape[0] > 0:
            log.print('found SIC codes locally at:',
                num_indents=num_indents+1)
            log.print(repo_filepath, num_indents=num_indents+2)
            log.print('done', num_indents=num_indents)
            return df
        else:
            log.print('failed to find SIC codes locally at:',
                num_indents=num_indents+1)
            log.print(repo_filepath, num_indents=num_indents+2)

    sec_url  = 'https://www.sec.gov/corpfin/division-of-corporation-finance-standard-industrial-classification-sic-code-list'
    osha_url = 'https://www.osha.gov/data/sic-manual'
    division_href       = '/data/sic-manual/division'
    major_group_href    = '/data/sic-manual/major-group-'
    industry_group_href = '/sic-manual/'

    log.print('downloading codes from OSHA source:', num_indents=num_indents+1)
    log.print(osha_url,   num_indents=num_indents+2, new_line_end=True)
    df = pd.DataFrame(columns=[
        'division_code',       'division_name',
        'major_group_code',    'major_group_name',
        'industry_group_code', 'industry_group_name'])
    response = requests.get(osha_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # with open('standard_industrial_codes.txt', 'w') as f:
    #     f.write(soup.prettify())
    for division_html in soup.find_all('a', href=lambda href : \
        href != None and href.startswith(division_href)):

        division_code = division_html.text.split(':')[0][-1]
        division_name = division_html.text.split(':')[1][1:]
        log.print('Division %s: %s' % (division_code, division_name),
            num_indents=num_indents+2)

        division_url = osha_url + '/' + division_html['href'].split('/')[-1]
        response = requests.get(division_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for major_group_html in soup.find_all('a', href=lambda href : \
            href != None and \
            href.startswith(major_group_href)):

            major_group_code = major_group_html.text.split(' ')[2][:-1]
            major_group_name = major_group_html.text.split(':')[1][1:]
            if verbose:
                log.print('Major Group %s: %s' % (
                    major_group_code, major_group_name),
                    num_indents=num_indents+3)

            major_group_url  = osha_url + '/major-group-' + major_group_code
            response = requests.get(major_group_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for industry_group_html in soup.find_all('a', href=lambda href : \
                href != None and \
                href.startswith(industry_group_href)):

                industry_group_code = industry_group_html['title'].split(' ')[0]
                industry_group_name = ' '.join(industry_group_html['title'].split(' ')[1:])
                if verbose:
                    log.print('Industry Group %s: %s' % (
                        industry_group_code, industry_group_name),
                        num_indents=num_indents+4)

                df = df.append(pd.DataFrame({
                    'division_code'       : [division_code],       'division_name'       : [division_name],
                    'major_group_code'    : [major_group_code],    'major_group_name'    : [major_group_name],
                    'industry_group_code' : [industry_group_code], 'industry_group_name' : [industry_group_name]
                }))

    log.print('downloading codes from SEC source:',
        num_indents=num_indents+1, new_line_start=True)
    log.print(sec_url, num_indents=num_indents+2, new_line_end=True)
    sec_df = pd.read_html(sec_url)[0]
    sec_df['SIC Code'] = sec_df['SIC Code'].apply(lambda sic : str(sic).rjust(4, '0'))
    undefined_sic_codes = sec_df[~sec_df['SIC Code'].isin(df['industry_group_code'].tolist())]
    undefined_sic_codes.reset_index(drop=True, inplace=True)
    log.print('appending %d code(s) that are in the SEC source but not the OSHA source' % \
        undefined_sic_codes.shape[0], num_indents=num_indents+2)
    for i, row in undefined_sic_codes.iterrows():
        sic                 = row['SIC Code']
        major_group_code    = sic[:2]
        df_row              = df[df['major_group_code'] == major_group_code].iloc[0]
        major_group_name    = df_row['major_group_name']
        division_code       = df_row['division_code']
        division_name       = df_row['division_name']
        industry_group_name = row['Industry Title']
        if verbose:
            log.print(
                'undefined SIC code %d of %d: %s%s' % (
                    i+1, undefined_sic_codes.shape[0],
                    ' ' * (len(str(undefined_sic_codes.shape[0])) - len(str(i+1))), sic),
                num_indents=num_indents+3)
            log.print('division_code ............ %s' % division_code,       num_indents=num_indents+4)
            log.print('division_name ............ %s' % division_name,       num_indents=num_indents+4)
            log.print('major_group_code ......... %s' % major_group_code,    num_indents=num_indents+4)
            log.print('major_group_name ......... %s' % major_group_name,    num_indents=num_indents+4)
            log.print('industry_group_code ...... %s' % industry_group_code, num_indents=num_indents+4)
            log.print('industry_group_name ...... %s' % industry_group_name, num_indents=num_indents+4)
        df = df.append(pd.DataFrame({
            'division_code'       : [division_code],       'division_name'       : [division_name],
            'major_group_code'    : [major_group_code],    'major_group_name'    : [major_group_name],
            'industry_group_code' : [sic],                 'industry_group_name' : [industry_group_name]
        }))

    df.sort_values(by=['division_code', 'major_group_code', 'industry_group_code'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    # log.print(df.to_string(), num_indents=num_indents+1)

    df.astype(str)
    df.to_csv(SIC_CODES_FILEPATH)
    log.print('done', num_indents=num_indents)
    return df
def get_state_and_country_codes(
    download=False,
    verbose=False,
    num_indents=0,
    new_line_start=True):

    log.print('getting latest state and country codes',
        num_indents=num_indents, new_line_start=new_line_start)

    # get codes from local csv file
    if not download:
        try:
            df = pd.read_csv(COUNTRY_CODES_FILEPATH, index_col=0, dtype=str)
        except:
            df = pd.DataFrame()
        repo_filepath = COUNTRY_CODES_FILEPATH[COUNTRY_CODES_FILEPATH.index('value-investing-app'):]
        if df.shape[0] > 0:
            log.print('found state and country codes locally at:',
                num_indents=num_indents+1)
            log.print(repo_filepath, num_indents=num_indents+2)
            log.print('done', num_indents=num_indents)
            return df
        else:
            log.print('failed to find state and country codes locally at',
                num_indents=num_indents+1)
            log.print(repo_filepath, num_indents=num_indents+2)

    # download the codes from the SEC website each time this program is run
    # because we want to know if they've changed it
    url = 'https://www.sec.gov/edgar/searchedgar/edgarstatecodes.htm'
    log.print('source: %s' % url, num_indents=num_indents+1)
    df = pd.DataFrame(columns=['code', 'country', 'state'])
    current_country = 'UNITED STATES'
    for i, row in pd.read_html(url)[0].iterrows():
        code = row['Code']['States']
        name = row['State or Country Name']['States']
        if code == 'Canadian Provinces' and name == 'Canadian Provinces':
            current_country = 'CANADA'
            continue
        elif code == 'Other Countries' and name == 'Other Countries':
            current_country = None
            continue
        if current_country == 'CANADA':
            name = name.split(',')[0]
        df = df.append(pd.DataFrame({
            'code'    : [code],
            'country' : [current_country if current_country != None else name],
            'state'   : [name if current_country != None else None]
        }))
    df.reset_index(drop=True, inplace=True)
    df.astype(str)
    df.to_csv(COUNTRY_CODES_FILEPATH)
    if verbose:
        log.print(df.to_string(), num_indents=num_indents+1)
    log.print('done', num_indents=num_indents)
    return df
def get_ticker_list_from_sec(
    download=False,
    num_indents=0,
    new_line_start=True):

    log.print('getting ticker list from SEC',
        num_indents=num_indents,
        new_line_start=new_line_start)

    # get tickers from local csv file
    if not download:
        try:
            df = pd.read_csv(TICKER_CODES_FILEPATH, index_col=0, dtype=str)
        except:
            df = pd.DataFrame()
        repo_filepath = TICKER_CODES_FILEPATH[TICKER_CODES_FILEPATH.index('value-investing-app'):]
        if df.shape[0] > 0:
            log.print('found ticker list locally at:',
                num_indents=num_indents+1)
            log.print(repo_filepath, num_indents=num_indents+2)
            log.print('done', num_indents=num_indents)
            return df
        else:
            log.print('failed to find tickers locally at:',
                num_indents=num_indents+1)
            log.print(repo_filepath, num_indents=num_indents+2)

    log.print('parsing ticker list from SEC',
        num_indents=num_indents+1)
    log.print('URL: %s' % TICKER_URL, num_indents=num_indents+2)
    response = requests.get(TICKER_URL, headers={'User-Agent' : USER_AGENT})
    data = json.loads(response.text)
    df = pd.DataFrame(data['data'], columns=data['fields'], dtype=str)
    df.to_csv(TICKER_CODES_FILEPATH)
    log.print('done, parsed %d tickers' % df.shape[0], num_indents=num_indents)
    return df
def get_new_quarter_raw_data(
    quarter_list=[],
    download=False,
    verbose=False,
    num_indents=0,
    new_line_start=False):

    log.print('getting new quarter data',
        num_indents=num_indents, new_line_start=new_line_start)

    # get data from local csv files
    if not download:
        data_paths = [
            os.path.join(TMP_FILINGS_PATH, quarter) \
            for quarter in os.listdir(TMP_FILINGS_PATH)]
        if len(data_paths) == 0:
            log.print('no local data to parse', num_indents=num_indents+1)
            log.print('please use optional arg --download or -d', num_indents=num_indents+1)
            log.print('to download data from online', num_indents=num_indents+1)
            log.print('program terminated', num_indents=num_indents, new_line_end=True)
            sys.exit()
        data_paths.sort()
        log.print('found %d quarters locally' % len(data_paths), num_indents=num_indents+1)
        log.print('done', num_indents=num_indents)
        return data_paths

    # determine the quarters already downloaded
    with open(METADATA_FILEPATH, 'r') as f:
        metadata_dct = json.load(f)
    quarters_downloaded = metadata_dct['quarters_downloaded']
    log.print(
        '%d quarter(s) previously downloaded %s' % (
            len(quarters_downloaded),
            ('' if len(quarters_downloaded) == 0 else (
            'from %s to %s' % (
                quarters_downloaded[0],
                quarters_downloaded[-1])))),
        num_indents=num_indents+1)

    # determine if there's any new quarters released on the
    # SEC's Financial Statements Data Sets webpage
    last_downloaded_quarter, last_downloaded_year = \
        year_and_quarter_from_quarter_str(quarters_downloaded[-1]) \
        if len(quarters_downloaded) > 0 else (None, None)
    df = pd.read_html(FINANCIAL_STATEMENTS_DATA_SETS_URL)[0]
    df = df[df['File'] > 'File: %d Q%d' % (last_downloaded_year, last_downloaded_quarter)] \
        if last_downloaded_year != None else df
    df.sort_values(by=['File'], inplace=True)
    df.reset_index(inplace=True)

    # download the zip files of the new quarters and
    # extract their data to a temporary directory
    log.print('found %d new quarter(s) at: %s' % (
        df.shape[0], FINANCIAL_STATEMENTS_DATA_SETS_URL),
        num_indents=num_indents+1)
    if df.shape[0] == 0:
        log.print('nothing to do. program terminated', num_indents=num_indents, new_line_end=True)
        sys.exit()
    data_paths = []
    for i, row in df.iterrows():
        year    = row['File'].split(' ')[1]
        quarter = row['File'].split(' ')[2][1]
        qtr     = '%sq%s' % (year, quarter)
        if quarter_list != []:
            if qtr not in quarter_list:
                continue
        log.print('downloading quarter %d of %d: %s Q%s' % (i+1, df.shape[0], year, quarter),
            num_indents=num_indents+2, new_line_start=verbose)
        zip_file_url = FINANCIAL_STATEMENTS_DATA_SETS_BASE_DOWNLOAD_URL.format(
            year=year, quarter=quarter)
        extraction_dir = os.path.join(TMP_FILINGS_PATH, qtr)
        if verbose:
            log.print('from: %s' % zip_file_url, num_indents=num_indents+3)
            log.print('to:   %s' % extraction_dir, num_indents=num_indents+3)
        r = requests.get(zip_file_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(extraction_dir)
        data_paths.append(extraction_dir)
    log.print('done', num_indents=num_indents)
    return data_paths

def current_year_and_quarter():
    d = date.today()
    return year_and_quarter(d)
def year_and_quarter_from_date_string(date_str):
    # date_str must have format yyyy-mm-dd
    # https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat
    d = date.fromisoformat(date_str)
    return year_and_quarter(d)
def year_and_quarter(d):
    q = pd.Timestamp(d).quarter
    y = d.year
    return q, y
def year_and_quarter_from_quarter_str(quarter_str):
    q = int(quarter_str.split('-')[1][-1])
    y = int(quarter_str.split('-')[0])
    return q, y
def get_quarter_date_range(y, q):
    if q == '1': return '-'.join([y, '01', '01']), '-'.join([y, '03', '31'])
    if q == '2': return '-'.join([y, '04', '01']), '-'.join([y, '06', '30'])
    if q == '3': return '-'.join([y, '07', '01']), '-'.join([y, '09', '30'])
    if q == '4': return '-'.join([y, '10', '01']), '-'.join([y, '12', '31'])

class SubmissionParser:

    def __init__(self):
        pass

    def parse_submissions(
        self,
        path,
        ticker_list=[],
        replace=False,
        verbose=False,
        num_indents=0):

        num_df, sub_df = self.read_quarter_data(path)
        num_subs = sub_df.shape[0]
        if ticker_list != []:
            sub_df['ticker'] = sub_df['cik'].apply(lambda cik : self.parse_ticker(cik))
            sub_df = sub_df[sub_df['ticker'].isin(ticker_list)]
        log.print(', iterating over %d submission(s)' % num_subs)
        for i, sub in sub_df.iterrows():
            self.ticker = self.parse_ticker(sub['cik'])
            self.form_type = sub['form']
            self.sub_qtr_enddate = sub['period']
            self.sub_nums = num_df[num_df['adsh'] == sub['adsh']]#.copy()
            if self.form_type == '10-Q': self.num_qtrs = 1
            if self.form_type == '10-K': self.num_qtrs = 4

            log.print('submission %d of %d:' % (i+1, num_subs),
                num_indents=num_indents, new_line_start=verbose)
            log.print('form type ... %s' % self.form_type, num_indents=num_indents+1)
            log.print('ticker ...... %s' % self.ticker,    num_indents=num_indents+1)
            log.print('cik ......... %s' % sub['cik'],     num_indents=num_indents+1)

            data = {
                'info'         : {
                    'industry_classification' : {}
                },
                'fundamentals' : {}
            }
            data = self.get_data_from_yahoo_finance(
                        data,
                        verbose=verbose,
                        num_indents=num_indents+1,
                        new_line_start=verbose)
            data = self.get_data_from_sec_financial_statements_data_sets(
                        data,
                        sub,
                        verbose=verbose,
                        num_indents=num_indents+1,
                        new_line_start=verbose)
            if verbose:
                self.print_data(
                    data,
                    num_indents=num_indents+1,
                    new_line_start=True)

            new_values_found = self.save_data(
                data,
                replace=replace,
                verbose=True,#verbose,
                num_indents=num_indents+1,
                new_line_start=verbose)

            self.update_data_quality_report(
                data,
                new_values_found,
                num_indents=num_indents+1,
                new_line_start=verbose)
            # input()
            time.sleep(5)
    def read_quarter_data(
        self,
        path):

        num_df = pd.read_csv(
            os.path.join(path, 'num.txt'),
            sep='\t',
            dtype=str)
        sub_df = pd.read_csv(
            os.path.join(path, 'sub.txt'),
            sep='\t',
            dtype=str)
        sub_df = sub_df[sub_df['form'].isin(VALID_FORM_TYPES)]
        # sort by 'form' descending to parse 10-Qs before 10-Ks
        # to increase the odds of 10-Ks having the data they need
        sub_df.sort_values(by=['form'], ascending=False, inplace=True)
        sub_df.reset_index(drop=True, inplace=True)
        return num_df, sub_df
    def get_data_from_yahoo_finance(
        self,
        data,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        log.print('parsing yahoo finance data%s' % \
            (':' if verbose else ' ... '),
            num_indents=num_indents,
            new_line_start=new_line_start,
            end=('\n' if verbose else ''))
        yf_company = yf.Ticker(self.ticker) if self.ticker != None else None
        yf_info = yf_company.info if yf_company != None else None
        if yf_info != None:
            data['info']['asset_type']                      = self.parse_yf_key(yf_info, 'quoteType')
            data['info']['description']                     = self.parse_yf_key(yf_info, 'longBusinessSummary')
            data['info']['name']                            = self.parse_yf_key(yf_info, 'longName')
            data['info']['website']                         = self.parse_yf_key(yf_info, 'website')
            data['info']['industry_classification']['gics'] = self.parse_gics(yf_info)
            data['info']['ex_dividend_date']                = self.parse_yf_ex_dividend_date(yf_info)
            data['dividend_per_share_history']              = self.parse_yf_dividend_per_share_history(
                                                                yf_company, num_indents=num_indents+1)
            data['stock_split_history']                     = self.parse_yf_stock_split_history(
                                                                yf_company, num_indents=num_indents+1)
            data['daily_price_data']                        = self.parse_yf_daily_price_data(
                                                                yf_company, num_indents=num_indents+1)
        else:
            keys = ['asset_type', 'description', 'name', 'website', 'ex_dividend_date']
            for k in keys: data['info'][k] = None
            data['info']['industry_classification']['gics'] = {
                'sector'   : None,
                'industry' : None
            }
            data['daily_price_data']           = None
            data['dividend_per_share_history'] = None
            data['stock_split_history']        = None
        log.print('done', num_indents=(num_indents if verbose else 0))
        return data
    def get_data_from_sec_financial_statements_data_sets(
        self,
        data,
        sub,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        log.print('parsing SEC Financial Statements Data Sets data%s' % \
            (':' if verbose else ' ... '),
            num_indents=num_indents,
            new_line_start=new_line_start,
            end=('\n' if verbose else ''))
        data['info']['cik']                            = sub['cik']
        data['info']['ticker']                         = self.ticker
        data['info']['country']                        = self.parse_country(sub)
        data['info']['industry_classification']['sic'] = self.parse_sic(sub)
        data['info']['name']                           = data['info']['name'] \
                                                            if data['info']['name'] != None \
                                                            else sub['name']
        data['fundamentals']['sub_qtr_enddate'] = '-'.join([
            self.sub_qtr_enddate[0:4],
            self.sub_qtr_enddate[4:6],
            self.sub_qtr_enddate[6:8]])
        data['fundamentals']['quarter'], data['fundamentals']['year'] = self.parse_year_and_quarter(data['fundamentals']['sub_qtr_enddate'])
        data['fundamentals']['shares_outstanding']                    = self.parse_value_with_ddate('shares_outstanding', num_qtrs=self.num_qtrs)
        data['fundamentals']['total_assets']                          = self.parse_value_with_ddate('total_assets')
        data['fundamentals']['total_liabilities']                     = self.parse_total_liabilities()
        data['fundamentals']['total_revenue']                         = self.parse_total_revenue(data)
        data['fundamentals']['total_expenses']                        = self.parse_total_expenses(data)
        data['fundamentals']['net_income']                            = self.parse_net_income(data)
        data['fundamentals']['earnings_per_share']                    = self.parse_earnings_per_share(data)
        data['fundamentals']['dividends_paid']                        = self.parse_dividends_paid(data)
        data['fundamentals']['sec_urls']                              = self.get_sec_urls(sub, verbose=False, num_indents=num_indents)
        log.print('done', num_indents=(num_indents if verbose else 0))
        return data
    def print_data(
        self,
        data,
        num_indents=0,
        new_line_start=False):

        log.print('data:', num_indents=num_indents, new_line_start=new_line_start)
        for k, v in data.items():
            log.print(k, num_indents=num_indents+1, new_line_start=True)
            if isinstance(v, dict):
                log.print_dct(v, truncate_str=100, num_indents=num_indents+2)
            elif isinstance(v, pd.DataFrame):
                log.print(v.to_string(max_rows=6), num_indents=num_indents+2)
            elif v == None:
                log.print('None', num_indents=num_indents+2)

    def get_sec_urls(
        self,
        sub,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        all_files_url = ALL_FILES_BASE_URL.format(cik=sub['cik'], adsh=sub['adsh'].replace('-', ''))
        filing_details_url = all_files_url + sub['adsh'] + '-index.html'
        response = requests.get(filing_details_url, headers={'User-Agent' : USER_AGENT})
        document_format_files_df, data_files_df = tuple(pd.read_html(response.text))

        # get filing's XML url
        try:
            data_files_df = pd.read_html(response.text)[1]
            xml_path = data_files_df[data_files_df['Description'].isin([
                'XBRL INSTANCE FILE',
                'XBRL INSTANCE DOCUMENT',
                'EXTRACTED XBRL INSTANCE DOCUMENT'])]['Document'].iloc[0]
            xml_url = all_files_url + xml_path
        except:
            xml_url = 'FAILED'

        # get filing's HTML url
        try:
            document_format_files_df = pd.read_html(response.text)[0]
            html_path = document_format_files_df[document_format_files_df['Type'
                ].isin(VALID_FORM_TYPES)]['Document'].iloc[0].split(' ')[0]
            tagged_base_url = '/'.join([
                '/'.join(all_files_url.split('/')[:3]),
                'ix?doc=',
                '/'.join(all_files_url.split('/')[3:])])
            html_url = tagged_base_url + html_path
        except:
            html_url = 'FAILED'

        # get filing's TXT url
        try:
            document_format_files_df = pd.read_html(response.text)[0]
            txt_path = document_format_files_df[document_format_files_df['Description'
                ] == 'Complete submission text file']['Document'].iloc[0]
            txt_url = all_files_url + txt_path
        except:
            txt_url = 'FAILED'

        sec_urls = {
            'all_files'      : all_files_url,
            'filing_details' : filing_details_url,
            'XML'            : xml_url,
            'HTML'           : html_url,
            'TXT'            : txt_url
        }
        if verbose:
            max_dots = max(map(lambda name : len(name), sec_urls.keys()))
            log.print('SEC URLs:',
                num_indents=num_indents,
                new_line_start=new_line_start)
            for name, url in sec_urls.items():
                dots = '.'*(max_dots - len(name)) + '...'
                log.print('%s %s %s' % (name, dots, url), num_indents=num_indents+1)
        return sec_urls
    def parse_ticker(
        self,
        cik):
        try:
            ticker = ticker_df[ticker_df['cik'] == cik]['ticker'].iloc[0]
        except:
            ticker = None
        return ticker
    def parse_yf_ex_dividend_date(
        self,
        yf_info):
        ex_dividend_date = self.parse_yf_key(yf_info, 'exDividendDate')
        if ex_dividend_date != None:
            return datetime.utcfromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
    def parse_yf_dividend_per_share_history(
        self,
        yf_company,
        num_indents=0,
        new_line_start=False):
        while True:
            try:
                df = yf_company.dividends
                break
            except ConnectionResetError as e:
                log.print('ConnectionResetError', num_indents=num_indents)
                time.sleep(60)
        return self.parse_yf_pandas(df)
    def parse_yf_stock_split_history(
        self,
        yf_company,
        num_indents=0,
        new_line_start=False):
        while True:
            try:
                df = yf_company.splits
                break
            except ConnectionResetError as e:
                log.print('ConnectionResetError', num_indents=num_indents)
                time.sleep(60)
        return self.parse_yf_pandas(df, num_decimals=5)
    def parse_yf_daily_price_data(
        self,
        yf_company,
        num_indents=0,
        new_line_start=False):
        while True:
            try:
                df = yf_company.history(period='max')
                break
            except ConnectionResetError as e:
                log.print('ConnectionResetError', num_indents=num_indents)
                time.sleep(60)
        return self.parse_yf_pandas(
            df, num_decimals=2,
            columns=['Close', 'Volume'])
    def parse_yf_key(
        self,
        yf_info,
        key):
        return yf_info[key] \
            if yf_info != None and key in yf_info.keys() \
            else None
    def parse_yf_pandas(
        self,
        x,
        num_decimals=None,
        columns=None):

        def index_to_str(i):
            return str(i).split(' ')[0]

        if isinstance(x, pd.Series):
            x = x.to_frame()
        if isinstance(x, pd.DataFrame):
            if columns != None:
                x = x[columns]
            if num_decimals != None:
                x = x.round(num_decimals)
            x.index = x.index.map(index_to_str)
            return x
        else:
            return None
    def parse_country(
        self,
        sub,
        num_indents=0,
        new_line_start=False):

        code = sub['countryinc']
        if code in ['US', 'CA']: code = sub['stprinc']
        country = country_codes_df[country_codes_df['code'] == \
            code]['country']
        return country.iloc[0] if not country.empty else None
    def parse_sic(
        self,
        sub):

        try:
            sic = str(int(float(sub['sic'])))
            row = sic_codes_df[sic_codes_df['industry_group_code'] == sic]
            division       = row['division_name'].iloc[0]
            major_group    = row['major_group_name'].iloc[0]
            industry_group = row['industry_group_name'].iloc[0]            
        except:
            sic            = None
            division       = None
            major_group    = None
            industry_group = None
        return {
            'sic'             : sic,
            'division'        : division,
            'major_group'     : major_group,
            'industry_group'  : industry_group
        }
    def parse_gics(
        self,
        yf_info):

        '''
            it seems yahoo finance uses the GICS classification system:
            https://www.yahoo.com/entertainment/amy-schumer-swimsuit-liposuction-164713278.html?utm_source=spotim&utm_medium=spotim_recirculation
            https://www.yahoo.com/now/sector-vs-industry-stock-market-154630803.html
        '''
        return {
            'sector'   : self.parse_yf_key(yf_info, 'sector'),
            'industry' : self.parse_yf_key(yf_info, 'industry')
        }
    def parse_year_and_quarter(
        self,
        date_str):
        q, y = year_and_quarter_from_date_string(date_str)
        return str(q), str(y)
    def parse_total_liabilities(
        self,
        num_indents=0,
        new_line_start=False):

        ''' note, some 10-Qs doesn't state total liabilities
                example:
                    https://www.sec.gov/Archives/edgar/data/1000229/0000950170-21-002488-index.html

            but
            total_liabilities = total_liabilities_and_equity - total_equity
            this has been verified, it will be equal to the sum of:
                TOTAL CURRENT LIABILITIES
                LONG-TERM DEBT, net
                LONG-TERM OPERATING LEASE LIABILITIES
                DEFERRED COMPENSATION
                DEFERRED TAX LIABILITIES, net
                OTHER LONG-TERM LIABILITIES
        '''
        total_liabilities = self.parse_value_with_ddate('total_liabilities', ret='int')
        if total_liabilities == None:
            total_liabilities_and_equity = self.parse_value_with_ddate(
                'total_liabilities_and_equity', ret='int')
            total_equity = self.parse_value_with_ddate(
                'total_equity', ret='int')
            if total_liabilities_and_equity != None and total_equity != None:
                total_liabilities = total_liabilities_and_equity - total_equity
        return str(total_liabilities) if total_liabilities != None else None
    def parse_total_revenue(
        self,
        data):

        if self.form_type == '10-Q':
            return self.parse_value_with_ddate('total_revenue', num_qtrs=1)
        elif self.form_type == '10-K':
            return self.calculate_10K_value_for_just_this_quarter(
                'total_revenue', data, 'fundamentals.csv')
    def parse_total_expenses(
        self,
        data):

        if self.form_type == '10-Q':
            return self.parse_value_with_ddate('total_expenses', num_qtrs=1)
        elif self.form_type == '10-K':
            return self.calculate_10K_value_for_just_this_quarter(
                'total_expenses', data, 'fundamentals.csv')
    def parse_net_income(
        self,
        data):

        if self.form_type == '10-Q':
            return self.parse_value_with_ddate('net_income', num_qtrs=1)
        elif self.form_type == '10-K':
            return self.calculate_10K_value_for_just_this_quarter(
                'net_income', data, 'fundamentals.csv')
    def parse_earnings_per_share(
        self,
        data):

        if self.form_type == '10-Q':
            return self.parse_value_with_ddate('earnings_per_share', num_qtrs=1)
        elif self.form_type == '10-K':
            return self.calculate_10K_value_for_just_this_quarter(
                'earnings_per_share', data, 'fundamentals.csv')
    def parse_dividends_paid(
        self,
        data):

        if self.form_type == '10-Q':
            dividends_paid = self.parse_value_with_ddate('dividends_paid', num_qtrs=1)
        elif self.form_type == '10-K':
            dividends_paid = self.calculate_10K_value_for_just_this_quarter(
                'dividends_paid', data, 'fundamentals.csv')

        # assume a dividend of $0 if none could be found
        return dividends_paid if dividends_paid != None else 0
    def calculate_10K_value_for_just_this_quarter(
        self,
        value_key,
        data,
        table_name,
        num_indents=0,
        new_line_start=False):

        value = self.parse_value_with_ddate(value_key, num_qtrs=4, ret='int')

        # value_previous_quarters = list of 3 values from previous quarters
        # or None if any of the 3 values can't be found in the database
        def get_previous_10Q_values(
            value_key,
            year,
            quarter,
            cik,
            table_name,
            num_indents=0,
            new_line_start=False):

            previous_quarters = []
            if year == None or quarter == None:
                return None
            y, q = int(year), int(quarter)
            for _ in [1, 2, 3]:
                q -= 1
                if q < 1:
                    q = 4
                    y -= 1
                previous_quarters.append((y, q))
            # for t in previous_quarters: print(t)

            # if any of the previous quarter's value is None in the database then return None
            filepath = os.path.join(DATA_STOCKS_PATH, str(cik), table_name)
            try:
                df = pd.read_csv(filepath)
            except:
                return None
            previous_values = []
            for year, quarter in previous_quarters:
                df2 = df[(df['year'] == year) & (df['quarter'] == quarter)]
                if df2.empty:
                    return None
                value = df2[value_key].iloc[0]
                if not (isinstance(value, int) or isinstance(value, float)):
                    return None
                previous_values.append(value)
            return previous_values
        value_previous_quarters = get_previous_10Q_values(
            value_key,
            data['fundamentals']['year'],
            data['fundamentals']['quarter'],
            data['info']['cik'],
            table_name,
            num_indents=num_indents)
        if value == None or value_previous_quarters == None:
            return None
        value -= sum(value_previous_quarters)
        return value
    def parse_value_with_ddate(
        self,
        value_key,
        num_qtrs=None,
        round_down=True,
        ret='str'):
    
        df = self.sub_nums[self.sub_nums['tag'].isin(DATA_TAGS[value_key])]
        df = df[df['coreg'].isna()]
        df = df[df['ddate'] == self.sub_qtr_enddate]
        df = df.dropna(subset=['value'])
        if num_qtrs != None:
            df = df[df['qtrs'] == num_qtrs]
        if df.shape[0] == 0:
            return None
        elif df.shape[0] == 1:
            value = df.iloc[0]['value']
        else:
            found = False

            # if all values are the same
            if df['value'].eq(df['value'].iloc[0]).all():
                value = df.iloc[0]['value']
                found = True

            # prioritize items by the tag order in the DATA_TAGS list
            for tag in DATA_TAGS[value_key]:
                if tag in df['tag'].tolist():
                    df2 = df[df['tag'] == tag]
                    if df2.shape[0] == 1 or \
                        df2['value'].eq(df2['value'].iloc[0]).all():
                        value = df2.iloc[0]['value']
                        found = True
                        break

            if not found:
                print('%s length > 1' % value_key)
                print(df)
                sys.exit()
        value = int(float(value)) if round_down else value
        value = int(float(value)) if ret == 'int' else value
        value = str(value) if ret == 'str' else value
        return value

    def save_data(
        self,
        data,
        replace=False,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        # deepcopy data to reuse it in data quality report and
        # create company CIK directory if it doesn't already exist
        data = copy.deepcopy(data)
        cik_path = os.path.join(DATA_STOCKS_PATH, str(data['info']['cik']))
        if not os.path.exists(cik_path):
            os.mkdir(cik_path)

        # save data
        log.print(('saved data to:' if verbose else 'saving data ...'),
            num_indents=num_indents,
            new_line_start=new_line_start,
            end=('\n' if verbose else ''))
        new_values_found = {}
        new_values_found = self.save_info(
            new_values_found, cik_path, data,
            replace=replace, verbose=True, num_indents=num_indents+1)
        new_values_found = self.save_fundamentals(
            new_values_found, cik_path, data,
            replace=replace, verbose=True, num_indents=num_indents+1)
        new_values_found = self.save_df(
            new_values_found, cik_path, 'dividend_per_share_history', data,
            replace=replace, verbose=True, num_indents=num_indents+1)
        new_values_found = self.save_df(
            new_values_found, cik_path, 'stock_split_history', data,
            replace=replace, verbose=True, num_indents=num_indents+1)
        new_values_found = self.save_df(
            new_values_found, cik_path, 'daily_price_data', data,
            replace=replace, verbose=True, num_indents=num_indents+1)

        if not verbose:
            log.print('done')
        return new_values_found
    def save_info(
        self,
        new_values_found,
        cik_path,
        data,
        replace=False,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        def empty_info(d):
            e = {}
            for k, v in d.items():
                e[k] = empty_info(v) if isinstance(v, dict) else None
            return e
        def flattened_to_nested_key_mapping(d):
            # m = pd.json_normalize(d, sep='_').to_dict(orient='records')[0]
            m = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    for k2, v2 in flattened_to_nested_key_mapping(v).items():
                        m[k+'_'+k2] = [k] + v2
                else:
                    m[k] = [k]
            return m
        def set_dct_key_path(d, key_list, v):
            d[key_list[0]] = v if len(key_list) == 1 else \
                set_dct_key_path(d[key_list[0]], key_list[1:], v)
            return d

        filepath = os.path.join(cik_path, 'info.json')
        repo_filepath = filepath[filepath.index('value-investing-app'):]
        log.print(repo_filepath, num_indents=num_indents)
        empty_info_template = empty_info(data['info'])
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump(empty_info_template, f, indent=4, sort_keys=True)
        with open(filepath, 'r') as f:
            old_values = json.load(f)
        key_map        = flattened_to_nested_key_mapping(data['info'])
        values_saved   = copy.deepcopy(old_values)
        new_values_found.update({k2 : 0 for k2 in key_map.keys()})
        if verbose:
            log.print('old_values', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(old_values, sort_keys=True, num_indents=num_indents+2)
            log.print('new_values', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(data['info'], sort_keys=True, num_indents=num_indents+2)
            log.print('key_map', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(key_map, sort_keys=True, num_indents=num_indents+2)
            log.print('empty_info_template', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(empty_info_template, sort_keys=True, num_indents=num_indents+2)
            log.print('new_values_found BEFORE update', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(new_values_found, sort_keys=True, num_indents=num_indents+2)
        for k_flat, k_list in key_map.items():
            old_metric, new_metric = old_values, data['info']
            for k2 in k_list:
                old_metric, new_metric = old_metric[k2], new_metric[k2]
            if (old_metric == None and new_metric != None) or \
                (old_metric != None and new_metric != None and replace):
                values_saved = set_dct_key_path(values_saved, k_list, new_metric)
            if (old_metric == None and new_metric != None):
                new_values_found[k_flat] = 1
        if verbose:
            log.print('new_values_found AFTER update', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(new_values_found, sort_keys=True, num_indents=num_indents+2)
            log.print('values_saved', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(values_saved, sort_keys=True, num_indents=num_indents+2)
        with open(filepath, 'w') as f:
            json.dump(values_saved, f, indent=4, sort_keys=True)
        return new_values_found
    def save_fundamentals(
        self,
        new_values_found,
        cik_path,
        data,
        replace=False,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        # get old fundamental data
        filepath = os.path.join(cik_path, 'fundamentals.csv')
        columns = DATA_COLUMNS['fundamentals']
        index_col = 'sub_qtr_enddate'
        repo_filepath = filepath[filepath.index('value-investing-app'):]
        log.print(repo_filepath, num_indents=num_indents)
        old_df = pd.read_csv(
                filepath,
                index_col=index_col,
                dtype=object) \
            if os.path.exists(filepath) \
            else pd.DataFrame(columns=columns)
        old_df.index = old_df.index.astype(object)
        old_df.index.name = index_col
        old_df.where(pd.notnull(old_df), other=None, inplace=True)
        if verbose:
            log.print('old_df', num_indents=num_indents+1, new_line_start=True)
            log.print(old_df.to_string(
                max_rows=6, max_cols=6, max_colwidth=20),
                num_indents=num_indents+2)

        # do nothing if no fundamental data was found
        if (not isinstance(data['fundamentals'], pd.DataFrame)) and \
            data['fundamentals'] == None:
            log.print('no updates to fundamentals.csv',
                num_indents=num_indents+1,
                new_line_start=True)
            new_values_found.update({c : 0 for c in columns})
            return new_values_found
        else:
            if verbose:
                log.print('new fundamentals dct', num_indents=num_indents+1, new_line_start=True)
                log.print_dct(data['fundamentals'], num_indents=num_indents+2)

        # convert new fundamentals from a dict into a dataframe
        # https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
        sub_qtr_enddate = data['fundamentals']['sub_qtr_enddate']
        del data['fundamentals']['sub_qtr_enddate']
        fundamentals_dct_flattened = pd.json_normalize(
            data['fundamentals'], sep='_').to_dict(orient='records')[0]
        data['fundamentals'] = pd.DataFrame(fundamentals_dct_flattened, index=[sub_qtr_enddate])
        data['fundamentals'].index.name = index_col
        if verbose:
            log.print('new fundamentals df',
                num_indents=num_indents+1,
                new_line_start=True)
            log.print(data['fundamentals'].to_string(
                max_rows=6, max_cols=6, max_colwidth=20),
                num_indents=num_indents+2)

        # just add it to the database and set all metrics to upgraded
        # if its a new sub_qtr_enddate, otherwise its not a new sub_qtr_enddate
        # so for each metric, only update its value in the database if:
        #     the old value is "None" and the new value isn't "None" or
        #     the old value isn't "None" and the new value isn't "None" and the --replace/-r argument is provided
        # and only update each metric's value in the quality report if:
        #     the old value is "None" and the new value isn't "None"
        if verbose:
            log.print('sub_qtr_enddate = %s' % sub_qtr_enddate,
                num_indents=num_indents+1, new_line_start=True)
        if sub_qtr_enddate not in old_df.index:
            if verbose:
                log.print('sub_qtr_enddate not in old_df, adding it, and sorting it by sub_qtr_enddate',
                    num_indents=num_indents+1)
            values_saved = old_df.append(data['fundamentals'])
            values_saved.sort_index(inplace=True)
            new_values_found.update({c : (1 if values_saved[c][sub_qtr_enddate] != None else 0) \
                for c in columns})
        else:
            if verbose:
                log.print('sub_qtr_enddate in old_df', num_indents=num_indents+1)
            values_saved = copy.deepcopy(old_df)
            for metric in columns:
                old_value = old_df.at[sub_qtr_enddate, metric]
                new_value = data['fundamentals'].at[sub_qtr_enddate, metric]
                if (old_value == None and new_value != None) or \
                    (old_value != None and new_value != None and replace):
                    values_saved.at[sub_qtr_enddate, metric] = new_value
                new_values_found[metric] = 1 \
                    if (old_value == None and new_value != None) \
                    else 0

        # save database to file and return new_values_found
        if verbose:
            log.print('new_values_found', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(new_values_found, num_indents=num_indents+2)
            log.print('values_saved', num_indents=num_indents+1, new_line_start=True)
            log.print(values_saved.to_string(
                max_rows=6, max_cols=6, max_colwidth=20),
                num_indents=num_indents+2)
        values_saved.to_csv(filepath)
        return new_values_found
    def save_df(
        self,
        new_values_found,
        cik_path,
        filename,
        data,
        replace=False,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        # get old dataframe
        filepath = os.path.join(cik_path, filename+'.csv')
        columns = DATA_COLUMNS[filename]
        index_col = 'Date'
        repo_filepath = filepath[filepath.index('value-investing-app'):]
        log.print(repo_filepath, num_indents=num_indents)
        old_df = pd.read_csv(
                filepath,
                index_col=index_col,
                dtype=object) \
            if os.path.exists(filepath) \
            else pd.DataFrame(columns=columns)
        old_df.index = old_df.index.astype(object)
        old_df.index.name = index_col
        old_df.where(pd.notnull(old_df), other=None, inplace=True) # replace Nan values with None
        if verbose:
            log.print('old_df', num_indents=num_indents+1, new_line_start=True)
            log.print(old_df.to_string(
                max_rows=6, max_cols=6, max_colwidth=20),
                num_indents=num_indents+2)

        # do nothing if no data was found
        if (not isinstance(data[filename], pd.DataFrame)) and \
            data[filename] == None:
            log.print('no updates to %s.csv' % filename,
                num_indents=num_indents+1,
                new_line_start=True)
            new_values_found.update({c : 0 for c in columns})
            return new_values_found
        else:
            if verbose:
                log.print('new dataframe',
                    num_indents=num_indents+1,
                    new_line_start=True)
                log.print(data[filename].to_string(
                    max_rows=6, max_cols=6, max_colwidth=20),
                    num_indents=num_indents+2)

        # append new data to old data,
        # if theres overlap between Dates then the "replace" arg will decide which to keep.
        # new_values_found is only 1 if the old data was empty and the new data is not, else 0
        values_saved = old_df.append(data[filename])
        values_saved = values_saved[~values_saved.index.duplicated(
            keep=('last' if replace else 'first'))]
        values_saved.sort_index(inplace=True)
        new_values_found[filename] = 1 \
            if old_df.empty and (not values_saved.empty) \
            else 0

        # save dataframe to file and return new_values_found
        if verbose:
            log.print('new_values_found', num_indents=num_indents+1, new_line_start=True)
            log.print_dct(new_values_found, num_indents=num_indents+2)
            log.print('values_saved', num_indents=num_indents+1, new_line_start=True)
            log.print(values_saved.to_string(
                max_rows=6, max_cols=6, max_colwidth=20),
                num_indents=num_indents+2)
        values_saved.to_csv(filepath)
        return new_values_found

    def update_data_quality_report(
        self,
        data,
        new_values_found,
        num_indents=0,
        new_line_start=False):

        log.print('updating data quality report:',
            num_indents=num_indents,
            new_line_start=new_line_start)
        self.update_price_data_stock_vs_day_report(data, new_values_found, verbose=True, num_indents=num_indents+1)
        new_submission_searched = self.update_stock_vs_quarter_report(data, new_values_found, verbose=True, num_indents=num_indents+1)
        self.update_metric_vs_quarter_report(data, new_values_found, new_submission_searched, verbose=True, num_indents=num_indents+1)
        self.update_stock_vs_metric_report(data, new_values_found, new_submission_searched, verbose=True, num_indents=num_indents+1)
    def update_price_data_stock_vs_day_report(
        self,
        data,
        new_values_found,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        log.print(
            ('updating price_data_stock_vs_day data:' if verbose else \
                'updating price_data_stock_vs_day data ... '),
            num_indents=num_indents,
            end=('\n' if verbose else ''))

        filepath = os.path.join(QUALITY_REPORT_PATH, 'price_data_stock_vs_day', 'price_data_coverage.csv')
        columns = ['start_date', 'end_date']
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(','.join(['cik']+columns)+'\n')
        df = pd.read_csv(filepath, index_col='cik')
        df.index = df.index.astype(str)
        if verbose:
            repo_filepath = filepath[filepath.index('value-investing-app'):]
            log.print('repo filepath: %s' % repo_filepath, num_indents=num_indents+1)

        # add stock if its not in the list
        stock_CIKs = df.index.values
        cik = str(data['info']['cik'])
        if cik in stock_CIKs:
            if verbose:
                log.print('stock with CIK=%s already exists in price_data_stock_vs_day/price_data_coverage.csv' % \
                    cik, num_indents=num_indents+1)
            old_df_filepath = os.path.join(DATA_STOCKS_PATH, cik, 'daily_price_data.csv')
            old_df = pd.read_csv(old_df_filepath, index_col='Date')
            new_stock_with_price_data = old_df.empty
        else:
            # apparently the df.insert() function can only insert columns, now rows:
            # https://stackoverflow.com/questions/24284342/insert-a-row-to-pandas-dataframe
            # so i used concat instead()
            df = pd.concat([
                df[df.index < cik],
                pd.DataFrame({c : np.nan for c in columns}, index=[cik]),
                df[df.index > cik]])
            new_stock_with_price_data = True
            if verbose:
                log.print('stock with CIK=%s didn\'t exist in price_data_stock_vs_day/price_data_coverage.csv, inserted an empty row at index=%d' % (
                    cik, df[df.index < cik].shape[0]), num_indents=num_indents+1)

        # update start/end_date and save the file
        start_date, end_date = (
            data['daily_price_data'].index.values[0],
            data['daily_price_data'].index.values[-1]) \
            if isinstance(data['daily_price_data'], pd.DataFrame) and \
                (not data['daily_price_data'].empty) \
            else (np.nan, np.nan)
        df.at[cik, 'start_date'], df.at[cik, 'end_date'] = start_date, end_date
        df.index.name = 'cik'
        df.to_csv(filepath)
        if verbose:
            log.print('start_date = %s' % start_date, num_indents=num_indents+2)
            log.print('end_date   = %s' % end_date, num_indents=num_indents+2)
        
        # update min/max_date and num_stocks_with_price_data in METADATA_FILEPATH
        with open(METADATA_FILEPATH, 'r') as f:
            metadata_dct = json.load(f)
        min_date = metadata_dct['price_data']['min_date']
        max_date = metadata_dct['price_data']['max_date']
        if        pd.isnull(start_date)  and      pd.isnull(min_date):  min_date = np.nan
        elif (not pd.isnull(start_date)) and      pd.isnull(min_date):  min_date = start_date
        elif      pd.isnull(start_date)  and (not pd.isnull(min_date)): min_date = min_date
        elif (not pd.isnull(start_date)) and (not pd.isnull(min_date)): min_date = min(start_date, min_date)
        if        pd.isnull(end_date)    and      pd.isnull(max_date):  max_date = np.nan
        elif (not pd.isnull(end_date))   and      pd.isnull(max_date):  max_date = end_date
        elif      pd.isnull(end_date)    and (not pd.isnull(max_date)): max_date = max_date
        elif (not pd.isnull(end_date))   and (not pd.isnull(max_date)): max_date = max(end_date, max_date)
        num_stocks_with_price_data = \
            metadata_dct['price_data']['num_stocks_with_price_data'] + \
                (1 if new_stock_with_price_data else 0)
        if verbose:
            if min_date != metadata_dct['price_data']['min_date']:
                log.print('updated min_date from %s to %s' % (
                    metadata_dct['price_data']['min_date'], min_date),
                    num_indents=num_indents+1)
            if max_date != metadata_dct['price_data']['max_date']:
                log.print('updated max_date from %s to %s' % (
                    metadata_dct['price_data']['max_date'], max_date),
                    num_indents=num_indents+1)
            if num_stocks_with_price_data != metadata_dct['price_data']['num_stocks_with_price_data']:
                log.print('updated num_stocks_with_price_data from %s to %s' % (
                    metadata_dct['price_data']['num_stocks_with_price_data'],
                    num_stocks_with_price_data),
                    num_indents=num_indents+1)
        metadata_dct['price_data'] = {
            'min_date' : min_date,
            'max_date' : max_date,
            'num_stocks_with_price_data' : num_stocks_with_price_data
        }
        with open(METADATA_FILEPATH, 'w') as f:
            json.dump(metadata_dct, f, indent=4, sort_keys=True)
        if not verbose:
            log.print('done')
    def update_stock_vs_quarter_report(
        self,
        data,
        new_values_found,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        log.print(
            ('updating stock_vs_quarter data:' if verbose else \
                'updating stock_vs_quarter data ... '),
            num_indents=num_indents,
            end=('\n' if verbose else ''))

        constant_new_values_found, variable_new_values_found = \
            self.split_constant_and_variable_metrics(new_values_found)

        # columns: CIK followed by the list of all quarters (with format: <year>q<quarter>, ex: 2021q3)
        # cells: if a cell is np.nan, then there was no submission for that stock during that quarter
        # else if a cell is 0, then 0 of the metrics were found for that stock during that quarter
        # the total number of metrics searched for is stored in METADATA_FILEPATH
        filepath = QUALITY_REPORT_PATHS.at['variable', 'stock_vs_quarter']
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write('cik\n')
        df = pd.read_csv(filepath, index_col='cik', dtype=object)
        df.index = df.index = df.index.astype(str)
        stock_CIKs = df.index.values
        quarters = df.columns.values
        cik = data['info']['cik']
        q = '%sq%s' % ( # q = new quarter to add
            data['fundamentals']['year'],
            data['fundamentals']['quarter'])
        if verbose:
            log.print('variable metrics:', num_indents=num_indents+1)
            repo_filepath = filepath[filepath.index('value-investing-app'):]
            log.print('repo filepath: %s' % repo_filepath, num_indents=num_indents+2)
            log.print('variable_new_values_found', num_indents=num_indents+2)
            log.print_dct(variable_new_values_found, num_indents=num_indents+3)
        if cik in stock_CIKs:
            if verbose:
                log.print('stock with CIK=%s already exists in stock_vs_quarter/variable_metrics.csv' % cik,
                    num_indents=num_indents+2)
            new_cik_found = False
        else:
            # apparently the df.insert() function can only insert columns, now rows:
            # https://stackoverflow.com/questions/24284342/insert-a-row-to-pandas-dataframe
            # so i used concat instead()
            df = pd.concat([
                df[df.index < cik],
                pd.DataFrame({qtr : np.nan for qtr in quarters}, index=[cik]),
                df[df.index > cik]])
            new_cik_found = True
            if verbose:
                log.print('stock with CIK=%s didn\'t exist in stock_vs_quarter/variable_metrics.csv, inserted an empty row at index=%d' % (
                    cik, df[df.index < cik].shape[0]),
                    num_indents=num_indents+2)

        # if quarter not in file, create an empty column for it in the right spot (quarters sorted numerically)
        # and add any in between quarters that might be missing
        df, new_quarters_found = self.insert_missing_quarters(
            df, q, quarters, 'stock_vs_quarter/variable_metrics.csv',
            verbose=verbose, num_indents=num_indents+2)

        # add the new values for the variable metrics
        v0 = df.at[cik, q]
        v0 = 0 if pd.isnull(v0) else int(v0)
        v = v0 + sum(variable_new_values_found.values())
        if verbose:
            log.print('old value at (CIK, quarter)=(%s, %s) equals %s' %(cik, q, v0),
                num_indents=num_indents+2)
            log.print('sum of variable_new_values_found equals %d' % \
                sum(variable_new_values_found.values()),
                num_indents=num_indents+2)
        df = df.astype(object)
        df.at[cik, q] = str(int(v))
        df.index.name = 'cik'
        df.to_csv(filepath)
        if verbose:
            log.print('new value at (CIK, quarter)=(%s, %s) equals %s' %(cik, q, v),
                num_indents=num_indents+2)

        # add the new values for the constant metrics
        filepath = QUALITY_REPORT_PATHS.at['constant', 'stock_vs_quarter']
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=4)
        with open(filepath, 'r') as f:
            dct = json.load(f)
        v0 = dct.get(cik, 0)
        dct[cik] = v0 + sum(constant_new_values_found.values())
        with open(filepath, 'w') as f:
            json.dump(dct, f, indent=4, sort_keys=True)
        if verbose:
            log.print('constant metrics', num_indents=num_indents+1)
            repo_filepath = filepath[filepath.index('value-investing-app'):]
            log.print('repo filepath: %s' % repo_filepath, num_indents=num_indents+2)
            log.print('constant_new_values_found', num_indents=num_indents+2)
            log.print_dct(constant_new_values_found, num_indents=num_indents+3)
            if cik in dct.keys():
                log.print('cik=%s in old dct equals %d' % (cik, v0), num_indents=num_indents+2)
            else:
                log.print('cik=%s not in old dct' % cik, num_indents=num_indents+2)
            log.print('sum of constant_new_values_found equals %d' % \
                sum(constant_new_values_found.values()), num_indents=num_indents+2)
            log.print('new value at cik=%s equals %d' % (cik, dct[cik]), num_indents=num_indents+2)

        # update metrics metadata
        with open(METADATA_FILEPATH, 'r') as f:
            metadata_dct = json.load(f)
        metrics_metadata = {
            'total'    : len(new_values_found.keys()),
            'variable' : len(variable_new_values_found.keys()),
            'constant' : len(constant_new_values_found.keys())
        }
        metadata_dct['number_of_metrics'] = metrics_metadata
        with open(METADATA_FILEPATH, 'w') as f:
            json.dump(metadata_dct, f, indent=4, sort_keys=True)
        if verbose:
            log.print('set \'number_of_metrics\' to:', num_indents=num_indents+1)
            log.print_dct(metrics_metadata, num_indents=num_indents+2)
            repo_metadata_filepath = METADATA_FILEPATH[METADATA_FILEPATH.index('value-investing-app'):]
            log.print('in file: %s' % repo_metadata_filepath, num_indents=num_indents+2)

        if not verbose:
            log.print('done')
        return new_cik_found and new_quarters_found
    def update_metric_vs_quarter_report(
        self,
        data,
        new_values_found,
        new_submission_searched,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        log.print(
            ('updating metric_vs_quarter data:' if verbose else \
                'updating metric_vs_quarter data ... '),
            num_indents=num_indents,
            end=('\n' if verbose else ''))

        constant_new_values_found, variable_new_values_found = \
            self.split_constant_and_variable_metrics(new_values_found)

        # for each metric for each quarter we only tried to find it for a variable number of stocks
        # so to save this data we are going to create 2 columns for each quarter:
        # the 1st will be the number of stocks we found this metric for this quarter
        #     with format: <year>q<quarter>-total_found, ex: "2021q3-total_found"
        # the 2nd will be the number of stocks we searched for this metric on for this quarter
        #     with format: <year>q<quarter>-total_searched, ex: "2021q3-total_searched"
        filepath = QUALITY_REPORT_PATHS.at['variable', 'metric_vs_quarter']
        all_metrics = list(variable_new_values_found.keys())
        all_metrics.sort()
        if not os.path.exists(filepath):
            df = pd.DataFrame(index=all_metrics)
            df.index.name = 'metric'
            df.to_csv(filepath)
        df = pd.read_csv(filepath, index_col='metric')
        quarters = list(set(map(lambda x : x.split('-')[0], df.columns.values)))
        q = '%sq%s' % ( # q = new quarter to add
            data['fundamentals']['year'],
            data['fundamentals']['quarter'])
        if verbose:
            log.print('variable metrics', num_indents=num_indents+1)
            repo_filepath = filepath[filepath.index('value-investing-app'):]
            log.print('repo filepath: %s' % repo_filepath, num_indents=num_indents+2)
            log.print('variable_new_values_found', num_indents=num_indents+2)
            log.print_dct(variable_new_values_found, num_indents=num_indents+3)

        # if quarter not in file, create an empty column for it in the right spot (quarters sorted numerically)
        # and add any in between quarters that might be missing
        df, _ = self.insert_missing_quarters(
            df, q, quarters, 'metric_vs_quarter/variable_metrics.csv', qtr_found_searched=True,
            verbose=verbose, num_indents=num_indents+1)

        # update the new variable values for each metric
        if verbose:
            log.print('new_submission_searched = %s, so +%d for each \"total_searched\"' % (
                    new_submission_searched,
                    (1 if new_submission_searched else 0)),
                num_indents=num_indents+2)
            log.print('updates for quarter %s: (total_found, total_searched)' % q,
                num_indents=num_indents+2)
        longest_key_len = max(map(lambda k : len(k), all_metrics))
        for m in all_metrics:
            tf_before, ts_before = df.at[m, q+'-total_found'], df.at[m, q+'-total_searched']
            df.at[m, q+'-total_found'] += variable_new_values_found[m]
            df.at[m, q+'-total_searched'] += 1 if new_submission_searched else 0
            tf_after, ts_after = df.at[m, q+'-total_found'], df.at[m, q+'-total_searched']
            if verbose:
                log.print('%s %s updated from (%d, %d) to (%d, %d)' % (
                    m, ' '*(longest_key_len - len(m)), tf_before, ts_before, tf_after, ts_after),
                    num_indents=num_indents+3)
        df.index.name = 'metric'
        df = df.astype(int)
        df.to_csv(filepath)


        # update the new values for the constant metrics
        filepath = QUALITY_REPORT_PATHS.at['constant', 'metric_vs_quarter']
        all_metrics = list(constant_new_values_found.keys())
        all_metrics.sort()
        empty_template = {
            'total_found'    : 0,
            'total_searched' : 0
        }
        if not os.path.exists(filepath):
            empty_dct = {m : empty_template for m in all_metrics}
            with open(filepath, 'w') as f:
                json.dump(empty_dct, f, indent=4)
        with open(filepath, 'r') as f:
            dct = json.load(f)
        if verbose:
            log.print('constant metrics', num_indents=num_indents+1)
            repo_filepath = filepath[filepath.index('value-investing-app'):]
            log.print('repo filepath: %s' % repo_filepath, num_indents=num_indents+2)
            log.print('new_submission_searched = %s, so +%d for each \"total_searched\"' % (
                new_submission_searched, (1 if new_submission_searched else 0)),
                num_indents=num_indents+2)
            log.print('constant_new_values_found', num_indents=num_indents+2)
            log.print_dct(constant_new_values_found, num_indents=num_indents+3)
            log.print('updates: (total_searched, total_found)',
                num_indents=num_indents+2)
        longest_key_len = max(map(lambda k : len(k), all_metrics))
        for m, v in constant_new_values_found.items():
            v0 = dct.get(m, empty_template)
            tf_before, ts_before = dct[m]['total_found'], dct[m]['total_searched']
            dct[m] = {
                'total_found'    : v0['total_found'] + constant_new_values_found[m],
                'total_searched' : v0['total_searched'] + (1 if new_submission_searched else 0)
            }
            tf_after, ts_after = dct[m]['total_found'], dct[m]['total_searched']
            if verbose:
                log.print('%s %s updated from (%d, %d) to (%d, %d)' % (
                    m, ' '*(longest_key_len - len(m)), tf_before, ts_before, tf_after, ts_after),
                    num_indents=num_indents+3)

        with open(filepath, 'w') as f:
            json.dump(dct, f, indent=4, sort_keys=True)

        if not verbose:
            log.print('done')
    def update_stock_vs_metric_report(
        self,
        data,
        new_values_found,
        new_submission_searched,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        log.print(
            ('updating stock_vs_metric data:' if verbose else \
                'updating stock_vs_metric data ... '),
            num_indents=num_indents,
            end=('\n' if verbose else ''))

        # for each metric for each stock we only tried to find it for a variable number of quarters
        # so to save this data we are going to create 2 columns for each metric:
        # the 1st will be the number of quarters we found this metric for this stock
        #     with format: <metric_name>-total_found, ex: "total_assets-total_found"
        # the 2nd will be the number of stocks we searched for this metric on for this quarter
        #     with format: <metric_name>-total_searched, ex: "total_assets-total_searched"
        filepath = os.path.join(QUALITY_REPORT_PATH, 'stock_vs_metric', 'all_metrics.csv')
        if verbose:
            repo_filepath = filepath[filepath.index('value-investing-app'):]
            log.print('repo filepath: %s' % repo_filepath, num_indents=num_indents+1)
        all_metrics = list(new_values_found.keys())
        all_metrics.sort()
        columns = []
        for m in all_metrics:
            columns += [m+'-total_found', m+'-total_searched']
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(','.join(['cik']+columns)+'\n')
        df = pd.read_csv(filepath, index_col='cik')
        df.index = df.index.astype(str)
        stock_CIKs = df.index.values
        cik = str(data['info']['cik'])
        if cik in stock_CIKs:
            if verbose:
                log.print('stock with CIK=%s already exists in stock_vs_metric/all_metrics.csv' % \
                    cik, num_indents=num_indents+1)
        else:
            # apparently the df.insert() function can only insert columns, now rows:
            # https://stackoverflow.com/questions/24284342/insert-a-row-to-pandas-dataframe
            # so i used concat instead()
            df = pd.concat([
                df[df.index < cik],
                pd.DataFrame({c : 0 for c in columns}, index=[cik]),
                df[df.index > cik]])
            if verbose:
                log.print('stock with CIK=%s didn\'t exist in stock_vs_metric/all_metrics.csv, inserted an empty row at index=%d' % (
                    cik, df[df.index < cik].shape[0]), num_indents=num_indents+1)

        # update new values for each metric
        if verbose:
            log.print('new_submission_searched = %s, so +%d for each \"total_searched\"' % (
                    new_submission_searched,
                    (1 if new_submission_searched else 0)),
                num_indents=num_indents+1)
            log.print('new_values_found', num_indents=num_indents+1)
            log.print_dct(new_values_found, num_indents=num_indents+2)
            log.print('updates for stock cik=%s: (total_found, total_searched)' % cik,
                num_indents=num_indents+1)
        longest_key_len = max(map(lambda m : len(m), all_metrics))
        for m in all_metrics:
            tf_before, ts_before = df.at[cik, m+'-total_found'], df.at[cik, m+'-total_searched']
            df.at[cik, m+'-total_found'] += new_values_found[m]
            df.at[cik, m+'-total_searched'] += 1
            tf_after, ts_after = df.at[cik, m+'-total_found'], df.at[cik, m+'-total_searched']
            if verbose:
                log.print('%s %s updated from (%d, %d) to (%d, %d)' % (
                    m, ' '*(longest_key_len - len(m)), tf_before, ts_before, tf_after, ts_after),
                    num_indents=num_indents+2)
        df.index.name = 'cik'
        df = df.astype(int)
        df.to_csv(filepath)

        if not verbose:
            log.print('done')
    def insert_missing_quarters(
        self,
        df, q, quarters, filepath,
        qtr_found_searched=False,
        verbose=False,
        num_indents=0,
        new_line_start=False):

        # if quarter not in file, create an empty column for it in the right spot (quarters sorted numerically)
        # and add any in between quarters that might be missing
        new_quarters_found = False
        if q not in quarters:
            new_quarters_found = True
            min_q = min(quarters) if len(quarters) > 0 else q
            max_q = max(quarters) if len(quarters) > 0 else q
            if q < min_q: min_q = q
            if q > max_q: max_q = q
            min_y, min_q = tuple(min_q.split('q'))
            max_y, max_q = tuple(max_q.split('q'))
            new_quarters = []
            for yr in range(int(min_y), int(max_y)+1):
                if yr == int(min_y) and yr == int(max_y):
                    start_q, end_q = int(min_q), int(max_q)
                elif yr == int(min_y):
                    start_q, end_q = int(min_q), 4
                elif yr == int(max_y):
                    start_q, end_q = 1, int(max_q)
                else:
                    start_q, end_q = 1, 4
                for qtr in range(start_q, end_q+1):
                    new_qtr = '%dq%d' % (yr, qtr)
                    if new_qtr not in quarters:
                        new_quarters.append(new_qtr)
            if qtr_found_searched:
                new_quarters_total_found    = list(map(lambda qtr : qtr+'-total_found',    new_quarters))
                new_quarters_total_searched = list(map(lambda qtr : qtr+'-total_searched', new_quarters))
                new_quarters_to_add = new_quarters_total_found + new_quarters_total_searched
            else:
                new_quarters_to_add = new_quarters
            empty_columns = pd.DataFrame({col : [0 if qtr_found_searched else np.nan]*df.shape[0] \
                for col in new_quarters_to_add}, index=df.index)
            df = pd.concat([df, empty_columns], axis=1)
            df = df.reindex(sorted(df.columns), axis=1)
            if verbose:
                log.print('inserted %d new quarter(s) into %s' % (
                    len(new_quarters), filepath), num_indents=num_indents)
                for qtr in new_quarters:
                    log.print(qtr, num_indents=num_indents+1)
        return df, new_quarters_found
    def split_constant_and_variable_metrics(
        self,
        new_values_found):

        constant_new_values_found = {k : v for k, v in new_values_found.items() if k not in DATA_COLUMNS['fundamentals']}
        variable_new_values_found = {k : v for k, v in new_values_found.items() if k in DATA_COLUMNS['fundamentals']}
        return constant_new_values_found, variable_new_values_found
    '''
    def num_metrics_aquired(
        self,
        data):
        
        value, all_metrics = 0, []
        metrics_aquired = {}
        for k, v in data['info'].items():
            if k == 'industry_classification':
                for classicification_name, classification_data in v.items():
                    for k2, v2 in classification_data.items():
                        metrics_aquired[classicification_name+'_'+k2] = 1 if v2 != None else 0
            else:
                metrics_aquired[k] = 1 if v != None else 0

        for k, v in data['fundamentals'].items():
            if k == 'sec_urls':
                for k2, v2 in v.items():
                    metrics_aquired[k+'_'+k2] = 1 if v2 != None else 0
            else:
                metrics_aquired[k] = 1 if v != None else 0
        df = data['daily_price_data']
        if (not isinstance(df, pd.DataFrame)) and df == None:
            metrics_aquired['daily_price_data'] = 0
        else:
            quarter_startdate, quarter_enddate = get_quarter_date_range(
                data['fundamentals']['year'], data['fundamentals']['quarter'])
            df = df.loc[quarter_startdate:quarter_enddate]
            metrics_aquired['daily_price_data'] = 0 if df.empty else 1
        metrics_aquired['stock_split_history'] = 0 if (not isinstance(data['stock_split_history'], pd.DataFrame)) and data['stock_split_history'] == None else 1
        metrics_aquired['dividend_per_share_history'] = 0 if (not isinstance(data['dividend_per_share_history'], pd.DataFrame)) and data['dividend_per_share_history'] == None else 1
        return metrics_aquired    
    def num_quarters_aquired(
        self, data):
        pass
    '''

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose',       action='store_true',   help='verbose logging')
    parser.add_argument('-c', '--clear',         action='store_true',   help='clear database before collecting new data')
    parser.add_argument('-l', '--lake',          action='store_true',   help='save the raw data downloaded to a data lake')
    parser.add_argument('-r', '--replace',       action='store_true',   help='replace database\'s old values with new values if new value != null')
    parser.add_argument('-d', '--download',      action='store_true',   help='download new raw data from online, else search for data locally (local search used for testing)')
    parser.add_argument('-q', '--quarter-list',  default=[], nargs='*', help='list of quarters to parse, if not specified all new quarters will be parsed, syntax example 2021q1')
    parser.add_argument('-t', '--ticker-list',   default=[], nargs='*', help='list of tickers to parse, if not specified all tickers will be parsed')
    args = parser.parse_args()
    for q in args.quarter_list:
        if not re.match(r'^[0-9]{4}q[1-4]$', q):
            log.print('invalid quarter in -q/--quarter-list arg: %s' % q)
            sys.exit()
    for t in args.ticker_list:
        if not re.match(r'^[a-zA-Z]+$', t):
            log.print('invalid ticker in -t/--ticker-list arg: %s' % t)
            sys.exit()

    # clear old database and init new files and directories
    if args.clear:
        clear_and_reset_database(
            num_indents=0,
            new_line_start=True)

    # get the raw new quarter(s) from the SEC website
    data_paths = get_new_quarter_raw_data(
        quarter_list=args.quarter_list,
        download=args.download,
        verbose=args.verbose,
        num_indents=0,
        new_line_start=True)
    if len(data_paths) > 0:

        # get industry and country codes, and tickers
        sic_codes_df     = get_standard_industrial_codes(download=args.download, verbose=False)#verbose=args.verbose)
        country_codes_df = get_state_and_country_codes(download=args.download)
        ticker_df        = get_ticker_list_from_sec(download=args.download)

        # iterate over each submission of each quarter, parse and save the data
        log.print('parsing data for %d new quarter(s)' % len(data_paths),
            num_indents=0, new_line_start=True)
        sub_parser = SubmissionParser()
        for i, path in enumerate(data_paths):
            year, quarter = tuple(path.split('/')[-1].split('q'))
            if args.quarter_list != []:
                if '%sq%s' % (year, quarter) not in args.quarter_list:
                    continue
            log.print('quarter %d of %d: %s Q%s' % (
                i+1, len(data_paths), year, quarter),
                num_indents=1, new_line_start=args.verbose, end='')
            sub_parser.parse_submissions(
                path,
                ticker_list=args.ticker_list,
                replace=args.replace,
                verbose=args.verbose,
                num_indents=2)

    # delete the tmp directory where any raw data was downloaded
    # else keep it as a data lake (if it doesn't take up that much storage)
    # TO DO: compress the data lake with the zip lib here, and decompress it at the beginning of this script
    if not args.lake:
        if os.path.exists(TMP_FILINGS_PATH):
            shutil.rmtree(TMP_FILINGS_PATH)
        os.mkdir(TMP_FILINGS_PATH)
