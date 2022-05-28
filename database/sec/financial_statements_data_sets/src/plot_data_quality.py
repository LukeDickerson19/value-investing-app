from libraries_and_constants import *

# global variables
log = logging_utils.Log(LOG_FILEPATH)

CHART_NAMES = [
	'Stock vs Quarter',
	'Metric vs Quarter',
	'Metric vs Stock',
	'Price Data Stock vs Day'
]



def select_chart(
	num_indents=0):

	user_input = None
	while user_input == None:
		log.print('Select which chart to view:',
			num_indents=num_indents,
			new_line_start=True)
		log.print('1) stock vs quarter',        num_indents=num_indents+1)
		log.print('2) metric vs quarter',       num_indents=num_indents+1)
		log.print('3) metric vs stock',         num_indents=num_indents+1)
		log.print('4) price data stock vs day', num_indents=num_indents+1)
		user_input = input()
		if user_input not in ['1', '2', '3', '4']:
			user_input = None
			log.print('invalid input, valid inputs are [1, 2, 3, 4]',
				num_indents=num_indents+1)
		else:
			break

	log.print('Selected option %s: %s' % (user_input, CHART_NAMES[int(user_input) - 1]),
		num_indents=num_indents)
	return int(user_input)
def plot_stock_vs_quarter(
	verbose=False,
	num_indents=0,
	new_line_start=False):
	
	log.print('plotting \"%s\" chart ...' % CHART_NAMES[0],
		num_indents=num_indents, new_line_start=True)

	with open(METADATA_FILEPATH, 'r') as f:
		metadata_dct = json.load(f)
	df = pd.read_csv(
		QUALITY_REPORT_PATHS['stock_vs_quarter']['variable'],
		index_col='cik')

	num_stocks           = int(metadata_dct['total_number_of_stocks'])
	quarters             = metadata_dct['quarters_parsed']['quarters']
	earliest_quarter     = quarters[0]
	latest_quarter       = quarters[-1]
	num_quarters         = int(metadata_dct['quarters_parsed']['count'])
	num_variable_metrics = int(metadata_dct['number_of_metrics']['variable'])


	fig, ax = plt.subplots()#figsize=(12, 6.5))
	fig.canvas.manager.set_window_title(CHART_NAMES[0])
	fig.canvas.manager.window.showMaximized() # go fullscreen
	cmap = mcolors.LinearSegmentedColormap.from_list(
		'', ['red', 'orange', 'yellow', 'green'])
	# colormaps: https://matplotlib.org/devdocs/tutorials/colors/colormaps.html#list-colormaps
	norm = mcolors.Normalize(vmin=0, vmax=num_variable_metrics)
	plot = ax.pcolormesh(df, cmap=cmap, norm=norm)
	ax.set_title(
		'Data Coverage of %d variable metrics of %d Stocks over %d Quarters (%.2f Years)' % (
			num_variable_metrics, num_stocks, num_quarters, (num_quarters / 4)),
		fontsize=14)
	ax.set_ylabel('%d Stocks' % num_stocks)# (sorted from least to most coverage)' % num_stocks)
	ax.set_yticks([])
	ax.set_xlabel('Quarters')
	ax.set_xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90) # Code C

	# legend
	# source: https://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
	divider = make_axes_locatable(ax)
	cax = divider.append_axes('right', size='5%', pad=0.10)
	cbar = fig.colorbar(
		plot,
		cax=cax,
		orientation='vertical')
	cbar.ax.set_ylabel('Percent Data Coverage (out of %d variable metrics)' % num_variable_metrics, fontsize=12)
	# tick_locs = np.linspace(0, num_variable_metrics - 1, 5)
	# cbar.set_ticks(tick_locs)
	# cbar.ax.set_yticklabels(['0 %', '25 %', '50 %', '75 %', '100 %'])

	def format_coord(x, y):
		# TO DO: fix this
		# if int(x) > len(quarters) or int(x) < 0: return ''
		# if int(y) > df.shape[0] or int(y) < 0: return ''
		# print(x, y, len(quarters), df.shape[0])
		q = quarters[int(x)]
		cik = df.iloc[int(y)].name
		s1 = 'quarter=%s' % q
		s2 = 'cik=%s' % cik
		s3 = '%d of %d variable metrics found' % (
			df.at[cik, q], num_variable_metrics)
		return '\t'.join([s1, s2, s3])
	ax.format_coord = format_coord

	fig.autofmt_xdate()
	fig.tight_layout()
	plt.show()
