from libraries_and_constants import *

# global variables
log = logging_utils.Log(LOG_FILEPATH)
xml = None
filing_quarter = None
filing_year = None


def download_state_and_country_codes():

    # download the codes from the SEC website each time this program is run
    # because we want to know if they've changed it
    url             = 'https://www.sec.gov/edgar/searchedgar/edgarstatecodes.htm'
    df              = pd.DataFrame(columns=['code', 'country', 'state'])
    current_country = 'United States'
    for i, row in pd.read_html(url)[0].iterrows():
        code = row['Code']['States']
        name = row['State or Country Name']['States']
        if code == 'Canadian Provinces' and name == 'Canadian Provinces':
            current_country = 'Canada'
            continue
        elif code == 'Other Countries' and name == 'Other Countries':
            current_country = None
            continue
        if current_country == 'Canada':
            name = name.split(',')[0]
        df = df.append(pd.DataFrame({
            'code'    : [code],
            'country' : [current_country if current_country != None else name],
            'state'   : [name if current_country != None else None]
        }))
    df.reset_index(drop=True, inplace=True)
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
        '%d quarters previously downloaded %s' % (
            len(quarters_downloaded),
            ('' if len(quarters_downloaded) == 0 else (
            'from %s to %s' % (
                quarters_downloaded[0],
                quarters_downloaded[-1])))),
        num_indents=num_indents+1)

    # download the list of filings the SEC received from Q1 of start_year
    # to the most recent quarter and year the SEC has released
    # https://github.com/edgarminers/python-edgar/blob/master/edgar/main.py
    if os.path.exists(TMP_FILINGS_PATH):
        shutil.rmtree(TMP_FILINGS_PATH)
    os.mkdir(TMP_FILINGS_PATH)
    edgar.download_index(
        TMP_FILINGS_PATH, start_year, USER_AGENT,
        skip_all_present_except_last=False)
    log.print('downloaded list of SEC filing submissions from Q1 of %s to present' % start_year,
        num_indents=num_indents+1)

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

def download_xml_filing(
    company_filing,
    num_indents=0,
    new_line_start=True):

    log.print('downloading XML of filing submission',
        num_indents=num_indents, new_line_start=new_line_start)
    filing_details_url = SEC_ARCHIVES_BASE_URL + company_filing['html_path']
    log.print('filing_details_url: %s' % filing_details_url, num_indents=num_indents+1)
    response = requests.get(filing_details_url, headers={'User-Agent' : USER_AGENT})
    data_files_df = pd.read_html(response.text)[1]
    # xml_path = data_files_df[data_files_df['Type'] == 'XML']['Document'].iloc[0]
    xml_path = data_files_df[data_files_df['Description'].isin([
        'XBRL INSTANCE DOCUMENT',
        'EXTRACTED XBRL INSTANCE DOCUMENT'])]['Document'].iloc[0]
    full_xml_url = \
        SEC_ARCHIVES_BASE_URL + \
        company_filing['html_path'].replace('-', '').replace('index.html', '') + \
        '/' + xml_path
    log.print('full_xml_url:       %s' % full_xml_url, num_indents=num_indents+1)
    response = requests.get(full_xml_url, headers={'User-Agent' : USER_AGENT})
    # with open('test_xml.txt', 'w') as f:
    #     f.write(response.text)
    log.print('done', num_indents=num_indents)
    return response
