from libraries_and_constants import *



''' TO DO

	dividend dates are fucking up
		its because each row in the dividend df has a date and some stocks have sporadic time intervals between the dates
		one possible solution is to divide the percent change divided by the number of days (to get percent change per day, aka the slope)
		and then use that for velocity
			would that account for if a company skipped it for a long time then paid a big one?

			what am i looking for in a dividend?
				im looking for it to be on regular intervals (weekly, monthly, quarterly, bi-annually, or annually)
					allowing for companies that occationally provide a special dividend
				im looking for it to have fast steady growth as well

	how are price velocity and volitility scores going to be found from the weighted averages?
		answer: all interval values for average velocity and volitility are storedin the
			the df stock_score_df, they are then normalized on a scale of -1 to 1,
			and then the weighted average is taken to find the final value

	make plot show
		for each time interval (on a 2x2 plt grid)
			price over time
			each of the percent changes on this interval
				as a straignt line starting at the price at the beginning of each time interval
			average percent change
				as a straight line from the beginning to the end of the entire plot
			and show the weight for this one in the subplot title
		and also show a similar plot with
			price data
			the weighted average percent change of all the average percent change of each interval 
				as a line from begining to end of the entire price chart

		... how could variance be incorporated into this too?

	maybe make something for acceleration too
		and the variance of the acceleration?
		if its a stable acceleration then its acceleration, not volitility

	idea:
		could the velocity be better calculated by looking at the percent change from the current 
		point in time to each point in the past for a long time interval of 5 to 10 years.
		Weight the long term velocity higher than the short term velocity to get a good picture

			velocity = percent change / window duration in days

			perhaps they could be weighted equally as well? and still favor long term growth?

	'''
''' Description:

	strategy 3:

		for each stock s:
			look at the price data and the dividend history
			price long term slope and volitility
			dividend slope and volitility
			current dividend yield
		record these metrics for each stock
		based on the weights for each metric create a ranking of all the stocks

	seeking
		"fast steady growth
			velocity  = the weighted average percent change in price for multiple time intervals (long term
				weighted stronger) "seeking this value to be high, aka fast"
			volitility = the weighted average variance of each percent change in price (relative to the avg pct
				change used to determine velocity) for multiple time intervals (long term weighted stronger)
				"seeking this value to be low, aka "stable""
			"

		for each time interval i:

			each of the time windows needs to be weighted equally so that stocks with
			consecultive growth in all time scales is prioritized
				infact its probably even better to weight the long term time windows are weighted stronger
				stronger
				than the short term values

		on what time interval though?

		do same thing for dividend and bookvalue
		for dividend make sure it accounts for dividends on variable time values
		for dividend yield im seeking the yield itself to be a high percent value as well
		perhaps with price to book as well (but seeking lower?)
		perhaps for price im seeking the most recent percent change to be down

	run with:

		python driver.py -v

	'''



decimal_to_percent_string = lambda v : '%.3f%%' % (100.0*v)

