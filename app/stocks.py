from app import config
import numpy as np
import pandas as pd
import quandl
from datetime import datetime, timezone, timedelta
import random

quandl.ApiConfig.api_key = config['QUANDL_API_TOKEN']

tickers = pd.read_csv('data/wiki_tickers.csv')

def get_date(is_datetime=False):
    def get_date_datetime():
        '''
        Since the free api is only used for historical data up until 2018, need to set how far back in time we are.
        Returns five years ago.
        '''
        return datetime.now(timezone.utc) - timedelta(days=5*365)

    def get_date_str():
        dt = get_date_datetime()
        return f'{dt.year}-{dt.month}-{dt.day}'

    return get_date_datetime() if is_datetime else get_date_str()

def get_tickers():
    return tickers['ticker']

def get_stocks(which_stocks, which_day:str=None):
    database_codes = [f'WIKI/{ticker}' for ticker in which_stocks]
    end_date = which_day if which_day else get_date()
    data = pd.DataFrame()
    for database_code in database_codes:
        new_data = quandl.get(database_code, end_date=end_date, rows=1)
        new_data['Ticker'] = database_code[5:]
        new_data['Date'] = end_date
        data = data.append(new_data, ignore_index=True)
    return data

def get_home_stocks(ticker:str=None):
    if ticker:
        home_tickers = []
        for tck in get_tickers():
            if ticker in tck or ticker == tck:
                home_tickers.append(tck)
        if len(home_tickers) == 0:
            home_tickers = random.choices(get_tickers(), k=10)
        if len(home_tickers) > 10:
            home_tickers = home_tickers[:10]
    else:
        home_tickers = random.choices(get_tickers(), k=10)
    return get_stocks(home_tickers).to_dict()