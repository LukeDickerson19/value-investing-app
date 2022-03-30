# value-investing-app
App that collects fundamental data on public companies

### Description
```
Backend script that collects quarterly fundamental data of all the companies that
have submitted filings to the SEC (about 16k companies, going back to 2009 Q1)
along with price data and other metadata (industry, sector, country, company
website, etc.) from the free version of yahoo finance (no api key required). To
see all metrics collected, go to file ./NOTES.txt
and see section: Design > BACKEND > DATABASE > data

Yahoo finance has a rate limit to their API so the script couldn't be parallelized.
They have a bulk request option for price data but not for the metadata (... fuckin
... amateur! right? XD lol) so this program takes like 2 weeks to run (as of 2022),
because each quarter probably takes about 2 days to run. So long as it takes less
time to run then the interval its run on, your're good to go to run it on a schedule.

Its incomplete but in the "./strategy" folder is the beginnings of a program that
would use this data to recommend, or potentially automate the investments of,
companies with a large dividend, a steadily growing dividend, along with steady
growth of stock price, net assets, and net cashflow. The weights of each of the
metrics are in the config file: ./strategy/src/strategy_config.json, the equation
to sort the companies is still tbd.
```

### Setup
```
git clone git@github.com:PopeyedLocket/value-investing-app.git # download repository
cd value-investing-app # enter repository folder
python3 -m venv ./virt_env # create a virtual environment
source ./virt_env/bin/activate # activate virtual environment
pip install -r ./requirements.txt # install all the required libraries
```

### Usage
```
cd value-investing-app # enter repository folder
source ./virt_env/bin/activate # activate virtual environment
python ./database/sec/financial_statements_data_sets/src/driver.py -vlrs # collect data
```