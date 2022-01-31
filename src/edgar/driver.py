from libraries_and_constants import *

# global variables
log = logging_utils.Log(LOG_FILEPATH)



def download_standard_industrial_codes(
    num_indents=0,
    new_line_start=True):

    log.print('downloading SIC codes:',
        num_indents=num_indents,
        new_line_start=new_line_start)
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
            num_indents=num_indents+1)

        division_url = osha_url + '/' + division_html['href'].split('/')[-1]
        response = requests.get(division_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for major_group_html in soup.find_all('a', href=lambda href : \
            href != None and \
            href.startswith(major_group_href)):

            major_group_code = major_group_html.text.split(' ')[2][:-1]
            major_group_name = major_group_html.text.split(':')[1][1:]
            log.print('Major Group %s: %s' % (
                major_group_code, major_group_name),
                num_indents=num_indents+2)

            major_group_url  = osha_url + '/major-group-' + major_group_code
            response = requests.get(major_group_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for industry_group_html in soup.find_all('a', href=lambda href : \
                href != None and \
                href.startswith(industry_group_href)):

                industry_group_code = industry_group_html['title'].split(' ')[0]
                industry_group_name = ' '.join(industry_group_html['title'].split(' ')[1:])
                log.print('Industry Group %s: %s' % (
                    industry_group_code, industry_group_name),
                    num_indents=num_indents+3)

                df = df.append(pd.DataFrame({
                    'division_code'       : [division_code],       'division_name'       : [division_name],
                    'major_group_code'    : [major_group_code],    'major_group_name'    : [major_group_name],
                    'industry_group_code' : [industry_group_code], 'industry_group_name' : [industry_group_name]
                }))

    log.print('downloading codes from SEC source:', num_indents=num_indents+1)
    log.print(sec_url, num_indents=num_indents+2, new_line_end=True)
    sec_df = pd.read_html(sec_url)[0]
    sec_df['SIC Code'] = sec_df['SIC Code'].apply(lambda sic : str(sic).rjust(4, '0'))
    undefined_sic_codes = sec_df[~sec_df['SIC Code'].isin(df['industry_group_code'].tolist())]
    undefined_sic_codes.reset_index(drop=True, inplace=True)
    log.print('appending %d code(s) that are in the SEC source but not the OSHA source:' % \
        undefined_sic_codes.shape[0], num_indents=num_indents+2)
    for i, row in undefined_sic_codes.iterrows():
        sic                 = row['SIC Code']
        major_group_code    = sic[:2]
        df_row              = df[df['major_group_code'] == major_group_code].iloc[0]
        major_group_name    = df_row['major_group_name']
        division_code       = df_row['division_code']
        division_name       = df_row['division_name']
        industry_group_name = row['Industry Title']
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
    log.print('done.', num_indents=num_indents)
    return df
def download_state_and_country_codes(
    verbose=False,
    num_indents=0,
    new_line_start=True):

    # download the codes from the SEC website each time this program is run
    # because we want to know if they've changed it
    log.print('downloading latest state and country codes',
        num_indents=num_indents, new_line_start=new_line_start)
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
    if verbose:
        log.print(df.to_string(), num_indents=num_indents+1)
    log.print('done.', num_indents=num_indents)
    return df
def download_new_quarter_filings_paths(
    num_indents=0,
    new_line_start=True):

    log.print('downloading new quarter filing submission URL paths',
        num_indents=num_indents,
        new_line_start=new_line_start)

    # get the quarters already downloaded and determine
    # the year of the most recently downloaded quarter
    with open(METADATA_FILEPATH, 'r') as f:
        metadata_dct = json.load(f)
    quarters_downloaded = metadata_dct['quarters_downloaded']
    start_year = EARLIEST_YEAR_EDGAR_OFFERS if quarters_downloaded == [] \
        else int(quarters_downloaded[-1].split('-')[0])
    log.print(
        '%d quarter(s) previously downloaded %s' % (
            len(quarters_downloaded),
            ('' if len(quarters_downloaded) == 0 else (
            'from %s to %s' % (
                quarters_downloaded[0],
                quarters_downloaded[-1])))),
        num_indents=num_indents+1)

    # download the list of filings the SEC received from Q1 of start_year
    # to the most recent quarter and year the SEC has released
    # https://github.com/edgarminers/python-edgar/blob/master/edgar/main.py
    current_quarter, current_year = current_year_and_quarter()
    num_quarters = 4 * (current_year - start_year)
    log.print('downloading list of SEC filing submissions for %d quarter(s) from Q1 %d to the present quarter, Q%d %d' % (
        num_quarters, start_year, current_quarter, current_year),
        num_indents=num_indents+1)
    if os.path.exists(TMP_FILINGS_PATH):
        shutil.rmtree(TMP_FILINGS_PATH)
    os.mkdir(TMP_FILINGS_PATH)
    edgar.download_index(
        TMP_FILINGS_PATH, start_year, USER_AGENT,
        skip_all_present_except_last=False)
    log.print('done.', num_indents=num_indents+1)

    # parse out the needed data for any
    # new quarters we haven't downloaded yet
    new_quarters = {} # key=quarter_name, value=filing_paths_df
    log.print('parsed filing submission lists for:',
        num_indents=num_indents+1)
    for filename in sorted(os.listdir(TMP_FILINGS_PATH)):
        quarter = filename.split('.')[0]
        if quarter not in quarters_downloaded:
            filepath = os.path.join(TMP_FILINGS_PATH, filename)
            new_quarters[quarter] = parse_filings_list(filepath)
            log.print(quarter, num_indents=num_indents+2)
        
    # delete the downloaded list of filing submissions and
    # update the list of quarters downloaded
    # and return the new_quarters filing submissions
    shutil.rmtree(TMP_FILINGS_PATH)
    if new_quarters != {}:
        metadata_dct['quarters_downloaded'] = sorted(
            quarters_downloaded + list(new_quarters.keys()))
        with open(METADATA_FILEPATH, 'w') as f:
            json.dump(metadata_dct, f, indent=4, sort_keys=True)
    log.print('done, downloaded %d new quarters' % len(new_quarters.keys()),
        num_indents=num_indents)
    return new_quarters
def parse_filings_list(filepath):

    # remove the filings that are not in VALID_FORM_NAMES
    # and return the results
    columns = {
        'cik'          : int,
        'company_name' : str,
        'form_type'    : str,
        'date'         : str,
        'txt_path'     : str,
        'html_path'    : str
    }
    filing_paths_df = pd.read_csv(
        filepath,
        sep='|',
        lineterminator='\n',
        names=columns.keys(),
        dtype=columns)
    filing_paths_df = filing_paths_df[
        filing_paths_df['form_type'].isin(VALID_FORM_NAMES)]
    return filing_paths_df

def current_year_and_quarter():
    d = date.today()
    return year_and_quarter(d)
def year_and_quarter_from_end_date(end_date):
    d = date.fromisoformat(end_date)
    return year_and_quarter(d)
def year_and_quarter(d):
    q = pd.Timestamp(d).quarter
    y = d.year
    return q, y
def year_and_quarter_from_quarter_str(quarter_str):
    q = int(quarter_str.split('-')[1][-1])
    y = int(quarter_str.split('-')[0])
    return q, y

def download_filing(
    company_filing,
    num_indents=0,
    new_line_start=True):

    # get filing detail url
    log.print('downloading filing submission',
        num_indents=num_indents, new_line_start=new_line_start)
    filing_details_url = SEC_ARCHIVES_BASE_URL + company_filing['html_path']
    log.print('filing_details_url: %s' % filing_details_url, num_indents=num_indents+1)
    response = requests.get(filing_details_url, headers={'User-Agent' : USER_AGENT})

    # get filing's XML url
    try:
        data_files_df = pd.read_html(response.text)[1]
        # xml_path = data_files_df[data_files_df['Type'] == 'XML']['Document'].iloc[0]
        xml_path = data_files_df[data_files_df['Description'].isin([
            'XBRL INSTANCE FILE',
            'XBRL INSTANCE DOCUMENT',
            'EXTRACTED XBRL INSTANCE DOCUMENT'])]['Document'].iloc[0]
        full_xml_url = \
            SEC_ARCHIVES_BASE_URL + \
            company_filing['html_path'].replace('-', '').replace('index.html', '') + \
            '/' + xml_path
    except:
        full_xml_url = 'FAILED'
    log.print('full_xml_url:       %s' % full_xml_url, num_indents=num_indents+1)

    # get filing's HTML url
    try:
        document_format_files_df = pd.read_html(response.text)[0]
        html_path = '/' + document_format_files_df[document_format_files_df['Type'].isin(VALID_FORM_NAMES)]['Document'].iloc[0].split(' ')[0]
        tagged_base_url = '/'.join([
            '/'.join(SEC_ARCHIVES_BASE_URL.split('/')[:3]),
            'ix?doc=',
            '/'.join(SEC_ARCHIVES_BASE_URL.split('/')[3:])])
        full_html_url = tagged_base_url + company_filing['html_path'].replace('-', '').replace('index.html', html_path)
    except:
        full_html_url = 'FAILED'
    log.print('full_html_url:      %s' % full_html_url, num_indents=num_indents+1)

    # get filing's TXT url
    try:
        full_txt_url = SEC_ARCHIVES_BASE_URL + '/' + company_filing['txt_path']
    except:
        full_txt_url = 'FAILED'
    log.print('full_txt_url:       %s' % full_txt_url, num_indents=num_indents+1)

    # try to get the XML filing
    # if that fails, try to get the HTML filing
    # if that fails, try to get the TXT filing
    try:
        response = requests.get(full_xml_url, headers={'User-Agent' : USER_AGENT})
        file_type = 'XML'
        # with open('test_xml.txt', 'w') as f:
        #     f.write(response.text)
    except:
        try:
            response = requests.get(full_html_url, headers={'User-Agent' : USER_AGENT})
            file_type = 'HTML'
        except:
            try:
                response = requests.get(full_txt_url, headers={'User-Agent' : USER_AGENT})
                file_type = 'TXT'
            except:
                response = None
                file_type = None
    if response != None:
        log.print('done, downloaded %s filing' % file_type, num_indents=num_indents)
    else:
        log.print('done. FAILED to download filing', num_indents=num_indents)
    return response, file_type
def parse_filing(
    filing,
    file_type,
    quarter_str,
    form_type,
    num_indents=0,
    new_line_start=True):

    if file_type == 'XML':
        parser = XML_Parser(
            filing.text,
            quarter_str,
            form_type)
    elif file_type == 'HTML':
        parser = HTML_Parser(
            filing.text,
            quarter_str,
            form_type)

    elif file_type == 'TXT':

        # parse html from txt
        html_txt = filing.text

        parser = HTML_Parser(
            html_txt,
            quarter_str,
            form_type)

    else:
        pass

    return parser.parse_filing(
        num_indents=num_indents,
        new_line_start=new_line_start)
class XML_Parser:
    def __init__(
        self,
        filing_txt,
        quarter_str,
        form_type):

        self.xml = BeautifulSoup(filing_txt, 'lxml')
        self.quarter_str = quarter_str
        self.form_type = form_type

    def parse_filing(
        self,
        num_indents=0,
        new_line_start=True):

        log.print('parsing XML file for fundamental data',
            num_indents=num_indents,
            new_line_start=new_line_start)

        # note: quarter from xml filing is different from quarter from quarter_str
        # going with the quarter on the xml filing
        self.filing_quarter, self.filing_year = self.parse_quarter_and_year(num_indents=num_indents+1)
        # self.filing_quarter, self.filing_year = year_and_quarter_from_quarter_str(quarter_str)
        if   self.form_type == '10-K': self.period_months = 12
        elif self.form_type == '10-Q': self.period_months = 3

        ticker             = self.parse_value_2('ticker',             num_indents=num_indents+1)
        company_name       = self.parse_value_2('company_name',       num_indents=num_indents+1)
        cik                = self.parse_value_2('cik',                num_indents=num_indents+1, value_type='int')
        shares_outstanding = self.parse_value_1('shares_outstanding', num_indents=num_indents+1, filter_period_duration=False)
        # total_revenue      = self.parse_value_1('total_revenue',      num_indents=num_indents+1)
        net_income         = self.parse_value_1('net_income',         num_indents=num_indents+1)
        total_assets       = self.parse_value_1('total_assets',       num_indents=num_indents+1)
        total_liabilities  = self.parse_total_liabilities(num_indents=num_indents+1)
        dividend_per_share = self.parse_dividend_per_share(num_indents=num_indents+1)
        dividends_paid     = self.parse_dividends_paid(num_indents=num_indents+1)
        # stock_split        = self.parse_stock_split(num_indents=num_indents+1)
        country            = self.parse_country(num_indents=num_indents+1)
        # sic, division, major_group, industry_group = \
        #     parse_sic_and_industry_classification_names(cik,
        #         num_indents=num_indents+1)

        fundamental_data = {
            'ticker'                  : ticker,
            'company_name'            : company_name,
            'cik'                     : cik,
            'quarter'                 : self.filing_quarter,
            'year'                    : self.filing_year,
            'shares_outstanding'      : shares_outstanding,
            # 'stock_split'             : stock_split,
            'net_income'              : net_income,
            # 'total_revenue'           : total_revenue,
            'total_assets'            : total_assets,
            'total_liabilities'       : total_liabilities,
            'dividend_per_share'      : dividend_per_share,
            'dividends_paid'          : dividends_paid,
            'country'                 : country,
            # 'industry_classification' : {
            #     'sic' : {
            #         'sic'             : sic,
            #         'division'        : division,
            #         'major_group'     : major_group,
            #         'industry_group'  : industry_group
            #     }
            # },
        }
        log.print_dct(fundamental_data, num_indents=num_indents+1)
        log.print('done', num_indents=num_indents)
        return fundamental_data
    def parse_quarter_and_year(
        self,
        num_indents=0,
        new_line_start=False):

        end_date = self.xml.find('dei:documentperiodenddate').string
        try:
            quarter, year = year_and_quarter_from_end_date(end_date)
        except:
            quarter, year = None, None
        log.print('parsing of quarter %s' % (
            'SUCCEEDED' if (quarter != None and year != None) else 'FAILED'),
            num_indents=num_indents)
        return quarter, year
    def parse_stock_split(
        self,
        num_indents=0):

        split_type = None
        ratio      = None
        split_date = None
        tags       = XML_DATA_TAGS['stock_split']['tags']
        attributes = XML_DATA_TAGS['stock_split']['attributes']
        for row in xml.find_all(tags, attrs=attributes):
            # print(row)
            context = xml.find(['context', 'xbrli:context'], id=row['contextref'])
            # print(context)
            if context == None:
                continue
            try:
                row_end_date = context.find(['instant', 'xbrli:instant']).string
                period_duration = 0
            except:
                row_end_date   = context.find(['enddate', 'xbrli:enddate']).string
                row_start_date = context.find(['startdate', 'xbrli:startdate']).string
                period_duration = (date.fromisoformat(row_end_date) - date.fromisoformat(row_start_date)).days

            # filter out period durations that aren't an instant
            if period_duration != 0:
                continue

            # just take the first one
            try:
                split_type = 'tbd'
                ratio      = int(row.string)
                split_date = row_end_date
                break
            except:
                continue

        succeeded = (ratio != None) and (split_date != None) and (split_type != None)
        log.print('parsing of stock_split %s' % (
            'SUCCEEDED' if succeeded else 'FAILED'),
            num_indents=num_indents)
        return {
            'type'  : split_type,
            'ratio' : ratio,
            'date'  : split_date
        } if succeeded else None
    def parse_total_liabilities(
        self,
        num_indents=0,
        new_line_start=False):

        total_liabilities = self.parse_value_1('total_liabilities', verbose=False)
        ''' note, this 10-Q doesn't state total liabilities
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
        if total_liabilities == None:
            total_liabilities_and_equity = self.parse_value_1(
                'total_liabilities_and_equity',
                verbose=False)
            total_equity = self.parse_value_1(
                'total_equity',
                verbose=False)
            if total_liabilities_and_equity != None and total_equity != None:
                total_liabilities = total_liabilities_and_equity - total_equity

        log.print('parsing of total_liabilities %s' % (
            'SUCCEEDED' if total_liabilities != None else 'FAILED'),
            num_indents=num_indents, new_line_start=new_line_start)
        return total_liabilities
    def parse_dividend_per_share(
        self,
        num_indents=0,
        new_line_start=False):

        dividend_per_share = self.parse_value_1(
            'dividend_per_share',
            value_type='float',
            num_indents=num_indents,
            new_line_start=new_line_start)

        # assume a dividend of $0.00 if none could be found
        return dividend_per_share if dividend_per_share != None else 0.0
    def parse_dividends_paid(
        self,
        num_indents=0,
        new_line_start=False):

        # try to find the dividends paid just this quarter (except if its a 10-K form)
        dividends_paid = None if self.form_type == '10-K' else \
            self.parse_value_1('dividends_paid', verbose=False)

        # if you cant find it then try to find dividends paid for the entire year so far
        # and subtract the previous quarters' dividends paid to get the
        # dividends paid for just this quarter
        if dividends_paid == None:
            dividends_paid = self.parse_value_1(
                'dividends_paid',
                filter_period_duration=False,
                verbose=False)
            if dividends_paid != None:
                dividends_paid_previous_quarters = [] # TODO: list of ints, pull from local database
                dividends_paid -= sum(dividends_paid_previous_quarters)
        log.print('parsing of dividends_paid %s' % (
            'SUCCEEDED' if dividends_paid != None else 'FAILED'),
            num_indents=num_indents)

        # assume a dividend of $0 if none could be found
        return dividends_paid if dividends_paid != None else 0
    def parse_country(
        self,
        num_indents=0,
        new_line_start=False):

        code = self.parse_value_2('state_or_country_code', verbose=False)
        country = state_country_codes_df[state_country_codes_df['code'] == code]['country'].iloc[0] \
            if code != None else None
        log.print('parsing of country %s' % (
            'SUCCEEDED' if country != None else 'FAILED'),
            num_indents=num_indents)
        return country
    def parse_sic_and_industry_classification_names(
        self,
        cik,
        num_indents=0,
        new_line_start=False):

        sic = self.parse_sic_code(cik, verbose=False)
        if sic != None:
            try:
                division = sic_codes_df[sic_codes_df['industry_group_code'] == sic]['division_name'].iloc[0]
            except:
                division = None
            try:
                major_group = sic_codes_df[sic_codes_df['industry_group_code'] == sic]['major_group_name'].iloc[0]
            except:
                major_group = None
            try:
                industry_group = sic_codes_df[sic_codes_df['industry_group_code'] == sic]['industry_group_name'].iloc[0]
            except:
                industry_group = None
        else:
            division = None
            major_group = None
            industry_group = None
        succeeded = \
            sic            != None and \
            division       != None and \
            major_group    != None and \
            industry_group != None
        log.print(
            'parsing of SIC and industry classification names %s' % (
                'SUCCEEDED' if succeeded else 'FAILED'),
            num_indents=num_indents)
        return sic, division, major_group, industry_group
    def parse_sic_code(
        self,
        cik,
        verbose=True,
        num_indents=0,
        new_line_start=False):
        
        ten_digit_cik = str(cik).rjust(10, '0')
        url = 'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=%s' % ten_digit_cik
        '''
        found this URL by clicking "Get insider transactions for this issuer" on the SEC CIK lookup page
        example: https://www.sec.gov/edgar/browse/?CIK=1000045
        '''
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        href_str = '/cgi-bin/browse-edgar?action=getcompany'
        sic_html_element = soup.find('a', href=lambda href : \
            href.startswith(href_str) and ('SIC' in href))
        try:
            sic = sic_html_element.text
        except:
            sic = None
        if verbose:
            log.print('parsing of SIC %s' % (
                'SUCCEEDED' if sic != None else 'FAILED'),
                num_indents=num_indents)
        return sic
    def parse_total_cash_inflow(
        self,
        num_indents=0,
        new_line_start=False):

        # Total Cash Inflow will equal
        # Total Net Sales
        # and then add "Other Income/Expenses, net" if "Other Income/Expenses, net" is positive (aka cash inflow)
        # TODO: the problem is not all filings have Total Net Sales
        # example: https://www.sec.gov/Archives/edgar/data/1000045/0001564590-21-043733-index.html

        total_net_sales = self.parse_total_net_sales(self.filing_quarter)
        # other_income_expenses_net = 
        total_cash_inflow = total_net_sales + (other_income_expenses_net if other_income_expenses_net > 0 else 0)    
    def parse_value_1(
        self,
        value_name,
        value_type='int',
        filter_period_duration=True,
        verbose=True,
        num_indents=0,
        new_line_start=False):

        value = None
        tags = XML_DATA_TAGS[value_name]['tags']
        attributes = XML_DATA_TAGS[value_name]['attributes']
        for row in self.xml.find_all(tags, attrs=attributes):
            # print(row)
            context = self.xml.find(['context', 'xbrli:context'], id=row['contextref'])
            if context == None:
                continue
            try:
                row_end_date   = context.find(['instant',   'xbrli:instant']).string
            except:
                row_end_date   = context.find(['enddate',   'xbrli:enddate']).string
                row_start_date = context.find(['startdate', 'xbrli:startdate']).string

                # filter out period durations that aren't period_months long
                period_duration = date.fromisoformat(row_end_date) - date.fromisoformat(row_start_date)
                num_months = round(period_duration.days / 30.0)
                if filter_period_duration and num_months != self.period_months:
                    continue

            # filter out rows that are not for the quarter we're looking for
            row_quarter, row_year = year_and_quarter_from_end_date(row_end_date)
            if not (row_quarter == self.filing_quarter and row_year == self.filing_year):
                continue

            # filter out non numeric values if value_type = 'int'
            if value_type == 'int':
                try:
                    value = int(row.string)
                except:
                    continue

            # just take the first one
            # print(row)
            # print('row_end_date row_quarter row_year: %s %s %s' % (row_end_date, row_quarter, row_year))
            if   value_type == 'int':   value = int(row.string)
            elif value_type == 'float': value = float(row.string)
            break
        if verbose:
            log.print('parsing of %s %s' % (
                value_name, ('SUCCEEDED' if value != None else 'FAILED')),
                num_indents=num_indents)
        return value
    def parse_value_2(
        self, value_name, value_type='string',
        verbose=True, num_indents=0, new_line_start=False):

        tags = XML_DATA_TAGS[value_name]['tags']
        attributes = XML_DATA_TAGS[value_name]['attributes']
        try:
            value = self.xml.find(tags, attrs=attributes).string
            if   value_type == 'int':    value = int(value.string)
            elif value_type == 'float':  value = float(value.string)
            elif value_type == 'string':
                # value = value.replace('\u00a0', ' ')
                # value = value.replace('\u00e9')
                value = re.sub(r'\\u[0-9a-f]{4}', '', value) # to do: for some reason this doesn't work, see the 10-K for "company_name": "Est\u00e9e Lauder Companies Inc", for 2021-Q3
                # value = restore_windows_1252_characters(value)
                # value = value.decode('unicode_escape').encode('utf-8')
                # value = ''.join(unicodize(seg) for seg in re.split(r'(\\u[0-9a-f]{4})', value))

        except:
            value = None
        if verbose:
            log.print('parsing of %s %s' % (
                value_name, ('SUCCEEDED' if value != None else 'FAILED')),
                num_indents=num_indents)
        return value
class HTML_Parser:
    def __init__(
        self,
        filing,
        quarter_str,
        form_type):

        self.html = BeautifulSoup(filing_txt, 'lxml')
        self.quarter_str = quarter_str
        self.form_type = form_type

    def parse(self):
        pass

    def parse_html_from_txt(self):
        pass



def get_daily_price_data(
    fundamental_data,
    quarter,
    num_indents=0,
    new_line_start=False):

    price_data = pd.DataFrame(columns=['date', 'closing_price'])

    ticker = fundamental_data['ticker']
    start_date = 'tbd'
    end_date = 'tbd'
    # query exchange here

    return price_data


def unicodize(seg):
    if re.match(r'\\u[0-9a-f]{4}', seg):
        return seg.decode('unicode-escape')
    return seg.decode('utf-8')









def restore_windows_1252_characters(restore_string):
    """
        Replace C1 control characters in the Unicode string s by the
        characters at the corresponding code points in Windows-1252,
        where possible.
    """

    def to_windows_1252(match):
        try:
            return bytes([ord(match.group(0))]).decode('windows-1252')
        except UnicodeDecodeError:
            # No character at the corresponding code point: remove it.
            return ''
        
    return re.sub(r'[\u0080-\u0099]', to_windows_1252, restore_string)
def save_to_database(
    fundamental_data,
    price_data,
    num_indents=0,
    new_line_start=True):

    pass

def download_form(
    cik,
    year=None,
    num_indents=0,
    new_line_start=True):

    log.print('Downloading Form',
        num_indents=num_indents,
        new_line_start=new_line_start)

    columns = {
        'cik'          : int,
        'company_name' : str,
        'form_name'    : str,
        'date'         : str,
        'path1'        : str,
        'path2'        : str
    }
    filings_df = pd.read_csv(
        os.path.join(DATA_PATH, '2019-QTR3.tsv'),
        sep='|',
        lineterminator='\n',
        names=columns.keys(),
        dtype=columns)

    report_row = filings_df[
        (filings_df['cik'] == cik) & \
        (filings_df['form_name'].isin(VALID_FORM_NAMES))]
    form_name = report_row['form_name'].iloc[0]
    log.print('found form: %s' % form_name,
        num_indents=num_indents+1)

    report_path = report_row['path2'].iloc[0]
    print(type(report_path), report_path)
    # sys.exit()

    url = 'https://www.sec.gov/Archives/' + report_path
    # Example: https://www.sec.gov/ix?doc=/Archives/edgar/data/1652044/000165204419000032/goog10-qq32019.htm
    print(url)
    header = { 'User-Agent' : USER_AGENT}
    response = requests.get(url, headers=header)

    # https://pandas.pydata.org/docs/reference/api/pandas.read_html.html
    # https://stackoverflow.com/questions/18939133/how-to-modify-pandass-read-html-user-agent
    document_format_files_df = pd.read_html(response.text)[0]
    document_format_files_df = document_format_files_df[document_format_files_df['Seq'].notna()]
    # print(document_format_files_df); sys.exit()

    document_name = document_format_files_df[
        document_format_files_df['Description'] == form_name]
    # print(document_name)

    document_name = document_name['Document'].str.split(' ')[0][0]
    # print(document_name)

    formatted_report_path = report_path.replace('-', '').replace('index.html', '')
    url = 'https://www.sec.gov/Archives/' + formatted_report_path + '/' + document_name
    print(url)

    response = requests.get(url, headers=header)
    dfs = pd.read_html(response.text)[1]
    print(df); sys.exit()
    sys.exit()

    for df in dfs:
        BS = (df[0].str.contains('Retained') | df[0].str.contains('Total Assets'))
        if BS.any():
            Balance_Sheet = df
            

    Balance_Sheet = Balance_Sheet.iloc[2:,[0,2,6]]

    header = Balance_Sheet.iloc[0]
    Balance_Sheet = Balance_Sheet[1:]

    Balance_Sheet.columns = header


    Balance_Sheet.columns.values[0] = 'Item'
    Balance_Sheet = Balance_Sheet[Balance_Sheet['Item'].notna()]

    Balance_Sheet[Balance_Sheet.columns[1:]] = Balance_Sheet[Balance_Sheet.columns[1:]].astype(str)
    Balance_Sheet[Balance_Sheet.columns[1]] = Balance_Sheet[Balance_Sheet.columns[1]].map(lambda x: x.replace('(','-'))
    Balance_Sheet[Balance_Sheet.columns[2]] = Balance_Sheet[Balance_Sheet.columns[2]].map(lambda x: x.replace('(','-'))

    Balance_Sheet[Balance_Sheet.columns[1]] = Balance_Sheet[Balance_Sheet.columns[1]].map(lambda x: x.replace(',',''))
    Balance_Sheet[Balance_Sheet.columns[2]] = Balance_Sheet[Balance_Sheet.columns[2]].map(lambda x: x.replace(',',''))

    Balance_Sheet[Balance_Sheet.columns[1]] = Balance_Sheet[Balance_Sheet.columns[1]].map(lambda x: x.replace('—','0'))
    Balance_Sheet[Balance_Sheet.columns[2]] = Balance_Sheet[Balance_Sheet.columns[2]].map(lambda x: x.replace('—','0'))



    Balance_Sheet[Balance_Sheet.columns[1:]] = Balance_Sheet[Balance_Sheet.columns[1:]].astype(float)

    print(type(Balance_Sheet))
    print(Balance_Sheet)




if __name__ == '__main__':

    # sic_codes_df = download_standard_industrial_codes()
    state_country_codes_df = download_state_and_country_codes()
    new_quarters = download_new_quarter_filings_paths()

    if new_quarters != {}:
        log.print('iterating over the submissions of each new quarter',
            num_indents=0, new_line_start=True)
        for i, (quarter, filing_df) in enumerate(new_quarters.items()):
            log.print('quarter %d of %d: %s' % (
                i+1, len(new_quarters.keys()), quarter),
                num_indents=1)
            filing_df.reset_index(inplace=True, drop=True) # reset just for the log
            for j, company_filing in filing_df.iterrows():
                log.print('company filing submission %d of %d' % (
                    j+1, filing_df.shape[0]),
                    num_indents=2)
                log.print('form type: %s' % company_filing['form_type'], num_indents=3)
                # if j+1 < 386: continue # for testing purposes only
                filing, file_type = download_filing(company_filing, num_indents=3)
                if filing == None:
                    continue
                fundamental_data = parse_filing(
                    filing, file_type, quarter, company_filing['form_type'], num_indents=3)
                price_data = get_daily_price_data(fundamental_data, quarter, num_indents=3)
                save_to_database(fundamental_data, price_data, num_indents=3)
                time.sleep(0.5)
                input()
                # if fundamental_data['stock_split'] != None:
                #     sys.exit()