def get_velocity_and_volitility_of_price(
	daily_price_history,
	verbose=False,
	num_indents=0,
	new_line_start=False,
	show_plots=False):

	# metrics = strategy_config['metrics']
	# use_window_width = strategy3['use_window_width']
	time_interval_weights = strategy_config['time_interval_weights']
	score_data = {'velocity' : {}, 'volitility' : {}}
	num_intervals = len(time_interval_weights.keys())
	if verbose:
		log.print('price data:', num_indents=num_indents, new_line_start=new_line_start)
		log.print('calculating average velocity and deviation of data using %d time interval(s):' % num_intervals,
			num_indents=num_indents+1)
	for i, (interval, weight) in enumerate(time_interval_weights.items()):
		data = get_data_on_interval(daily_price_history.copy(), interval)
		if strategy_config['use_window_width']:
			data = data.iloc[-(strategy_config['window_width'] +1):] # +1 because pct_change() has a nan at the beginning
		pct_changes = data['Close'].pct_change()
		pct_changes = pd.DataFrame({
			'Date'    : data['Date'],
			'decimal' : pct_changes,
			'percent' : pct_changes.apply(decimal_to_percent_string)}).iloc[1:]
		average_velocity = pct_changes['decimal'].mean() # non weighted
		deviations = pct_changes['decimal'].apply(lambda v : abs(v - average_velocity))
		average_deviation = deviations.sum() / pct_changes.shape[0] # non weighted
		if verbose:
			log.print('interval %d of %d: \"%s\"' % (
				i+1, num_intervals, interval),
				num_indents=num_indents+2)
			log.print('weight:      %.1f %%' % (
				100.0*weight),
				num_indents=num_indents+3)
			log.print('time_window: %s' % (
				'all time' if not strategy_config['use_window_width'] else (
					'past %d %s(s)' % (strategy_config['window_width'], interval))),
				num_indents=num_indents+3)
			log.print('data:', num_indents=num_indents+3)
			log.print(data.to_string(max_rows=6), num_indents=num_indents+4)
			log.print('pct_changes:', num_indents=num_indents+3)
			log.print(pct_changes.to_string(max_rows=6), num_indents=num_indents+4)
			log.print('average_velocity:', num_indents=num_indents+3)
			log.print('decimal: %s' % average_velocity, num_indents=num_indents+4)
			log.print('percent: %s' % decimal_to_percent_string(average_velocity),
				num_indents=num_indents+4)
			log.print('average_deviation', num_indents=num_indents+3)
			log.print('decimal: %s' % average_deviation, num_indents=num_indents+4)
			log.print('percent: %s' % decimal_to_percent_string(average_deviation),
				num_indents=num_indents+4)
		score_data['velocity'][interval]   = average_velocity
		score_data['volitility'][interval] = average_deviation
	if verbose:
		# log.print('values and weighted average of each time intervals\' average velocity and deviation:',
		log.print('values of each time intervals\' average velocity and deviation:',
			num_indents=num_indents+1)
		score_data_percent = {}
		for k, v in score_data.items():
			score_data_percent[k] = {}
			for interval, value in v.items():
				score_data_percent[k][interval] = decimal_to_percent_string(value)
		log.print(json.dumps(score_data_percent, indent=4), num_indents=num_indents+2)
	return score_data