def parse_xml_filing(
    xml_filing,
    quarter_str,
    num_indents=0,
    new_line_start=True):

    log.print('parsing XML for fundamental data',
        num_indents=num_indents,
        new_line_start=new_line_start)

    global xml, filing_quarter, filing_year
    xml = BeautifulSoup(xml_filing.text, 'lxml')
    # note: quarter from xml filing is different from quarter from quarter_str
    # going with the quarter on the xml filing
    filing_quarter, filing_year = parse_quarter_and_year_from_xml(num_indents=num_indents+1)
    # filing_quarter, filing_year = year_and_quarter_from_quarter_str(quarter_str)

    ticker                = parse_value_from_xml_2('ticker',                num_indents=num_indents+1)
    company_name          = parse_value_from_xml_2('company_name',          num_indents=num_indents+1)
    cik                   = parse_value_from_xml_2('cik', value_type='int', num_indents=num_indents+1)
    shares_outstanding    = parse_value_from_xml_1('shares_outstanding',    num_indents=num_indents+1)
    net_income            = parse_value_from_xml_1('net_income',            num_indents=num_indents+1)
    # total_revenue         = parse_value_from_xml_1('total_revenue',         num_indents=num_indents+1)
    total_assets          = parse_value_from_xml_1('total_assets',          num_indents=num_indents+1)
    total_liabilities     = parse_total_liabilities_from_xml(num_indents=num_indents+1)
    dividend_per_share    = parse_dividend_per_share_from_xml(num_indents=num_indents+1)
    dividends_paid        = parse_dividends_paid_from_xml(num_indents=num_indents+1)
    country               = parse_country_from_xml(num_indents=num_indents+1)
    sic, sector, industry = parse_sector_and_industry(cik, num_indents=num_indents+1)

    fundamental_data = {
        'ticker'             : ticker,
        'company_name'       : company_name,
        'cik'                : cik,
        'quarter'            : filing_quarter,
        'year'               : filing_year,
        'shares_outstanding' : shares_outstanding,
        'net_income'         : net_income,
        # 'total_revenue'      : total_revenue,
        'total_assets'       : total_assets,
        'total_liabilities'  : total_liabilities,
        'dividend_per_share' : dividend_per_share,
        'dividends_paid'     : dividends_paid,
        'country'            : country,
        'sic'                : sic,
        'sector'             : sector,
        'industry'           : industry
    }
    log.print_dct(fundamental_data, num_indents=num_indents+1)
    log.print('done', num_indents=num_indents)
    return fundamental_data
def parse_quarter_and_year_from_xml(
    num_indents=0,
    new_line_start=False):

    end_date = xml.find('dei:documentperiodenddate').string
    try:
        quarter, year = year_and_quarter_from_end_date(end_date)
    except:
        quarter, year = None, None
    log.print('parsing of quarter %s' % (
        'SUCCEEDED' if (quarter != None and year != None) else 'FAILED'),
        num_indents=num_indents)
    return quarter, year
def parse_total_liabilities_from_xml(
    num_indents=0, new_line_start=False):

    total_liabilities = parse_value_from_xml_1('total_liabilities', verbose=False)
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
        total_liabilities_and_equity = parse_value_from_xml_1(
            'total_liabilities_and_equity',
            verbose=False)
        total_equity = parse_value_from_xml_1(
            'total_equity',
            verbose=False)
        if total_liabilities_and_equity != None and total_equity != None:
            total_liabilities = total_liabilities_and_equity - total_equity

    log.print('parsing of total_liabilities %s' % (
        'SUCCEEDED' if total_liabilities != None else 'FAILED'),
        num_indents=num_indents, new_line_start=new_line_start)
    return total_liabilities
def parse_dividend_per_share_from_xml(
    num_indents=0, new_line_start=False):

    dividend_per_share = parse_value_from_xml_1(
        'dividend_per_share',
        value_type='float',
        num_indents=num_indents,
        new_line_start=new_line_start)

    # assume a dividend of $0.00 if none could be found
    return dividend_per_share if dividend_per_share != None else 0.0
def parse_dividends_paid_from_xml(
    num_indents=0, new_line_start=False):

    # try to find the dividends paid just this quarter
    dividends_paid = parse_value_from_xml_1(
        'dividends_paid', period_months=3, verbose=False)

    # if you cant find it then try to find dividends paid for the entire year so far
    # and subtract the previous quarters' dividends paid to get the
    # dividends paid for just this quarter
    if dividends_paid == None:
        dividends_paid = parse_value_from_xml_1(
            'dividends_paid', period_months=None, verbose=False)
        if dividends_paid != None:
            dividends_paid_previous_quarters = [] # TODO: list of ints, pull from mysql db
            dividends_paid -= sum(dividends_paid_previous_quarters)
    log.print('parsing of dividends_paid %s' % (
        'SUCCEEDED' if dividends_paid != None else 'FAILED'),
        num_indents=num_indents)

    # assume a dividend of $0 if none could be found
    return dividends_paid if dividends_paid != None else 0
def parse_country_from_xml(
    num_indents=0, new_line_start=False):

    code = parse_value_from_xml_2('state_or_country_code', verbose=False)
    country = state_country_codes_df[state_country_codes_df['code'] == code]['country'].iloc[0]
    log.print('parsing of country %s' % (
        'SUCCEEDED' if country != None else 'FAILED'),
        num_indents=num_indents)
    return country