def plot_metric_vs_quarter(
	verbose=False,
	num_indents=0,
	new_line_start=False):
	
	log.print('plotting \"%s\" chart ...' % CHART_NAMES[0],
		num_indents=num_indents, new_line_start=True)

	with open(METADATA_FILEPATH, 'r') as f:
		metadata_dct = json.load(f)
	df = pd.read_csv(
		QUALITY_REPORT_PATHS['metric_vs_quarter']['variable'],
		index_col='metric')
	# search_cols = list(filter(lambda c : c.split('-')[1] == 'searched', df.columns))
	# print(search_cols)
	# print(df[search_cols])
	quarters = list(set(map(lambda c : c.split('-')[0], df.columns)))
	quarters.sort()
	# print(quarters)
	variable_metrics = df.index.tolist()
	# print(variable_metrics)

	fraction_df = pd.DataFrame(columns=quarters, index=df.index)
	for q in quarters:
		for m in variable_metrics:
			f, s = df.at[m, q+'-found'], df.at[m, q+'-searched']
			fraction_df.at[m, q] = '%s/%s' % (f, s)
	print('\n\nFraction:')
	print(fraction_df)

	percent_df = pd.DataFrame(columns=quarters, index=df.index)
	for q in quarters:
		for m in variable_metrics:
			f, s = df.at[m, q+'-found'], df.at[m, q+'-searched']
			percent_df.at[m, q] = '%.1f%%' % ((100.0 * f / s) if s != 0 else np.nan)
	print('\n\nPercentage:')
	print(percent_df)
			
	sys.exit()
	print(percent_df)
	print(len(percent_df.columns))
	print(len(percent_df.columns) // 2)
	print(len(percent_df.columns) // 2 + 1)
	sys.exit()








	# actual plot

	for i in range(0, len(df.columns), 2):
		print(i, i+1)

	num_stocks           = int(metadata_dct['total_number_of_stocks'])
	quarters             = metadata_dct['quarters_parsed']['quarters']
	earliest_quarter     = quarters[0]
	latest_quarter       = quarters[-1]
	num_quarters         = int(metadata_dct['quarters_parsed']['count'])
	num_variable_metrics = int(metadata_dct['number_of_metrics']['variable'])


	fig, ax = plt.subplots()#figsize=(12, 6.5))
	fig.canvas.manager.set_window_title(CHART_NAMES[0])
	fig.canvas.manager.window.showMaximized() # go fullscreen
	cmap = mcolors.LinearSegmentedColormap.from_list(
		'', ['red', 'orange', 'yellow', 'green'])
	# colormaps: https://matplotlib.org/devdocs/tutorials/colors/colormaps.html#list-colormaps
	norm = mcolors.Normalize(vmin=0, vmax=num_variable_metrics)
	plot = ax.pcolormesh(df, cmap=cmap, norm=norm)
	ax.set_title(
		'Data Coverage of Fundamental Data of %d Variable Metrics over %d Quarters (%.2f Years)' % (
		num_variable_metrics,
		num_quarters,
		(num_quarters / 4)),
		fontsize=14)
	ax.set_ylabel('%d Variable Metrics' % num_variable_metrics)
	ax.set_yticks([])
	ax.set_xlabel('Quarters')
	ax.set_xticks(np.arange(0.5, len(df.columns), 1), df.columns)#, rotation=60) # Code C

	# legend
	# source: https://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
	divider = make_axes_locatable(ax)
	cax = divider.append_axes('right', size='5%', pad=0.10)
	cbar = fig.colorbar(
		plot,
		cax=cax,
		orientation='vertical')
	cbar.ax.set_ylabel('Percent Data Coverage (out of %d variable metrics)' % num_variable_metrics, fontsize=12)
	# tick_locs = np.linspace(0, num_variable_metrics - 1, 5)
	# cbar.set_ticks(tick_locs)
	# cbar.ax.set_yticklabels(['0 %', '25 %', '50 %', '75 %', '100 %'])

	def format_coord(x, y):
		q = quarters[int(x)]
		var_m = df.iloc[int(y)].name
		s1 = 'quarter=%s' % q
		s2 = 'metric=%s' % var_m
		s3 = '%d of %d stocks found this metric' % (
			df.at[var_m, q], num_stocks)
		return '\t'.join([s1, s2, s3])
	ax.format_coord = format_coord

	fig.autofmt_xdate()
	fig.tight_layout()
	plt.show()



''' plot_data_quality_report
	Returns:
		None, it displays a plot showing the quality of the data for each quarter and each stock.
		The plot is a grid with each quarter along the horizontal axis and each stock listed along the vertical axis.
		Each stock has fundamental data for SOME of the quarters. The stocks are sorted by the number of quarters they
		have data for. The stock with data for the most number of quarters is at the top and the stock with data for
		the least number of quarters is at the bottom. For each quarter there are x fundamental data columns a stock
		can have data for. If a stock has data on 100% of its values that cell in the grid is GREEN; if it has 0 that 
		cell is RED, with a gradient inbetween depending on the percentage of data it has.
	Arguments:
		verbose - boolean - print to the console if True
	'''
def plot_data_quality_report(
	chart_name,
	verbose=True,
	num_indents=0,
	new_line_start=False):

	# converts start and end quarters to proper end dates according to Google
	# Proper End Dates:
	# Q1   03/31
	# Q2   06/30
	# Q3   09/30
	# Q4   12/31
	def proper_end_date(date_str):
		y, m, d = tuple(date_str.split('-'))
		if '01-01' <= '-'.join([m, d]) <= '03-31': (m, d) = ('03', '31')
		if '04-01' <= '-'.join([m, d]) <= '06-30': (m, d) = ('06', '30')
		if '07-01' <= '-'.join([m, d]) <= '09-30': (m, d) = ('09', '30')
		if '10-01' <= '-'.join([m, d]) <= '12-31': (m, d) = ('12', '31')
		return '-'.join([y, m, d])
	# gets next proper quarter after date_str
	def next_quarter(date_str):
		y, m, d = tuple(date_str.split('-'))
		if '-'.join([m, d]) == '03-31': return '-'.join([y, '06', '30'])
		if '-'.join([m, d]) == '06-30': return '-'.join([y, '09', '30'])
		if '-'.join([m, d]) == '09-30': return '-'.join([y, '12', '31'])
		if '-'.join([m, d]) == '12-31': return '-'.join([str(int(y)+1), '03', '31'])
	# creates list of proper quarters
	def get_quarters(assets, verbose=True):

		if verbose: print('\nGetting Quarter range ...')

		# create list of all quarters
		# from earliest to latest quarter of all the assets
		earliest_quarter = assets[list(assets.keys())[0]]['Quarter end'].min()
		latest_quarter   = assets[list(assets.keys())[0]]['Quarter end'].max()
		for i, (ticker, df) in enumerate(assets.items()):
			if df.shape[0] == 0: continue
			latest_quarter = df['Quarter end'].iloc[0] \
				if df['Quarter end'].iloc[0] > latest_quarter else \
					latest_quarter
			earliest_quarter = df['Quarter end'].iloc[-1] \
				if df['Quarter end'].iloc[-1] < earliest_quarter else \
					earliest_quarter

		# convert start and end quarters to proper end dates according to Google
		earliest_quarter = proper_end_date(earliest_quarter)
		latest_quarter   = proper_end_date(latest_quarter)

		# create list of all quarters
		quarters = []
		q = earliest_quarter
		while q <= latest_quarter:
			quarters.append(q)
			q = next_quarter(q)
		num_quarters = len(quarters)

		if verbose:
			print('Quarter Range aquired.')
			print('	earliest_quarter = %s' % earliest_quarter)
			print('	latest_quarter   = %s' % latest_quarter)
			print('	covering %d quarters, aka %.2f years\n' % (num_quarters, (num_quarters / 4)))

		return quarters, num_quarters, earliest_quarter, latest_quarter
	# get data coverage percentage each quarter for each asset (in 2D array)
	def calculate_data_coverage(assets, quarters, verbose=True, save=True):

		if verbose:
			print('\nCalculating data coverage for each asset for each quarter ...')
			start_time = datetime.now()
		number_of_cols_in_dfs = set(map(lambda df : df.shape[1], list(assets.values())))
		if len(number_of_cols_in_dfs) != 1:
			print('Not all the CSV files have the same number of columns.')
			print('Number of columns in CSV files:' % number_of_cols_in_dfs)
			print('Aborting creating data quality report.')
			sys.exit()
		x = list(number_of_cols_in_dfs)[0] - 1 # x = total number of fields (minus the "Quarter end" field)
		data_coverage = {}
		bp = BlockPrinter()
		n  = len(assets.keys())
		for i, (ticker, df) in enumerate(assets.items()):
			if verbose:
				bp.print('Ticker %s:\tasset %d out of %d, %.1f %% complete.' % (
					ticker, (i+1), n, 100 * (i+1) / n))
			ticker_data_coverage = []
			number_of_quarters_covered = 0
			ticker_proper_quarters_series = df['Quarter end'].apply(lambda q : proper_end_date(q))
			for q in quarters:
				try:
					j = ticker_proper_quarters_series[ticker_proper_quarters_series == q].index[0]
				except:
					j = None
					number_of_data_points_this_quarter = 0
				if j != None:
					quarter_series = df.iloc[j].drop(labels=['Quarter end'])
					number_of_data_points_this_quarter = \
						quarter_series[quarter_series != 'None'].shape[0]
					number_of_quarters_covered += 1

				ticker_data_coverage.append(number_of_data_points_this_quarter)
			data_coverage[ticker] = (number_of_quarters_covered, ticker_data_coverage)

		# sort them by number_of_quarters_covered
		data_coverage = OrderedDict(sorted(data_coverage.items(), key=lambda x : x[1]))
		data_coverage_2D_array = [ticker_data_coverage for ticker, (number_of_quarters_covered, ticker_data_coverage) in data_coverage.items()]

		if save:
			json.dump(data_coverage, open(PLOT_DATA_PATH, 'w'))

		if verbose:
			end_time = datetime.now()
			print('Calculations complete. Duration: %.1f minutes\n' % ((end_time - start_time).total_seconds() / 60.0))

		return data_coverage, data_coverage_2D_array
	def get_data_coverage_from_file():
		data_coverage          = json.load(open(PLOT_DATA_PATH, 'r'))
		data_coverage_2D_array = [ticker_data_coverage for ticker, (number_of_quarters_covered, ticker_data_coverage) in data_coverage.items()]
		return data_coverage, data_coverage_2D_array


	assets = self.get_data_of_all_assets('local')
	num_assets = len(assets.keys())
	num_metrics = list(assets.values())[0].shape[1]
	cols = list(assets.values())[0].columns
	# print(cols)
	# print(len(cols))

	quarters, num_quarters, earliest_quarter, latest_quarter = \
		get_quarters(assets, verbose=verbose)
	# data_coverage_dct, data_coverage_2D_array = calculate_data_coverage(assets, quarters)
	data_coverage_dct, data_coverage_2D_array = get_data_coverage_from_file()

	# plot the data coverage
	if verbose:
		print('\nPlotting data coverage ...')
	fig, ax = plt.subplots()#figsize=(12, 6.5))
	fig.canvas.set_window_title(self.report_name)
	fig.canvas.manager.window.showMaximized() # go fullscreen
	red_to_green_cmap = mcolors.LinearSegmentedColormap.from_list('', ['red', 'yellow', 'green'])
	# colormaps: https://matplotlib.org/devdocs/tutorials/colors/colormaps.html#list-colormaps
	plot = ax.pcolormesh(data_coverage_2D_array, cmap='RdYlGn')#'RdBu')#red_to_green_cmap)
	ax.set_title(
		'Data Coverage of Fundamental Data of %d Stocks over %d Quarters (%.2f Years)' % (
		num_assets,
		num_quarters,
		(num_quarters / 4)),
		fontsize=14)
	ax.set_ylabel('%d Stocks (sorted from least to most coverage)' % num_assets)
	ax.set_yticks([])
	ax.set_xlabel('Quarters')
	years = sorted(set(map(lambda q : q.split('-')[0], quarters)))
	years_x_loc = []
	for y in years:
		# year x loc goes at beginning of quarter
		quarters_in_year = list(filter(lambda q : q.split('-')[0] == y, quarters))
		q1 = min(quarters_in_year)
		years_x_loc.append(quarters.index(q1))
	mry   = int(latest_quarter.split('-')[0]) # mry = most recent year
	years = list(map(lambda y : y if (mry-int(y))%5==0 else '', years))
	ax.set_xticks(years_x_loc)
	ax.set_xticklabels(years)

	# format labels appear when hoving over a point
	# source: https://stackoverflow.com/questions/7908636/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib
	def format_coord(x, y):
		ticker = list(data_coverage_dct.keys())[int(y)]
		quarter = quarters[int(x)]
		_y, _m, _d = tuple(quarter.split('-'))
		quarter_label = '%s Q%d' % (_y, (int(_m) / 3))
		num_quarters_with_nonzero_coverage = data_coverage_dct[ticker][0]
		quarter_values_with_nonzero_coverage = \
			list(filter(lambda coverage : coverage > 0.0, data_coverage_dct[ticker][1]))
		data_coverage_average_of_all_non_zero_quarters = \
			float(sum(quarter_values_with_nonzero_coverage)) / len(quarter_values_with_nonzero_coverage) \
			if len(quarter_values_with_nonzero_coverage) > 0 else 0.0
		percent_of_quarters_with_nonzero_data_coverage = \
			100.0 * float(num_quarters_with_nonzero_coverage) / num_quarters
		current_quarter_coverage = data_coverage_dct[ticker][1][int(x)]
		current_quarter_coverage_pct = 100 * float(current_quarter_coverage) / num_metrics
		s1 = "Stock %d / %d: %s%s" % (int(y)+1, num_assets, ticker, ' '*(6-len(ticker)))
		s2 = "Quarter: %s, %d / %d fields (%.1f%%) are covered" % (quarter_label, current_quarter_coverage, num_metrics, current_quarter_coverage_pct)
		s3 = "%d / %d quarters (%.1f%%) have data." % (num_quarters_with_nonzero_coverage, num_quarters, percent_of_quarters_with_nonzero_data_coverage)
		s4 = "Data's average coverage: %.1f%%." % (data_coverage_average_of_all_non_zero_quarters)
		return '\t'.join([s1, s2, s3, s4])
	ax.format_coord = format_coord

	# legend
	# source: https://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
	divider = make_axes_locatable(ax)
	cax = divider.append_axes('right', size='5%', pad=0.10)
	tick_locs = np.linspace(0, num_metrics-1, 5) # why there should be -1 idk, but without it the top tick disappears
	cbar = fig.colorbar(
		plot,
		cax=cax,
		orientation='vertical')
	cbar.ax.set_ylabel('Percent Data Coverage (out of %d fields)' % num_metrics, fontsize=12)
	cbar.set_ticks(tick_locs)
	cbar.ax.set_yticklabels(['0 %', '25 %', '50 %', '75 %', '100 %'])


	plt.show()
	if verbose:
		print('Plot complete.\n')



if __name__ == '__main__':
	chart_number = select_chart()
	if chart_number == 1: plot_stock_vs_quarter(num_indents=0)
	if chart_number == 2: plot_metric_vs_quarter(num_indents=0)
	if chart_number == 3: pass
	if chart_number == 4: pass
