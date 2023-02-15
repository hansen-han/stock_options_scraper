# options_scraper
As I became interested in options trading and algorithmic trading, I realized that unlike historical stock data, historical option chain data is not readily available to the public. This made me curious about how I could collect and store option chain data for my own use. After researching different options, I decided to write a scraping script using TD Ameritrade's API that would collect and store the data in an SQLite database for backtesting and development of algorithmic strategies.

## Requirements
To use this script, you will need:

A TD Ameritrade API key, which can be obtained by registering for a TD Ameritrade Developer account.

## Configuration
To configure the script, you will need to:

- Enter your TD Ameritrade API key in the script where indicated.
- Add the list of tickers for which you want to collect option chain data in the ticker_list variable.
- Set the interval (in minutes) at which you want to collect option chain data in the scraping_interval variable.

## Usage
To use the script, simply run it from your command line or preferred Python IDE. The script will continuously scrape option chain data for the specified list of tickers at the defined interval, storing the data in an SQLite database. The script will also check whether the stock market is open and sleep until it opens if it is not.

The options_data table in the SQLite database will contain the following columns:

```date_time```: the date and time of the data collection.
```ticker_symbol```: the ticker symbol of the stock for which the option chain data was collected.
```options_chain```: a JSON string containing the option chain data.
## License
This script is licensed under the MIT License, which means you can use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the script. Please see the LICENSE file for more details.

