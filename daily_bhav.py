# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 22:03:13 2019

@author: Admin
"""

import sqlalchemy as db
import pandas as pd
import requests
from io import BytesIO
from datetime import date as dt, timedelta as td, datetime as dtm
import logging
import traceback

def get_date():
    # market is closed on Saturday and Sunday
    if dt.weekday(dt.today()) not in (0,6):
        return dt.today()-td(days=1)
    else:
        #return dtm.strptime("2019-06-21","%Y-%m-%d")
        return None

def get_url(source,market_date,log):
    try:
        if source == 'nse':
            base_url = 'https://www.nseindia.com/content/historical/EQUITIES/{}/{}/cm{}bhav.csv.zip'
        elif source == 'bse':
            base_url = ''
        else:
            log.error("{} - Invalid source".format(dtm.now()))
            raise ValueError
        return base_url.format(str(market_date.year),str.upper(dt.strftime(market_date,"%b")),str.upper(dt.strftime(market_date,"%d%b%Y"))) 
    except:
        raise

def get_data(url, log):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
        req = requests.get(url, headers=headers)
        if req.status_code ==200:
            zipped_data = BytesIO(req.content)
        else:
            #Raise error
            log.error("{} - Error reading data from url status code is {}".format(dtm.now(),req.status_code))
            log.error(url)
            raise ValueError
        
        return zipped_data
    except:
        raise

def inicio(log):
    try:
        engine = db.create_engine("mysql+mysqldb://root:root@localhost:3306/portfolio_tracker")
        # prepare the url
        market_date = get_date()
        print(market_date)
        if market_date:
            url = get_url('nse',market_date,log)
            # read url data
            data = get_data(url, log)
            # read data in dataframe
            df_bhav = pd.read_csv(data,compression='zip')
            #data processing begins
            df_bhav.set_index('ISIN', inplace=True)
            # get the portfolio details
            query_sec_id = "Select isin as ISIN, id from d_portfolio"
            df_sec_id = pd.read_sql(sql=query_sec_id,con=engine,index_col='ISIN')
            
            df_port_data = df_bhav.merge(df_sec_id,how='inner',on='ISIN')
            df_port_data.rename(index=str,columns={'id':'sec_id','TOTALTRADES':'no_trade','TOTTRDQTY':'no_shares','TOTTRDVAL':'net_turnover','TIMESTAMP':'txn_date'}, inplace=True)
            df_port_data.rename(str.lower, axis='columns', inplace=True)
            df_port_data.reset_index(inplace=True)
            df_update = df_port_data[['sec_id','txn_date','open','close','high','low','last','no_trade', 'no_shares', 'net_turnover']]
            df_update['txn_date'] = pd.to_datetime(df_update['txn_date'],format="%d-%b-%Y")
            df_update.to_sql(name='f_daily_data',con=engine, if_exists='append',index=False)
        else:
            log.info("Market Closed, no data to be read")
    except db.exc.SQLAlchemyError:
        log.error("Database error occurred at {}".format(dtm.now()))
        raise

def main():   
    try:
        logging.basicConfig(filename='E:\\Personal\\advait\\Analytics\\bhav\\bhav.log')
        log = logging.getLogger()  
        log.setLevel("INFO")
        log.info(str(dtm.now()) + " - "+"Daily Bhav Start" )
        inicio(log)
        log.info(str(dtm.now()) + " - "+"Daily Bhav End" )
    except:
        err = traceback.format_exc()
        log.error("{} - {}".format(dtm.now(),err))

if __name__ == '__main__':
    main()
    