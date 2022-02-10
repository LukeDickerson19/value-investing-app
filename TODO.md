# value-investing-bot
bot/ui that collects fundamental data and partially automates the management of a stock portfolio



### To Do:

  - learn to read 10-Q and 10-K forms
```

  check this out, might be useful if i can't parse everything successfully
    http://www.xbrl.org/Specification/XBRL-RECOMMENDATION-2003-12-31+Corrected-Errata-2005-04-25.htm#_4.6.1
    original source: https://stackoverflow.com/questions/14513938/xbrl-us-gaap-contextref-standard

  Metrics the front end plots:

    "Total Liabilities" in 10-Q
      net value of all liabilities (debt, etc.)
        tag: Liabilities

    "Total Assets" in 10-Q
      net value of all assets (money, physical objects they could sell if they had too, etc.)
        tag: Assets

    "Total Cash Inflow"
      use "Total Net Sales" in 10-Q, aka the amount of money made that quarter (from products/services sold)
        tag: RevenueFromContractWithCustomerExcludingAssessedTax
      this excludes other ways the company made money, such as the selling of securities
        not accurate but it should be close enough

        might want to include other ways the company made money, such as realized investments
          does total assets include unrealized investments?

        Total Cash inflow = 
          Total Net Sales
          and then add "Other Income/Expenses, net" if "Other Income/Expenses, net" is positive (aka cash inflow)

      cash flow vs profitability?
        profiatability (aka net profiatability, aka net income) includes agreements of future cash inflow (such as customers paying for a product over time). Cash Flow only looks at the money coming in/out of the business during the time period the submission is covering
      https://www.nav.com/blog/cash-flow-vs-profit-whats-the-difference-92291/

    "Total Cash Outflow"
      amount of money spent that quarter (on paying off debt, on paying employees, ect.), aka cash outflow
        Total Cash Outflow (made up term) = Total Net Sales (in 10-Q) - Net income (in 10-Q)
          not accurate but it should be close enough

        Total Cash Outflow (made up term) should be the sum of:
          Net Income = Operating Income +/- Other Income/Expenses, net - Provision for Income Taxes
            note: "Net Earnings" is synonomous to "Net Income"

          Operating Income = Total Net Sales - (Total Cost of Sales + Total Operating Expenses)

          so
          Net Income =
            Total Net Sales
            - Total Cost of Sales
            - Total Operating Expenses
            +/- Other Income/Expenses, net
            - Provision for Income Taxes

          so for total cash outflow include the following:
            + Total Cost of Sales
            + Total Operating Expenses
            + Other Income/Expenses, net (if its negative, aka cash outflow)
            - Provision for Income Taxes

          should Total Cash Outflow include dividends?
            no, dividends are subtracted from a stocks retained earnings. retained earnings contains both inflows and outflows. Dividends are indeed an outflow of cash from the company so we could either include it in Total Cash Outflow or not. I want to not include it and make it a separate variable because I want to be able to measure the dividends visually on the chart.
              https://www.investopedia.com/ask/answers/090415/are-dividends-considered-expense.asp
              https://www.investopedia.com/terms/r/retainedearnings.asp

    "Total Dividend Payout"
      total amount of money given as dividends
        "Dividends and dividend equivalents declared" (in 10-Q)
      also want to grab "Dividends and dividend equivalents declared per share or RSU"
        tag: CommonStockDividendsPerShareDeclared

    "Total Number Of Shares"
      authorized
        in metric "Shares used in computing earnings per share"
        in table LIABILITIES AND SHAREHOLDERS’ EQUITY
        in 10-Q form
      outstanding
        metric "Diluted" ... "Shares used in computing earnings per share"
        in table CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS
        in 10-Q form
          tag: WeightedAverageNumberOfDilutedSharesOutstanding

      plot this on a graph over time to see how much a company dilutes their shares, see FRONTEND

  possible filters:
    total assets / total liabilities
    determine what this ratio looks like over time for companies that survive a long time
      - Eric Dickerson

      also include this with total assets - total liabilities because

  i dont want to invest in a company where execs take it all for themselves
    "All executive compensation information can be found in public filings with the Securities and Exchange Commission (SEC)."
      - https://www.investopedia.com/articles/stocks/07/executive_compensation.asp

  Questions:

    Answered:

      why is the dividend $0.77 per share on Apple's 2020 Q1 10-Q form?
        why is the dividend on the 10-Q different than the whats on seeking alpha?
          https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019320000052/a10-qq220203282020.htm#s1D43D3A139195BB08634F3B6B1743277
          https://seekingalpha.com/symbol/AAPL/dividends/history

            because there was a stock split Aug 28, 2020. Ctrl + F "Common Stock Split" here
              https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019321000056/aapl-20210327.htm#idad8dee9abea45438a0e024ffb815d1a_13

      is it possible for us (regular investors/people) to view what a public company has in their portfolio, that causes their comprehensive income to fluctuate)?

        See what "Total Assets" is composed of on the balance sheet (aka CONDENSED CONSOLIDATED BALANCE SHEETS)

      why are there 2 columns (sometimes 4 columns) that show different points in time
        with the phrase "Three Months Ended" above it

        ex:
        https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019321000010/aapl-20201226.htm#i61cd8cd699644b40bc5002ed0a038b5a_13

        What is the difference between quarter ended and six months ended on quarterly reports?
          "They both refer to the trailing period of time ending on the dates shown. So, quarter ended would be a quarter of a year, or 3 months from the dates shown. For example, the quarter ended March 28, 2015 would be the time period from December 31, 2014 (or thereabouts) to March 28, 2015. Whereas six months ende d to that date would start September 30, 2014 (or thereabouts), making the period about twice as long - which is why the numbers are about twice as large."
        https://www.quora.com/What-is-the-difference-between-quarter-ended-and-six-months-ended-on-quarterly-reports

        Theres 2 columns for both "Three Months Ended" and "Six Months Ended" instead of 1 coumn because theyre showing the previous year's 3 or 6 month period because they want to show progress or something. Just look at the left column of the 2 for that part you want (thats the most recent column).

      what does "()" mean around a gain/loss?

        "()" usually means a loss, otherwise it'll say it somewhere on the balance sheet

    Unanswered:

      still need to figure out how to get the ex-dividend date, and the pay date

        seeking alpha has it, but id rather get it from the 10-Q
          else ill just use the pandas parse html function and search for the table name
        https://seekingalpha.com/symbol/AAPL/dividends/history

        The ex-dividend date of a stock is the day on which the stock begins trading without the subsequent dividend value. Investors who purchased the stock before the ex-dividend date are entitled to the next dividend payment while those who purchased the stock on the ex-dividend date, or after, are not.

      why are the number of shares outstanding greater than the number of shares issued?

        possible answer:
          "Shares outstanding refer to a company's stock currently held by all its shareholders, including share blocks held by institutional investors and restricted shares owned by the company’s officers and insiders."
            - https://www.investopedia.com/terms/o/outstandingshares.asp

          so how do i calculate the float?
            float = number of shares help by the public
              "To calculate a company's floating stock, subtract its restricted stock and closely held shares from its total number of outstanding shares"
              https://www.investopedia.com/terms/f/floating-stock.asp

        the shares outstanding is on the bottom of the first page of the 10-Q
          however the date is different
          still not sure why the LIABILITIES AND SHAREHOLDERS’ EQUITY section has different numbers but
          if you look at the tag labels of this and this

            https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019321000056/aapl-20210327.htm#idad8dee9abea45438a0e024ffb815d1a_13

            https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019321000010/aapl-20201226.htm#i61cd8cd699644b40bc5002ed0a038b5a_13

            the order  of the tags for "Issued" and "Outstanding" are flip flopped
            also the 2nd number in each of them is the same ... could this be a typo?

            regardless i think it'll just be best to move on and only store
              diluted shares outstanding from the table
                CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS
              and maybe authorized shares from the table
                CONDENSED CONSOLIDATED BALANCE SHEETS

              do i also want the float?
                no because even if a company has a high float they'll still have a bunch of shares authorized but not issued
                also the outstanding shares date is different so it'd just be super hard

      why are the number of shares used to calculate earnings per share different than the number of shares used to calculate?

        this is because the earnings per share uses the "Weighted Average basic shares outstanding" instead of the shares outstanding itself

          on the 10-Q Ctrl + F for "The following table shows the computation of basic and diluted earnings per share"

          Weighted Average of Outstanding Shares
            "To calculate the weighted average of outstanding shares, take the number of outstanding shares and multiply the portion of the reporting period those shares covered; do this for each portion and then add the totals together."
          https://www.investopedia.com/ask/answers/05/weightedoutstandingshares.asp

  write the definitions of each CSV column in a table called fundamental_metrics_definitions
    they're all on stockpup 
    http://www.stockpup.com/data/

  each quarter form is getting the quarter before
    why is the FB 2019 Q4 form getting the 2019 Q3 form?
      "For the quarterly period ended September 30, 2019"
        https://www.sec.gov/Archives/edgar/data/1326801/000132680119000069/fb-09302019x10q.htm#s86440F9012665AA1B578CBCDC37CB566

    list of tickers and CIKs
      contains 12424 tickers
    https://www.sec.gov/include/ticker.txt

  integrate it with apache airflow as a PythonOperator
    it will need to be a function that grabs data as far back into the past as is missing and append it to the database
      like the bitcoin price data collector
      either store the data in a mysql database or csv files
    run it in a docker image

  re-read through stockpup and simfin scrappers
    give them better logs and stuff
    verification:

            Revenue  Cost of Revenue  Total Assets  Total Liabilities
      9734000000.00   -5751000000.00   48140000000        22252000000
      12207000000.00  -7102000000.00   47501000000        15861000000

      48140000000
      22252000000

      9734000000.00
       -5751000000.00
       ______________
        3983000000.00

      ok so it doesn't add up, but its still pretty good
        im not accounting for taxes or shares sold / bought
      lets try stockpup and see what we get
        are the numbers the same as simfin for AAPL for specific quarters?

        2019-03-31 84310000000.00  -52279000000.00  373719000000       255827000000  -3568000000.00
        2019-03-30    97000000.00    2363000000.00  341998000000       236138000000            0.73

        assets and liabilities are about the same, revenue and cost of revenue are vastly different

        use yahoo finance to determine which is right

  use flutter for the front end, i want to be able to view it on my phone and my computer

  Side Experiment:

    What do the fundamentals of companies with no dividend but long term price growth look like in the beginning when they first went public? Is there a consistent pattern in their fundamentals that doesn't exist in the stocks that don't grow?

```


### Column Name
- [ ] Task title ~3d #type @name yyyy-mm-dd  
  - [ ] Sub-task or description  
- Task without checkbox
  - SubTask without checkbox
    - SubSubTask without checkbox

### Completed Column
- [x] Completed task title