def get_data_on_interval(
	df,
	interval):

	most_recent_date_str = df['Date'].iloc[-1]
	most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
	if interval == 'day':
		pass
	elif interval == 'week':
		df['datetime'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
		df['weekday'] = df['datetime'].dt.weekday
		df = df[df['weekday'] == most_recent_date.weekday()].copy()
		df.drop(columns=['datetime', 'weekday'], inplace=True)
	elif interval == 'month':
		df = closest_month_day(df, most_recent_date)
	elif interval == 'year':
		df = closest_year_day(df, most_recent_date)
	return df
def closest_month_day(df, most_recent_date):
	# this function will get a value for each month in the data thats closest to the current day of the month of today
	# this is required because the data is often not on daily intervals (ex: price data is only on workdays)
	df2 = pd.DataFrame(columns=df.columns)
	years = list(set(map(lambda d : d[:4], df['Date'].tolist())))
	years.sort()
	for y in years:
		df_of_y = df[df['Date'].str[:4] == y]
		months = list(set(map(lambda d : d[5:7], df_of_y['Date'].tolist())))
		months.sort()
		for m in months:
			df_of_m = df[df['Date'].str[:7] == '%s-%s' % (y, m)]
			current_day = datetime(int(y), int(m), most_recent_date.day)
			i = 1
			max_i = 4 # only add a row for this month if it has data thats within max_i of the current day, this is only used on the first month/year
			b = True
			while True:

				# days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
				# print(days[current_day.weekday()], current_day.strftime('%Y-%m-%d'))
				x = df_of_m[df_of_m['Date'] == current_day.strftime('%Y-%m-%d')]
				# print(x)
				# input()

				if not x.empty:
					df2 = df2.append(x)
					break
				else:
					current_day += timedelta(days=((1 if b else -1) * i))
					b = not b
					i += 1
					if i > max_i: break
	return df2
def closest_year_day(df, most_recent_date):
	# this function will get a value for each year in the data thats closest to the current day and month of today
	# this is required because the data is often not on daily intervals (ex: price data is only on workdays)
	df2 = pd.DataFrame(columns=df.columns)
	years = list(set(map(lambda d : d[:4], df['Date'].tolist())))
	years.sort()
	for y in years:
		df_of_y = df[df['Date'].str[:4] == y]
		current_day = datetime(int(y), most_recent_date.month, most_recent_date.day)
		i = 1
		max_i = 4 # only add a row for this year if it has data thats within max_i of the current month and day, this is only used on the first year
		b = True
		while True:

			# days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			# print(days[current_day.weekday()], current_day.strftime('%Y-%m-%d'))
			x = df_of_y[df_of_y['Date'] == current_day.strftime('%Y-%m-%d')]
			# print(x)
			# input()

			if not x.empty:
				df2 = df2.append(x)
				break
			else:
				current_day += timedelta(days=((1 if b else -1) * i))
				b = not b
				i += 1
				if i > max_i: break
	return df2

def get_velocity_and_volitility_of_dividend(
	dividend_per_share_history,
	verbose=False,
	num_indents=0,
	new_line_start=False,
	show_plots=False):

	# metrics = strategy_config['metrics']
	# use_window_width = strategy3['use_window_width']
	time_interval_weights = strategy_config['time_interval_weights']
	score_data = {'velocity' : {}, 'volitility' : {}}
	num_intervals = len(time_interval_weights.keys())
	if verbose:
		log.print('dividend data:',
			num_indents=num_indents,
			new_line_start=new_line_start)
		log.print('calculating average velocity and deviation of data using %d time interval(s):' % num_intervals,
			num_indents=num_indents+1)
	for i, (interval, weight) in enumerate(time_interval_weights.items()):
		data = get_data_on_interval(dividend_per_share_history.copy(), interval)
		if strategy_config['use_window_width']:
			data = data.iloc[-(strategy_config['window_width'] +1):] # +1 because pct_change() has a nan at the beginning
		pct_changes = data['Close'].pct_change()
		pct_changes = pd.DataFrame({
			'Date'    : data['Date'],
			'decimal' : pct_changes,
			'percent' : pct_changes.apply(decimal_to_percent_string)}).iloc[1:]
		average_velocity = pct_changes['decimal'].mean() # non weighted
		deviations = pct_changes['decimal'].apply(lambda v : abs(v - average_velocity))
		average_deviation = deviations.sum() / pct_changes.shape[0] # non weighted
		if verbose:
			log.print('interval %d of %d: \"%s\"' % (
				i+1, num_intervals, interval),
				num_indents=num_indents+2)
			log.print('weight:      %.1f %%' % (
				100.0*weight),
				num_indents=num_indents+3)
			log.print('time_window: %s' % (
				'all time' if not strategy_config['use_window_width'] else (
					'past %d %s(s)' % (strategy_config['window_width'], interval))),
				num_indents=num_indents+3)
			log.print('data:', num_indents=num_indents+3)
			log.print(data.to_string(max_rows=6), num_indents=num_indents+4)
			log.print('pct_changes:', num_indents=num_indents+3)
			log.print(pct_changes.to_string(max_rows=6), num_indents=num_indents+4)
			log.print('average_velocity:', num_indents=num_indents+3)
			log.print('decimal: %s' % average_velocity, num_indents=num_indents+4)
			log.print('percent: %s' % decimal_to_percent_string(average_velocity),
				num_indents=num_indents+4)
			log.print('average_deviation', num_indents=num_indents+3)
			log.print('decimal: %s' % average_deviation, num_indents=num_indents+4)
			log.print('percent: %s' % decimal_to_percent_string(average_deviation),
				num_indents=num_indents+4)
		score_data['velocity'][interval]   = average_velocity
		score_data['volitility'][interval] = average_deviation
	if verbose:
		# log.print('values and weighted average of each time intervals\' average velocity and deviation:',
		log.print('values of each time intervals\' average velocity and deviation:',
			num_indents=num_indents+1)
		score_data_percent = {}
		for k, v in score_data.items():
			score_data_percent[k] = {}
			for interval, value in v.items():
				score_data_percent[k][interval] = decimal_to_percent_string(value)
		log.print(json.dumps(score_data_percent, indent=4), num_indents=num_indents+2)
	return score_data

def get_book_value_history(df):

	return df


####################### unused, old strategies ###########################

def get_quadratic_slope_and_volitility(x, x_labels, y, ticker, show_plots=False):

	# line of best fit: i want the line of best fit to be either linear, or curving at most 1 time
	# no "s" shaped lines with 2 curves or squiggly shaped lines with more than 2 curves.
	# So using a quadratic equation
	# https://www.statology.org/quadratic-regression-python/
	coefficients = np.polyfit(x, y, 2)
	# print(coefficients)
	model = np.poly1d(coefficients)
	line_of_best_fit = model(x)

	# price slope: the slope of the line of best fit at this current point in time
	slope = 'tbd'

	# price volitility: the (sum from t=0 to t_max of the absolute value of the percent change between the
	# price at time t and the value of the line of best fit at time t) / number of timesteps
	volitility = sum([abs((y[t] - line_of_best_fit[t]) / y[t]) for t in x]) / float(len(x))

	if show_plots:
		s = str(model).split('\n')[-1].split('x')
		s[0], s[1] = s[0][0:-2]+'*', '^2'+s[1][0:-2]+'*'
		equation_str = 'x'.join(s)
		fig, ax = plt.subplots()
		ax.plot(x, y, c='b')
		ax.plot(x, line_of_best_fit, c='r')
		ax.set_title('ticker: %s\nline_of_best_fit: %s\nvolitility: %s' % (
			ticker, equation_str, volitility))

		ax.set_xlabel('Quarters')
		num_labels_to_display   = 5
		label_x_loc_to_display  = np.linspace(
			x[0], x[-1], num_labels_to_display).astype(int)
		labels_to_display = [x_labels[t] for t in label_x_loc_to_display]
		ax.set_xticks(label_x_loc_to_display)
		# https://stackoverflow.com/questions/14852821/aligning-rotated-xticklabels-with-their-respective-xticks
		ax.set_xticklabels(labels_to_display, rotation=45, ha='right', rotation_mode='anchor')
		fig.tight_layout()
		plt.show()

	return slope, volitility
def get_sma_slope_and_std_dev(x, x_labels, y, ticker, show_plots=False, period=200):

	# line of best fit: i want the line of best fit to be the SMA (simple moving average)
	# using a default trailing window of 200 days
	# line_of_best_fit = pd.Series(y).rolling(period).mean()
	line_of_best_fit = []
	for t in range(len(x)):
		# print(y[:t+1])
		# input()
		s, tot_w = 0, 0
		for w in range(1, t+1):
			s += y[w-1]*w*w
			tot_w += w*w
		p = s / (tot_w if tot_w != 0 else 1)
		line_of_best_fit.append(p)
	# print(line_of_best_fit)
	line_of_best_fit = pd.Series(line_of_best_fit)
	# price slope: the slope of the line of best fit at this current point in time
	slope = (line_of_best_fit.values[-1] - line_of_best_fit.values[-2]) / line_of_best_fit.values[-2]
	# slope = pd.Series(np.gradient(line_of_best_fit), line_of_best_fit.index, name='slope')

	# price volitility: the std deviation of the price around the line of best fit (using the same trailing window)
	volitility_series = pd.Series(y).rolling(period).std()
	volitility = volitility_series.values[-1] / line_of_best_fit.values[-1]

	# print(slope)
	# print(volitility)
	# sys.exit()

	if show_plots:
		fig, ax = plt.subplots()
		ax.plot(x, y, c='b')
		ax.plot(x, line_of_best_fit, c='r')
		# ax.plot(x, volitility_series, c='g')
		# ax.plot(x, line_of_best_fit + volitility_series, c='g')
		# ax.plot(x, line_of_best_fit - volitility_series, c='g')
		ax.set_title('ticker: %s' % (ticker))

		ax.set_xlabel('Quarters')
		num_labels_to_display   = 5
		label_x_loc_to_display  = np.linspace(
			x[0], x[-1], num_labels_to_display).astype(int)
		labels_to_display = [x_labels[t] for t in label_x_loc_to_display]
		ax.set_xticks(label_x_loc_to_display)
		# https://stackoverflow.com/questions/14852821/aligning-rotated-xticklabels-with-their-respective-xticks
		ax.set_xticklabels(labels_to_display, rotation=45, ha='right', rotation_mode='anchor')
		fig.tight_layout()
		plt.show()

	return slope, volitility	

def get_price_stats(df, ticker, verbose=False, show_plots=False):
	if verbose:
		log.print('daily_price_data:', num_indents=1, new_line_start=True)
		log.print(df.to_string(max_rows=6), num_indents=1)
	time_span = df.index.tolist()
	dates     = df['Date'].tolist()
	prices    = df['Close'].tolist()
	# price_slope, price_volitility = get_slope_and_volitility1(
	# 	time_span, dates, prices, ticker, show_plots=show_plots)
	price_slope, price_volitility = get_sma_slope_and_std_dev(
		time_span, dates, prices, ticker, show_plots=show_plots, period=200)
	return price_slope, price_volitility
def get_dividend_stats(df, ticker, verbose=False, show_plots=False):
	if verbose:
		log.print('dividend_per_share_history:', num_indents=1, new_line_start=True)
		log.print(df.to_string(max_rows=6), num_indents=1)
	time_span = df.index.tolist()
	dates     = df['Date'].tolist()
	dividends = df['Dividends'].tolist()
	# dividend_slope, dividend_volitility = get_slope_and_volitility1(
	# 	time_span, dates, dividends, ticker, show_plots=show_plots)
	dividend_slope, dividend_volitility = get_sma_slope_and_std_dev(
		time_span, dates, dividends, ticker, show_plots=show_plots, period=200)
	return dividend_slope, dividend_volitility

###########################################################################



if __name__ == '__main__':

	# put args in their own variable
	verbose = args.verbose
	show_plots = args.plot

	# init stock_score_df columns
	metric_score_columns = []
	for k, v in strategy_config['metrics'].items():
		for k2 in v.keys():
			if k2 != 'metric_weight':
				k2 = k2.replace('_weight', '')
				if k2 in ['velocity', 'volitility']:
					for interval in strategy_config['time_interval_weights']:
						metric_score_columns.append(k+'_'+k2+'-'+interval)
				else:
					metric_score_columns.append(k+'_'+k2)
	stock_score_df = pd.DataFrame(columns=metric_score_columns+['final_score'])
	# for c in stock_score_df.columns: print(c)
	# # print(stock_score_df)
	# sys.exit()

	ciks = os.listdir(DATA_STOCKS_PATH)
	num_ciks = len(ciks)
	if verbose:
		log.print('iterating over %d stocks (SEC CIKs):' % num_ciks,
			num_indents=0, new_line_start=True)
	i = 0
	for cik in ciks:

		cik_path = os.path.join(DATA_STOCKS_PATH, cik)
		with open(os.path.join(cik_path, 'info.json')) as f:
			info = json.load(f)
		ticker = info['ticker']
		daily_price_history = pd.read_csv(os.path.join(cik_path, 'daily_price_data.csv'))
		dividend_per_share_history = pd.read_csv(os.path.join(cik_path, 'dividend_per_share_history.csv'))
		fundamental_history = pd.read_csv(os.path.join(cik_path, 'fundamentals.csv'))
		if ticker == None or \
			daily_price_history.shape[0] in [0, 1] or \
			dividend_per_share_history.shape[0] in [0, 1] or \
			fundamental_history.shape[0] in [0, 1]:
			continue
		else:
			i += 1
		if verbose:
			log.print('cik %d of %d: %s' % (i, num_ciks, cik),
				num_indents=1, new_line_start=True)
			repo_cik_path = cik_path[cik_path.index('value-investing-app'):]
			log.print(repo_cik_path, num_indents=2)
		price_score_data = get_velocity_and_volitility_of_price(
			daily_price_history,
			verbose=verbose,
			num_indents=3,
			new_line_start=True,
			show_plots=show_plots)
		dividend_score_data = get_velocity_and_volitility_of_dividend(
			dividend_per_share_history,
			verbose=verbose,
			num_indents=2,
			new_line_start=True,
			show_plots=show_plots)
		# book_value_history = get_book_value_history(fundamental_history)
		# book_value_score_data = get_velocity_and_volitility(
		# 	book_value_history, "Book Value",
		# 	verbose=verbose,
		# 	num_indents=2,
		# 	new_line_start=True,
		# 	show_plots=show_plots)
		# current_dividend_yield = ...
		stock_score_df = stock_score_df.append(pd.DataFrame({
			'dividend_yield_value'                : 'tbd',
			'dividend_per_share_velocity-day'     : 'tbd',
			'dividend_per_share_velocity-week'    : 'tbd',
			'dividend_per_share_velocity-month'   : 'tbd',
			'dividend_per_share_velocity-year'    : 'tbd',
			'dividend_per_share_volitility-day'   : 'tbd',
			'dividend_per_share_volitility-week'  : 'tbd',
			'dividend_per_share_volitility-month' : 'tbd',
			'dividend_per_share_volitility-year'  : 'tbd',
			'price_velocity-day'                  : price_score_data['velocity']['day'],
			'price_velocity-week'                 : price_score_data['velocity']['week'],
			'price_velocity-month'                : price_score_data['velocity']['month'],
			'price_velocity-year'                 : price_score_data['velocity']['year'],
			'price_volitility-day'                : price_score_data['volitility']['day'],
			'price_volitility-week'               : price_score_data['volitility']['week'],
			'price_volitility-month'              : price_score_data['volitility']['month'],
			'price_volitility-year'               : price_score_data['volitility']['year'],
			'book_value_velocity-day'             : 'tbd',
			'book_value_velocity-week'            : 'tbd',
			'book_value_velocity-month'           : 'tbd',
			'book_value_velocity-year'            : 'tbd',
			'book_value_volitility-day'           : 'tbd',
			'book_value_volitility-week'          : 'tbd',
			'book_value_volitility-month'         : 'tbd',
			'book_value_volitility-year'          : 'tbd',
			'final_score'                         : 'tbd'
		}, index=[cik]))
		if verbose:
			log.print('stock_score_df.loc[cik] = ', num_indents=2, new_line_start=True)
			log.print(stock_score_df.loc[cik].to_string(), num_indents=3)

		input() # for testing purposes only
		if i > 5: break # for testing purposes only

	# normalize data (chose the "maximum absolute scaling" method)
	# https://www.geeksforgeeks.org/normalize-a-column-in-pandas/
	for k, v in strategy_config['metrics'].items():
		for k2, w in v.items():
			if k2 != 'metric_weight':
				k2 = k2.replace('_weight', '')
				if k2 in ['velocity', 'volitility']:
					for interval in strategy_config['time_interval_weights']:
						column = k+'_'+k2+'-'+interval
						stock_score_df[column].normalize()
						stock_score_df[column] = \
							stock_score_df[column] / stock_score_df[column].abs().max()
				else:
					column = k+'_'+k2
					stock_score_df[column] = \
						stock_score_df[column] / stock_score_df[column].abs().max()

	# calculate weighted averages (in a new df)
	# tbd

	# calculate final scores
	# tbd

	# save to csv file
	df.to_csv(stock_score_df)


