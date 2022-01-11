# value-investing-bot
bot/ui that collects fundamental data and partially automates the management of a stock portfolio




### To Do:

  - learn to read 10-Q and 10-K forms
```

  try to use yahoo finance instead

    see function "get_ticker_by_isin" in utils file of yfinance
      i think it could get ALL the tickers on yahoo finance

    figure out API stuff
      how is yfinance using the yahoo finance API?
      how can i still use yfinance but use my API key?
      why are my API calls in yf_api.py not appearing on the dashboard
        https://www.yahoofinanceapi.com/dashboard

    it will be way easier to get the data I want than parsing SEC filings
    setup the code to find all the tickers from the SEC
    then set up the yahoo finance calls on this list of tickers (calling it from the json)
      libs
        yfinance
          https://pypi.org/project/yfinance/
          https://github.com/ranaroussi/yfinance
          https://analyticsindiamag.com/top-python-libraries-to-get-historical-stock-data-with-code/
          https://algotrading101.com/learn/yahoo-finance-api-guide/
          https://aroussi.com/post/python-yahoo-finance
        yahoo_fin
          http://theautomatic.net/yahoo_fin-documentation/#stock_info
          http://theautomatic.net/2020/05/05/how-to-download-fundamentals-data-with-python/
          https://algotrading101.com/learn/yahoo-finance-api-guide/
    then set up the code to save the data
      save the raw data and also the parsed data to different databases
    then get the Yahoo Finance Essentials Plus 14 day free trial
      and see if you can get data for each of the tickers for each quarter in the list
      https://finance.yahoo.com/quote/NFLX/financials?p=NFLX
      https://www.yahoo.com/plus/finance?ncid=dcm_306158723_490172245_127172993
      i still need to figure out how im going to make api calls using Yahoo Finance Essentials Plus
        how will the server know its me? does yfinance lib have anything I could use to specify its me
        at the very least i can just iterate over the tickers and 
      other libs
        https://github.com/janlukasschroeder/sec-api
    run it on your raspi and save the data on your external hard drive

  i dont want to invest in a company where execs take it all for themselves
    "All executive compensation information can be found in public filings with the Securities and Exchange Commission (SEC)."
      - https://www.investopedia.com/articles/stocks/07/executive_compensation.asp

  parse 10-Ks

  daily price data
    then compare the total number of tickers the exchange has to the number of tickers that submitted a filing this most recent quarter
    I want the program to get the most current price owned, and get the price of all the days from then until the current day. this way the get_daily_price_data function (or whatever its called) can be run on daily intervals or quarterly intervals.
    I want the exchange to provide trading stocks and via an API and with zero trading fee.
    the price is going to be collected on quarterly intervals

    using this API wrapper for yahoo finance
    https://pypi.org/project/yfinance/

    yahoo finance has free historical daily price data for global stocks
    https://help.yahoo.com/kb/SLN2310.html

    historical fundamentals back to a company's IPO requires payment though
      https://finance.yahoo.com/quote/NFLX/financials?p=NFLX
        theres a 14 day free trial though, i might be able to get all the data i need without paying for it then run the program for current data and be fine so long as the program continued to run
        if i were to do this i'd need a list of all tickers of current public companies
          i think ill just use the SEC tickers
      https://www.yahoo.com/plus/finance?ncid=dcm_311080551_490172245_127172993

    it seems to have stock split and dividend per share history all the way back though
      ex: MSFT

  interactive brokers
    https://www.reddit.com/r/algotrading/comments/mkthpv/ib_apis_pricing_and_some_questions/
    https://interactivebrokers.github.io/tws-api/initial_setup.html#enable_api
    https://www.interactivebrokers.com/en/index.php?f=4969
    https://algotrading101.com/learn/ib_insync-interactive-brokers-api-guide/#why-shouldn't-i-use-ib-insync
    https://www.interactivebrokers.com/en/trading/ib-api.php

  write the code to store the data
    use a mysql database because it'll make integrating into airflow involve using the MySQLOperator
      mysql is in general about just as fast as csv
      https://stackoverflow.com/questions/561058/csv-vs-mysql-performance
      https://www.quora.com/What-makes-SQL-faster-than-just-reading-through-a-CSV-file-using-a-language-like-Python-or-Java

      you can set the mysql data dir in your docker image
      https://stackoverflow.com/questions/6754944/where-is-my-database-saved-when-i-create-it-in-mysql
    see the DESIGN section for database tables and columns

  determine the data coverage for each data source individually and also collectively:
    [10-Q, 10-K, Finanical Statements Data Set]
    
    make df with a column for each variable gathered
    and a row for each quarter
    each value will be a fraction

  check this out, might be useful if i can't parse everything successfully
    http://www.xbrl.org/Specification/XBRL-RECOMMENDATION-2003-12-31+Corrected-Errata-2005-04-25.htm#_4.6.1
    original source: https://stackoverflow.com/questions/14513938/xbrl-us-gaap-contextref-standard

  data sources:

    10-Q

      CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS
        Total Net Sales
        Total Cost of Sales
        Total Operating Expenses
        Operating Income = Total Net Sales - Total Cost of Sales - Total Operating Expenses
        Other Income/Expenses, net
        Provision for Income Taxes
        Net Income = Operating Income +/- Other Income/Expenses, net - Provision for Income Taxes
          note: "Net Earnings" is synonomous to "Net Income"
        Earnings per share = Net Income / (number of shares (basic or diluted))
          Basic
          Diluted
        Shares used in computing earnings per share:
          Basic
          Diluted

          note:
            What is the difference between basic shares and fully diluted shares?
              "Basic shares represent the number of common shares that are outstanding today (or as of the reporting date).  Fully diluted shares equals basic shares plus the potentially dilutive effect from any outstanding stock options, warrants, convertible preferred stock or convertible debt.  In calculating a company’s market value of equity (MVE) we always want to use diluted shares.  Implicitly the market also uses diluted shares to value a company’s stock."
            https://ibankingfaq.com/interviewing-technical-questions/enterprise-value-and-equity-value/what-is-the-difference-between-basic-share-and-fully-diluted-shares/

            "Diluted" vs. "Basic"
              "In financial statements, you'll often see references to "diluted" and "basic" earnings per share. What's the difference? Well, it reflects some interesting changes in how companies report their earnings. At the end of 1997, a new rule went into effect, instituted by the Financial Accounting Standards Board. It required companies to report their quarterly earnings per share in two ways: basic and diluted.

              This is important stuff for investors to understand, since corporate per-share profits are, in many ways, at the core of all things financial. Per-share profits show investors their share of a company's total profits. Fools should pay attention to the diluted numbers, not the basic ones.

              Basic EPS is net income, less any preferred-stock dividends, divided by the weighted average number of common stock shares outstanding during the reporting period. Diluted EPS also takes into account stock options, warrants, preferred stock, and convertible debt securities, all of which can be converted into common stock. These common-stock equivalents represent the potential claims of other owners on earnings and show investors how much of the company's earnings they're entitled to, at a minimum."
            https://www.fool.com/investing/value/2006/04/24/quotdilutedquot-vs-quotbasicquot.aspx

      CONDENSED CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME

        Total comprehensive income = Net income - Total other comprehensive income/(loss)
          note:
            Comprehensive Income
              "Comprehensive income includes net income AND unrealized income, such as unrealized gains or losses on hedge/derivative financial instruments and foreign currency transaction gains or losses."
            https://www.investopedia.com/terms/c/comprehensiveincome.asp

            Net Income Vs. Comprehensive Income

              "Businesses use up economic resources called assets to start up, maintain and run their operations. Assets can be acquired in one of two methods -- either through incurring economic obligations called liabilities to other entities or through receiving them as investments from business owners. This investment is called equity or net assets since assets minus liabilities is equal to equity. Net income is the financial gain or loss that a business has made in one single time period while comprehensive income is the change in equity in that same time period originating in non-owner sources.

              In general, revenues and expenses are recorded on the accounts when the transactions are both realized and collectible. Collectible means that the sums, if owing, can expect to be collected while realized means that the source transaction has been completed. Certain transactions produce unrealized gains and losses that do not appear as either revenues or expenses but are recorded as changes in equity.

              Net income or net loss is equal to the sum of all revenues in the period minus the sum of all expenses in the period. If revenues exceed expenses, it is a net income and vice versa. Net income and net loss represent the change in the business's financial circumstances because of it running its revenue-producing operations for the period.

              Comprehensive income is equal to net income plus other comprehensive income. Other comprehensive income is a catch-all term for changes in equity from non-owner sources, including unrealized gains and losses on investments because of changing market prices, on foreign exchange fluctuations, and the like. Because of the volatile nature of these items, comprehensive income is more susceptible to change than net income."

            https://bizfluent.com/info-8754360-net-income-vs-comprehensive-income.html

      CONDENSED CONSOLIDATED BALANCE SHEETS

        ASSETS:
          Total current assets (sum of the below assets)
            Cash and cash equivalents
              note:
                Cash And Cash Equivalents (CCE)
                  "Cash and cash equivalents refers to the line item on the balance sheet that reports the value of a company's assets that are cash or can be converted into cash immediately. Cash equivalents include bank accounts and marketable securities, which are debt securities with maturities of less than 90 days. However, oftentimes cash equivalents do not include equity or stock holdings because they can fluctuate in value."
                https://www.investopedia.com/terms/c/cashandcashequivalents.asp
            Marketable securities
              note:
                Common Examples of Marketable Securities
                  "Marketable securities are investments that can easily be bought, sold, or traded on public exchanges. The high liquidity of marketable securities makes them very popular among individual and institutional investors. These types of investments can be debt securities or equity securities."
                https://www.investopedia.com/ask/answers/033015/what-are-some-common-examples-marketable-securities.asp
            Accounts receivable, net
              note:
                Net Receivables
                  "Net receivables are the total money owed to a company by its customers minus the money owed that will likely never be paid. Net receivables are often expressed as a percentage, and a higher percentage indicates a business has a greater ability to collect from its customers."
                https://www.investopedia.com/terms/n/netreceivables.asp
            Inventories
              note:
                Is Inventory a Current Asset?
                  "Inventory is a current asset when the business intends to sell them within the next accounting period or within twelve months from the day it’s listed in the balance sheet." ... "Inventory is goods and items of value that a business holds and plans to sell for profit. This includes merchandise, raw materials, work-in-progress and finished products."
                https://www.freshbooks.com/hub/accounting/is-inventory-current-asset
            Vendor non-trade receivables
              note:
                Non trade receivables definition
                  "Non trade receivables are amounts due for payment to an entity other than its normal customer invoices for merchandise shipped or services performed. Examples of non trade receivables are amounts owed to a company by its employees for loans or wage advances, tax refunds owed to it by taxing authorities, or insurance claims owed to it by an insurance company."
                https://www.accountingtools.com/articles/what-are-non-trade-receivables.html
            Other current assets
              note:
                Other Current Assets (OCA)
                  "Other current assets (OCA) is a category of things of value that a company owns, benefits from, or uses to generate income that can be converted into cash within one business cycle. They are referred to as “other” because they are uncommon or insignificant, unlike typical current asset items such as cash, securities, accounts receivable, inventory, and prepaid expenses."
                https://www.investopedia.com/terms/o/othercurrentassets.asp
          Total non-current assets (sum of the below assets)
            Marketable securities
              note:
                same definition as "Marketable securities" in "Total current assets"
            Property, plant and equipment, net
              note:
                Property, Plant, and Equipment (PP&E)
                  "Property, plant, and equipment (PP&E) are long-term assets vital to business operations. Property, plant, and equipment are tangible assets, meaning they are physical in nature or can be touched; as a result, they are not easily converted into cash."
                https://www.investopedia.com/terms/p/ppe.asp
            Other non-current assets
              note:
                same definition as "Other current assets" in "Total current assets"
          Total Assets = Total current assets + Total non-current assets
            note:
              Current Assets vs. Noncurrent Assets: What's the Difference?
                "Current assets are assets that are expected to be converted to cash within a year. Noncurrent assets are those that are considered long-term, where their full value won't be recognized until at least a year."
              https://www.investopedia.com/ask/answers/030215/what-difference-between-current-assets-and-noncurrent-assets.asp

        LIABILITIES AND SHAREHOLDERS’ EQUITY:

          Total current liabilities (sum of the below liabilities)
            Accounts payable
              note:
                Accounts Payable (AP)
                  "Accounts payable (AP) are amounts due to vendors or suppliers for goods or services received that have not yet been paid for." ... (aka) ... ""Accounts payable" (AP) refers to an account within the general ledger that represents a company's obligation to pay off a short-term debt to its creditors or suppliers."
                https://www.investopedia.com/terms/a/accountspayable.asp
            Other current liabilities
              note:
                Other Current Liabilities
                  "Other current liabilities, in financial accounting, are categories of short-term debt that are lumped together on the liabilities side of the balance sheet. The term "current liabilities" refers to items of short-term debt that a firm must pay within 12 months. To that, companies add the word "other" to describe those current liabilities that are not significant enough to identify separately on their own lines in financial statements, so they are grouped together as "other current liabilities.""
                https://www.investopedia.com/terms/o/othercurrentliabilities.asp
            Deferred revenue
              note:
                Deferred Revenue
                  "Deferred revenue, also known as unearned revenue, refers to advance payments a company receives for products or services that are to be delivered or performed in the future. The company that receives the prepayment records the amount as deferred revenue, a liability, on its balance sheet.

                  Deferred revenue is a liability because it reflects revenue that has not been earned and represents products or services that are owed to a customer. As the product or service is delivered over time, it is recognized proportionally as revenue on the income statement."
                https://www.investopedia.com/terms/d/deferredrevenue.asp
            Commercial paper and repurchase agreement
              note:
                Repurchase Agreement (Repo)
                  " A repurchase agreement (repo) is a form of short-term borrowing for dealers in government securities. In the case of a repo, a dealer sells government securities to investors, usually on an overnight basis, and buys them back the following day at a slightly higher price. That small difference in price is the implicit overnight interest rate. Repos are typically used to raise short-term capital. They are also a common tool of central bank open market operations.

                  For the party selling the security and agreeing to repurchase it in the future, it is a repo; for the party on the other end of the transaction, buying the security and agreeing to sell in the future, it is a reverse repurchase agreement."
                https://www.investopedia.com/terms/r/repurchaseagreement.asp
            Term debt
              note:
                Current portion of long-term debt (CPLTD) 
                  "The current portion of long-term debt (CPLTD) is the amount of unpaid principal from long-term debt that has accrued in a company’s normal operating cycle (typically less than 12 months). It is considered a current liability because it has to be paid within that period."
                https://www.bdc.ca/en/articles-tools/entrepreneur-toolkit/templates-business-guides/glossary/current-portion-of-long-term-debt
          Total non-current liabilities (sum of the below liabilities)
            Term debt
              note:
                Long-Term Debt
                  "Long-term debt is debt that matures in more than one year. Long-term debt can be viewed from two perspectives: financial statement reporting by the issuer and financial investing. In financial statement reporting, companies must record long-term debt issuance and all of its associated payment obligations on its financial statements. On the flip side, investing in long-term debt includes putting money into debt investments with maturities of more than one year."
                https://www.investopedia.com/terms/l/longtermdebt.asp
            Other non-current liabilities
              note:
                Other Long-Term Liabilities
                  "Other long-term liabilities are a line item on a balance sheet that lumps together obligations that are not due within 12 months. These debts that are less urgent to repay are a part of their total liabilities but are categorized as “other” when the company doesn’t deem them important enough to warrant individual identification."
                https://www.investopedia.com/terms/o/otherlongtermliabilities.asp
          Total Liabilities = Total current liabilities + Total non-current liabilities
            note:

              Types of Liabilities
                Current liabilities, also known as short-term liabilities, are debts or obligations that need to be paid within a year.
                Non-current liabilities, also known as long-term liabilities, are debts or obligations due in over a year’s time.
                Contingent liabilities are liabilities that may occur, depending on the outcome of a future event. For example, when a company is facing a lawsuit of $100,000, the company would incur a liability if the lawsuit proves successful.
              https://corporatefinanceinstitute.com/resources/knowledge/accounting/types-of-liabilities/

          Total shareholders’ equity
            Common stock and additional paid-in capital, $0.00001 par value: 12,600,000 shares authorized; 4,323,987 and 4,443,236 shares issued and outstanding, respectively
              note:
                Common Stock
                  "
                  Authorized shares

                    When a business applies for incorporation to a secretary of state, its approved application will specify the classes (or types) of stock, the par value of the stock, and the number of shares it is authorized to issue. When its articles of incorporation are prepared, a business will often request authorization to issue a larger number of shares than what is immediately needed.

                    To illustrate, assume that the organizers of a new corporation need to issue 1,000 shares of common stock to get their corporation up and running. However, they foresee a future need to issue additional shares. As a result, they decide that their articles of incorporation should authorize 100,000 shares of common stock, even though only 1,000 shares will be issued at the time that the corporation is formed.
                    
                  Issued shares

                    When a corporation sells some of its authorized shares, the shares are described as issued shares. The number of issued shares is often considerably less than the number of authorized shares.

                    Corporations issue (or sell) shares of stock to obtain cash from investors, to acquire another company (the new shares are given to the owners of the other company in exchange for their ownership interest), to acquire certain assets or services, and as an incentive/reward for key officers of the corporation.

                    The par value of a share of stock is sometimes defined as the legal capital of a corporation. However, some states allow corporations to issue shares with no par value. If a state requires a par value, the value of common stock is usually an insignificant amount that was required by state laws many years ago. If the common stock has a par value, then whenever a share of stock is issued the par value is recorded in a separate stockholders' equity account in the general ledger. Any proceeds that exceed the par value are credited to another stockholders' equity account. This required accounting (discussed later) means that you can determine the number of issued shares by dividing the balance in the par value account by the par value per share.

                  Outstanding shares

                    If a share of stock has been issued and has not been reacquired by the corporation, it is said to be outstanding. For example, if a corporation initially sells 2,000 shares of its stock to investors, and if the corporation did not reacquire any of this stock, this corporation is said to have 2,000 shares of stock outstanding.

                    The number of outstanding shares is always less than or equal to the number of issued shares. The number of issued shares is always less than (or equal to) the authorized number of shares.
                  "
                https://www.accountingcoach.com/stockholders-equity/explanation/2
            Retained earnings
              note:
                Retained Earnings
                  "Retained earnings are an important concept in accounting. The term refers to the historical profits earned by a company, minus any dividends it paid in the past.

                  RE = BP + Net Income (or Loss) − C − S
                  where:
                    RE = Retained earnings
                    BP = Beginning Period RE
                    C  = Cash dividends
                    S  = Stock dividends"
                https://www.investopedia.com/terms/r/retainedearnings.asp
            Accumulated other comprehensive income/(loss)
              note:
                Accumulated Other Comprehensive Income
                  "Accumulated other comprehensive income (OCI) includes unrealized gains and losses reported in the equity section of the balance sheet that are netted below retained earnings. Other comprehensive income can consist of gains and losses on certain types of investments, pension plans, and hedging transactions. It is excluded from net income because the gains and losses have not yet been realized."
                https://www.investopedia.com/terms/a/accumulatedother.asp

      CONDENSED CONSOLIDATED STATEMENTS OF SHAREHOLDERS’ EQUITY
        the only thing parsed from this table is:
          Dividends and dividend equivalents declared
            note:
              total dividend payout
          Dividends and dividend equivalents declared per share or RSU
            note:
              dividend payout per share

      CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS

        nothing taken from this table

      also grab the quarter and year from the page footer on every page after the table of contents on page 2
        cant, on some forms the footer is just the page number
          ex: https://www.sec.gov/ix?doc=/Archives/edgar/data/1000045/000095017021004287/nick-20210930.htm

        done notes
          parsed net_income instead of total_cash_inflow and total_cash_outflow
            might come back to it another time to get total_cash_inflow and total_cash_outflow
              possibly using tag: us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
                in https://www.sec.gov/Archives/edgar/data/1000229/0000950170-21-002488-index.html

                or tag: us-gaap:Revenues
                in https://www.sec.gov/Archives/edgar/data/1000045/0000950170-21-004287-index.html
          stock splits
            see if they match up with shares outstanding
            stock splits are in form 10-K

            couldn't find stock split data for most of the 10-K forms, did find it fo rthe below 10-K though
              company filing submission 355 of 6777
                downloading filing submission
                  https://www.sec.gov/Archives/edgar/data/1057352/0001057352-21-000104-index.html
                  https://www.sec.gov/ix?doc=/Archives/edgar/data/1057352/000105735221000104/csgp-20210930.htm
                  https://www.sec.gov/Archives/edgar/data/1057352/000105735221000104/csgp-20210930_htm.xml

                need to figure out a way to determine if its a forward stock split or a reverse stock split
                  "A reverse split reduces the overall number of shares a shareholder owns, causing some shareholders who hold less than the minimum required by the split to be cashed out. The forward stock split increases the overall number of shares a shareholder owns."
                  https://www.investopedia.com/terms/r/reverse-forward-split.asp

                need to verify the stock splits are correct
                https://www.stocksplithistory.com/

            Adjusting Historical Stock Prices for Splits Using SQL
            https://stackoverflow.com/questions/63945130/adjusting-historical-stock-prices-for-splits-using-sql
          dividend (both total amount and per share)

            verify the dividends paid divided by the shares outstanding equal dividends per share
              it seems to be correct, make sure to look at only the dividends paid for this quarter

            if the dividends paid are not for a 3 month period:
              for total amount you need to subtract Q1 for Q2 total, Q2 from Q3 total, etc.
              ex: the dividends for this 10q are for 9 months becuase tis 10q is for Q3
                Ctrl + F: "Cash dividends paid to SWM stockholders"
                https://www.sec.gov/ix?doc=/Archives/edgar/data/1000623/000100062321000129/swm-20210930.htm
            however sometimes the dividneds paid are for a 3 month period:
              for example:
                Ctrl + F: "Dividends paid"
                https://www.sec.gov/ix?doc=/Archives/edgar/data/1000229/000095017021002488/clb-20210930.htm
    
            right now the program will assume a dividend of 0 if it cant find anything in the form
            all thats left to do is write the code that pulls the data of the previous quarters dividends paid from the mysql db. see fn. parse_dividends_paid_from_xml() in driver.py

            Important Dividend Dates
              Dividend payments follow a chronological order of events and the associated dates are important to determine the shareholders who qualify for receiving the dividend payment.

              Announcement date:
                Dividends are announced by company management on the announcement date, or declaration date, and must be approved by the shareholders before they can be paid.
              Ex-dividend date:
                The date on which the dividend eligibility expires is called the ex-dividend date or simply the ex-date. For instance, if a stock has an ex-date of Monday, May 5, then shareholders who buy the stock on or after that day will NOT qualify to get the dividend as they are buying it on or after the dividend expiry date. Shareholders who own the stock one business day prior to the ex-date—that is on Friday, May 2, or earlier—will receive the dividend.
              Record date:
                The record date is the cutoff date, established by the company in order to determine which shareholders are eligible to receive a dividend or distribution.
              Payment date:
                The company issues the payment of the dividend on the payment date, which is when the money gets credited to investors' accounts.
            https://www.investopedia.com/terms/d/dividend.asp

    10-K

      example 10-Ks:

        AAPL's 10-K for 2020
        https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019320000096/aapl-20200926.htm

        AAPL search
        https://www.sec.gov/edgar/browse/?CIK=320193&owner=exclude

      How do you find a public company’s Q4 results?
        "You can’t. The SEC does not require a 10-Q for the fourth quarter, as it would be unnecessarily redundant, given the information found in the 10-K. About the best you can do to look at Q4 is to take the annual numbers from the 10-K income statement and subtract the third quarter year to date figures found in the third quarter 10-Q."
      https://www.quora.com/How-do-you-find-a-public-company%E2%80%99s-Q4-results

    Finanical Statements Data Set:

      THIS LINK WILL BE WAAAAYYYYYYY EASIER TO PARSE, only goes back to 2009 though :(
      https://www.sec.gov/dera/data/financial-statement-data-sets.html

      done notes:
        does it have the data i need? does it have share splits?
          it has country, sector, and industry data

          sadly a few of the submissions dont have the data i need
            the data is in the form on the SEC website
            but its not in the num.txt file for some reason

            so i need to create a program that parses this stuff
            then if anything is missing, i parse the xml

      this link explains what the downloaded data contains
      https://www.sec.gov/files/aqfs.pdf

      metrics to grab:
        sub
          adsh - Accession Number. The 20-character string formed from the 18-digit number assigned by the SEC to each EDGAR submission.
            "Accession number: In the example above, 0001193125-15-118890 is the accession number, a unique identifier assigned automatically to an accepted submission by EDGAR. The first set of numbers (0001193125) is the CIK of the entity submitting the filing. This could be the company or a third-party filer agent. Some filer agents without a regulatory requirement to make disclosure filings with the SEC have a CIK but no searchable presence in the public EDGAR database. The next two numbers (15) represent the year. The last series of numbers represent a sequential count of submitted filings from that CIK. The count is usually, but not always, reset to zero at the start of each calendar year."
              - https://www.sec.gov/os/accessing-edgar-data
          cik - C entral Index Key (C IK). Ten digit number assigned by the SEC to each registrant that submits filings.
          name - Name of registrant. This corresponds to the name of the legal entity as recorded in EDGAR as of the filing date.
          sic - Standard Industrial Classification (SIC ). Four digit code assigned by the SEC as of the filing date, indicating the registrant’s type of business.
            https://en.wikipedia.org/wiki/Industry_classification
          countryba - The ISO 3166-1 country of the registrant's business address.
          form - The submission type of the registrant’s filing.
            10-Q, 10-K, etc.
          period - Balance Sheet Date
          fy - Fiscal Year Focus (as defined in EFM Ch. 6).
          fp - Fiscal Period Focus (as defined in EFM Ch. 6) within Fiscal Year. The 10-Q for the 1st, 2nd and 3rd quarters would have a fiscal period focus of Q1, Q2 (or H1), and Q3 (or M9) respectively, and a 10-K would have a fiscal period focus of FY.
          filed - The date of the registrant’s filing with the Commission.
          instance - The name of the submitted XBRL Instance Document (EX101.INS) type data file. The name often begins with the company ticker symbol.
        tag
          tag - The unique identifier (name) for a tag in a specific taxonomy release.
          doc - The detailed definition for the tag (truncated to 2048 characters). If a standard tag, then the text provided by the taxonomy, otherwise the text assigned by the filer. Some tags have neither, and this field is NULL.
        num
          adsh
          tag
          ddate - The end date for the data value, rounded to the nearest month end.
          qtrs - The count of the number of quarters represented by the data value, rounded to the nearest whole number. “0” indicates it is a point-in-time value.
          uom - The unit of measure for the value.
          value - The value. This is not scaled, it is as found in the Interactive Data file, but is limited to four digits to the right of the decimal point. 
        pre
          nothing from this table

    Other:
      done notes:
        sector and industry
          
          https://smallbusiness.chron.com/company-sic-codes-13398.html
          https://www.investopedia.com/ask/answers/05/industrysector.asp

          ways to get sector and industry are
            SIC
              https://www.investopedia.com/terms/s/sic_code.asp
                The SIC system classifies the economy into 11 major divisions:
                  Agriculture, forestry, and fishing
                  Mining
                  Construction
                  Manufacturing
                  Transportation and public utilities
                  Wholesale trade
                  Retail trade
                  Finance, insurance, real estate
                  Services
                  Public administration
                  Nonclassifiable establishments
                  These are then divided into 83 two-digit major groups, and further subdivided into 416 three-digit industry groups and then into more than 1,000 four-digit industries.
                Every company has a primary SIC code that indicates its main line of business. The first two digits of the SIC code identify the major industry group, the third digit identifies the industry group, and the fourth digit identifies the specific industry.
              https://en.wikipedia.org/wiki/Standard_Industrial_Classification#Structure
                SIC codes have a hierarchical, top-down structure that begins with general characteristics and narrows down to the specifics. The first two digits of the code represent the major industry sector to which a business belongs. The third and fourth digits describe the sub-classification of the business group and specialization, respectively. For example, "36" refers to a business that deals in "Electronic and Other Equipment." Adding "7" as a third digit to get "367" indicates that the business operates in "Electronic, Component and Accessories." The fourth digit distinguishes the specific industry sector, so a code of "3672" indicates that the business is concerned with "Printed Circuit Boards."
              https://www.sec.gov/corpfin/division-of-corporation-finance-standard-industrial-classification-sic-code-list
              https://libguides.calvin.edu/business/industry
                https://www.osha.gov/data/sic-manual
              https://www.thecorporatecounsel.net/blog/2016/03/sic-codes-how-does-the-sec-assign-them.html
              https://offistraedgarfiling.com/standard-industrial-classification-sic-code-list/
            NAICS
              https://www.census.gov/naics/
              https://libguides.calvin.edu/business/industry
                https://www.census.gov/naics/?58967?yearbck=2017
              https://libguides.umgc.edu/c.php?g=970568&p=7014343
            GICS

              Sectors
                Energy
                Materials
                Industrials
                Consumer Discretionary
                Consumer Staples
                Health Care
                Financials
                Information Technology
                Communication Services
                Utilities
                Real Estate

              https://www.msci.com/our-solutions/indexes/gics

              https://www.investopedia.com/terms/g/gics.asp
              https://en.wikipedia.org/wiki/Global_Industry_Classification_Standard
              https://stackoverflow.com/questions/11339993/getting-stocks-by-industry-via-yahoo-finance
              https://www.spglobal.com/ratings/en/?ffFix=yes
                U: email
                P: ajyEDY463@%$
                Ratings_Content_Management@spglobal.com

              could potentially scrap it from yahoo finance
              https://finance.yahoo.com/quote/AAPL/profile/
                maybe theres an API?
            ICB (Industry Classification Benchmark), a classification structure maintained by Dow Jones Indexes and FTSE Group

              https://www.ftserussell.com/data/industry-classification-benchmark-icb

          I couldn't find the SIC on the 10Q but i found a page on the SEC website with the SIC that just uses the CIK in the URL (see the function parse_sic_code()). For the mapping of the SIC to the industry classification names i created the function download_standard_industrial_codes(), which uses 2 sources to create a list of all SIC codes, the SEC and OSHA. Of the SIC codes I've encountered in the 1st dozen 10-Qs of 2021 Q4, all of them have been in the SEC source, but the OSHA source provides the hierarchical structure the SIC codes use (as described in Wikipedia and Investopedia). I have found codes in the first dozen 10-Qs of 2021 Q4 that aren't in the OSHA source though. So both sources are needed.

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

    make sure it includes "tax harvesting"
      "Tax-loss harvesting allows you to sell investments that are down, replace them with reasonably similar investments, and then offset realized investment gains with those losses. The end result is that less of your money goes to taxes and more may stay invested and working for you."
        - https://www.google.com/search?q=tax+loss+harvesting&sxsrf=AOaemvJ2xNLYQ0BLtovTCzAVB7Ywqqb_zA%3A1639003134181&ei=_jOxYfb9CczD0PEP6r2w-As&ved=0ahUKEwj29OO8otX0AhXMITQIHeoeDL8Q4dUDCA4&uact=5&oq=tax+loss+harvesting&gs_lcp=Cgdnd3Mtd2l6EAMyCggAELEDEIMBEEMyBQgAEIAEMgoIABCABBCHAhAUMgQIABBDMgUIABCABDIFCAAQgAQyBQgAEIAEMgQIABBDMgQIABBDMgUIABCABDoHCAAQRxCwAzoHCAAQsAMQQzoICAAQ5AIQsAM6EAguEMcBEKMCEMgDELADEEM6EAguEMcBENEDEMgDELADEEM6BAgjECc6BggAEAcQHkoECEEYAEoECEYYAVCYA1ijCWDACmgBcAJ4AIABggGIAbEEkgEDMi4zmAEAoAEByAESwAEB&sclient=gws-wiz

    maybe include the selling of cash secured puts of stocks that are cheap enough and i want to own anyway

  really interesting investing strategy of Peter Lynch
    once you have this value investing app built
      watch it again and take notes
  https://www.youtube.com/watch?v=J1DFMXL2kXE&t=1934s

  maybe make a file with all the metric definitions

  for testing
    Facebook 2020 q3
    https://www.sec.gov/Archives/edgar/data/1326801/0001326801-20-000076-index.html
    https://www.sec.gov/Archives/edgar/data/1326801/000132680120000076/fb-06302020x10q.htm

  create cronjob:
    on daily intervals:
      check to see if the SEC has released a new quarters company filings
        you can either:
          store all the filings (parsed for the relevant info)
          or store a variable in a file of the most recent quarter data has been gathered for

    THIS MIGHT NOT WORK!!!

      you need to verify that the SEC doesn't just update the list of companies that have submitted a filin when they submit it by downloading the new list each time and seeing if theres any new companies on it

  each quarter form is getting the quarter before
    the 10-K is the annual report that has q4 data
    the 10-Q is the quarterly report that has q1, q2, and q3 data

    why is the FB 2019 Q4 form getting the 2019 Q3 form?
      "For the quarterly period ended September 30, 2019"
        https://www.sec.gov/Archives/edgar/data/1326801/000132680119000069/fb-09302019x10q.htm#s86440F9012665AA1B578CBCDC37CB566

  EDGAR

    using this tutorial to download all the forms (see driver2.py)
      https://codingandfun.com/python-sec-edgar-scraper/

      the tutorial uses this library, if you wanted you could just take the parts of the library you need and not import it.
        https://pypi.org/project/python-edgar/
        https://github.com/edgarminers/python-edgar

    used this link to figure out what to assign the user_agent variable
      https://sec-edgar.github.io/sec-edgar/usage.html      

      user_agent is a value thats passed to the SEC API to identify you
        https://www.sec.gov/os/accessing-edgar-data

      and copied the way this script formats the header the user_agent is passed in
        https://github.com/edgarminers/python-edgar/blob/master/edgar/main.py

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

