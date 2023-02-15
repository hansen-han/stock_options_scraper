#FUNCTIONS
# - Check the time 
# - Fetch option data
# - Store in sqlite database

import time
import datetime
from datetime import timedelta
import json
import requests
import logging
#import pandas as pd
import sqlite3
from pytz import timezone


# Input TD Ameritrade API Key
TD_AMERITRADE_API_KEY = "TD_AMERITRADE_API_KEY"

#configuration
log_format = (
    '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    filename=('options_debug.log'),
)
tz = timezone('EST')
format = "%d/%m/%Y %H:%M:%S"

#create the database for storing options data
conn = sqlite3.connect("optionsdata.db")
c = conn.cursor()
c.execute('''CREATE TABLE options_data (date_time text, ticker_symbol text, options_chain text)''')

#Determine the time until the market opens 
def time_to_open(current_time):
    if current_time.weekday() <= 4:
        d = (current_time + timedelta(days=1)).date()
    else:
        days_to_mon = 0 - current_time.weekday() + 7
        d = (current_time + timedelta(days=days_to_mon)).date()
    next_day = datetime.datetime.combine(d, datetime.time(9, 30, tzinfo=tz))
    seconds = (next_day - current_time).total_seconds()
    return seconds


def options_scraper(ticker_list, scraping_interval):
    '''
    This function collects options chain data from the TD Ameritrade API for a given list of stock tickers, 
    and stores the data in a local SQLite database. The function continuously runs and collects data during 
    the trading hours of Monday to Friday. The collection interval is defined by scraping_interval in minutes.

    Parameters:
        ticker_list: a list of stock tickers to collect options chain data for.
        scraping_interval: an integer that defines the time interval in minutes between consecutive data collections.
    Returns:
        None
    '''
    logging.debug("Initializied options scraper")

    #stablish connection with local db
    conn = sqlite3.connect("optionsdata.db")
    c = conn.cursor()

    while True:
        # Check if Monday-Friday
        if datetime.datetime.now(tz).weekday() >= 0 and datetime.datetime.now(tz).weekday() <= 4:
            # Checks market is open
            print('Trading day')
            if datetime.datetime.now(tz).time() > datetime.time(9, 30) and datetime.datetime.now(tz).time() <= datetime.time(15, 30):
                #collect data
                for ticker in ticker_list:
                    try:
                        print("fetching options chain data")
                        #try to collect data
                        r = requests.get(("https://api.tdameritrade.com/v1/marketdata/chains?apikey={TD_AMERITRADE_API_KEY}&symbol={ticker_symbol}&contractType=ALL&strikeCount=10&includeQuotes=TRUE&strategy=SINGLE&range=ALL").format(ticker_symbol=ticker, TD_AMERITRADE_API_KEY = TD_AMERITRADE_API_KEY))
                        r_dict = r.json()
                        options_chain_entry = str(r_dict)
                        print("fetched options chain data")
                        entry = (datetime.datetime.now().strftime(format), ticker, options_chain_entry)
                        print("inserting into database")
                        c.execute("INSERT INTO options_data VALUES (?, ?, ?)", entry)
                        conn.commit()
                        print("Collected options chain:", str(ticker))
                        logging.info(("Collected options chain:", str(ticker)))
                    except:
                        print("ERROR: Unable to complete options chain data retreival:", str(ticker))
                        logging.error(("Unable to fetch options chain for {ticker_symbol}").format(ticker_symbol=ticker))
                        #If unable to collect data, log failure and move on to next ticker
                #sleep until next interval
                time.sleep(scraping_interval*60) #the number of minutes multiplied by 60 to get the seconds to sleep
            else:
                # Get time amount until open, sleep that amount
                print('Market closed ({})'.format(datetime.datetime.now(tz)))
                print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
                time.sleep(time_to_open(datetime.datetime.now(tz)))
        else:
            # If not trading day, find out how much until open, sleep that amount
            print('Market closed ({})'.format(datetime.datetime.now(tz)))
            print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
            time.sleep(time_to_open(datetime.datetime.now(tz)))


#run the options scraper
if __name__ == "__main__":
    options_scraper(
        ticker_list = ["GME", "PLTR", "AMC", "TSLA", "MSFT", "GOOGL", "AAPL", "T", "SPY", "VIX", "SVXY", "MRNA"],
        scraping_interval = 30 #30 minutes
    )