def parse_sector_and_industry(
    cik,
    num_indents=0, new_line_start=False):
    sic = parse_sic_code(cik)
    if sic == None:
        return None, None
    sector = 'tbd'
    industry = 'tbd'
    return sic, sector, industry
def parse_sic_code(
    cik,
    num_indents=0, new_line_start=False):
    
    ten_digit_cik = str(cik).rjust(10, '0')
    url = 'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=%s' % ten_digit_cik
    '''
    found this URL by clicking "Get insider transactions for this issuer" on the SEC CIK lookup page
    example: https://www.sec.gov/edgar/browse/?CIK=1000045
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    href_str = '/cgi-bin/browse-edgar?action=getcompany'
    sic_html_element = soup.find('a', href= lambda href : \
        href.startswith(href_str) and ('SIC' in href))
    try:
        sic = int(sic_html_element.text)
    except:
        sic = None
    log.print('parsing of SIC %s' % (
        'SUCCEEDED' if sic != None else 'FAILED'),
        num_indents=num_indents)
    return sic
def parse_total_cash_inflow_from_xml(
    xml, filing_quarter, filing_year,
    num_indents=0, new_line_start=False):

    # Total Cash Inflow will equal
    # Total Net Sales
    # and then add "Other Income/Expenses, net" if "Other Income/Expenses, net" is positive (aka cash inflow)
    # TODO: the problem is not all filings have Total Net Sales
    # example: https://www.sec.gov/Archives/edgar/data/1000045/0001564590-21-043733-index.html

    total_net_sales = parse_total_net_sales_from_xml(xml, filing_quarter)
    # other_income_expenses_net = 
    total_cash_inflow = total_net_sales + (other_income_expenses_net if other_income_expenses_net > 0 else 0)    
def parse_value_from_xml_1(
    value_name, value_type='int', period_months=3,
    verbose=True, num_indents=0, new_line_start=False):

    value = None
    tags = XML_DATA_TAGS[value_name]['tags']
    attributes = XML_DATA_TAGS[value_name]['attributes']
    for row in xml.find_all(tags, attrs=attributes):
        context = xml.find('context', id=row['contextref'])
        try:
            row_end_date = context.find('instant').string
        except:
            row_end_date   = context.find('enddate').string
            row_start_date = context.find('startdate').string

            # filter out period durations that aren't a quarter
            period_duration = date.fromisoformat(row_end_date) - date.fromisoformat(row_start_date)
            num_months = round(period_duration.days / 30.0)
            if num_months != period_months and period_months != None:
                continue

        # filter out rows that are not for the quarter we're looking for
        row_quarter, row_year = year_and_quarter_from_end_date(row_end_date)
        if not (row_quarter == filing_quarter and row_year == filing_year):
            continue

        # just take the first one
        if   value_type == 'int':   value = int(row.string)
        elif value_type == 'float': value = float(row.string)
        break
    if verbose:
        log.print('parsing of %s %s' % (
            value_name, ('SUCCEEDED' if value != None else 'FAILED')),
            num_indents=num_indents)
    return value
def parse_value_from_xml_2(
    value_name, value_type='string',
    verbose=True, num_indents=0, new_line_start=False):

    tags = XML_DATA_TAGS[value_name]['tags']
    attributes = XML_DATA_TAGS[value_name]['attributes']
    try:
        value = xml.find(tags, attrs=attributes).string
        if   value_type == 'int':   value = int(value.string)
        elif value_type == 'float': value = float(value.string)
    except:
        value = None
    if verbose:
        log.print('parsing of %s %s' % (
            value_name, ('SUCCEEDED' if value != None else 'FAILED')),
            num_indents=num_indents)
    return value






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

    state_country_codes_df = download_state_and_country_codes()
    new_quarters = download_new_quarter_filings_paths()

    # new_filings = test_download_new_quarter_filings_paths('2020-QTR3')
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
                xml_filing = download_xml_filing(company_filing, num_indents=3)
                fundamental_data = parse_xml_filing(xml_filing, quarter, num_indents=3)
                save_to_database(fundamental_data, num_indents=3)
                time.sleep(0.5)
                input()


