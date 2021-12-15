import sys
import pandas as pd
pd.set_option('display.max_rows', 1111)
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_colwidth', 2000)
pd.set_option('display.width', 100000)

# iso codes, these are different codes than what the 10-Q uses
# https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes

def x():

	num_subs_with_tag    = 0
	num_subs_without_tag = 0
	sub_df = pd.read_csv('../data/2018q4/sub.txt', sep='\t')
	num_df = pd.read_csv('../data/2018q4/num.txt', sep='\t')
	base_url = 'http://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/'
	for adsh, num_df0 in num_df.groupby('adsh'):
		num_df0.sort_values('tag', inplace=True)
		sub_df0 = sub_df[sub_df['adsh'] == adsh]
		cik = adsh.split('-')[0]
		form_type = sub_df0['form'].iloc[0]
		instance = sub_df0['instance'].iloc[0]
		url = base_url.format(cik=cik, adsh=adsh.replace('-', ''))
		if form_type in ['10-Q', '10-K']:
			# print(adsh)
			# print(num_df0.columns)
			# print(num_df0)
			# input()
			# print(num_df0['tag'].tolist())
			# for tag in num_df0['tag'].tolist():
			# 	if 'Totalassets' == tag:
			# 		print('\t', tag)
			# print('Totalassets' in num_df0['tag'].tolist())
			num_df1 = num_df0[num_df0['tag'].isin(['Assets', 'AssetsNet', 'Totalassets'])]
			if not num_df1.empty:
				# print(num_df1)
				# print(adsh)
				# sub_df0 = sub_df[sub_df['adsh'] == adsh]
				# print(sub_df0['form'])
				# print()
				num_subs_with_tag += 1
				# print('yes')
			else:
				num_subs_without_tag += 1
				print('\nno')
				print('adsh\t\t', adsh)
				print('cik\t\t', cik)
				print('form type\t', form_type)
				print('instance\t', instance)
				print(sub_df0)
				print(num_df0)
				print('%d tags' % num_df0.shape[0])
				print(url)
				print(num_df0[num_df0['value'] == 15093464000.0])
				input()

		# sys.exit()

	print(num_subs_with_tag, num_subs_without_tag)


def download_new_quarter_filings_paths():

    # get the quarters already downloaded and determine
    # the year of the most recently downloaded quarter
    with open(METADATA_FILEPATH, 'r') as f:
        metadata_dct = json.load(f)
    quarters_downloaded = metadata_dct['quarters_downloaded']
    start_year = EARLIEST_YEAR_EDGAR_OFFERS if quarters_downloaded == [] \
        else int(quarters_downloaded[-1].split('-')[0])

    # download the list of filings the SEC received from Q1 of start_year
    # to the most recent quarter and year the SEC has released
    # https://github.com/edgarminers/python-edgar/blob/master/edgar/main.py
    tmp_filings_path = os.path.join(DATA_PATH, 'quarterly_filings')
    os.mkdir(tmp_filings_path)
    edgar.download_index(
        tmp_filings_path, start_year, USER_AGENT,
        skip_all_present_except_last=False)

    # if the SEC has released new filings list(s)
    # for any quarters we haven't downloaded yet
    # parse out the needed data and
    # update the list of quarters downloaded
    new_filings = {} # key=quarter_name, value=filing_paths_df
    for filename in os.listdir(tmp_filings_path):
        quarter = filename.split('.')[0]
        if quarter not in quarters_downloaded:
            filepath = os.path.join(tmp_filings_path, filename)
            new_filings[quarter] = parse_filings_list(filepath)
            quarters_downloaded.append(quarter)
    
    # delete the downloaded list of filings and
    # update the list of quarters downloaded in the metadata file
    # and return the new_fillings_list
    shutil.rmtree(tmp_filings_path)
    if new_filings != {}:
        metadata_dct['quarters_downloaded'] = sorted(quarters_downloaded)
        with open(METADATA_FILEPATH, 'w') as f:
            json.dump(metadata_dct, f, indent=4, sort_keys=True)

    return new_filings
def test_download_new_quarter_filings_paths(test_quarter):
    tmp_filings_path = os.path.join(DATA_PATH, 'quarterly_filings')
    new_filings = {} # key=quarter_name, value=filing_paths_df
    for filename in os.listdir(tmp_filings_path):
        quarter = filename.split('.')[0]
        if quarter == test_quarter:
            filepath = os.path.join(tmp_filings_path, filename)
            new_filings[quarter] = parse_filings_list(filepath)
    return new_filings
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


if __name__ == '__main__':

	