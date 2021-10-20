#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 15:35:33 2021

@author: roji
"""


import numpy as np
import tweeter
import constants
import time
import alpaca_trade_api as tradeapi

def main():
    ticker = 'GOOGL'
    max_results = 100
    end_point = constants.end_point
    BEARERTOKEN = constants.BEARERTOKEN
    PUB_KEY = constants.PUB_KEY
    SEC_KEY = constants.SEC_KEY
    
    
    api = tradeapi.REST(key_id = PUB_KEY,secret_key = SEC_KEY,base_url = end_point)
    twitter = tweeter.tweet(ticker = ticker, BEARER_TOKEN = BEARERTOKEN, max_results= max_results)
    
    pos_held = False
    
    while True:
        print("")
        print("Checking Price")
        market_data = api.get_barset(ticker,'minute', limit = 5)
        
        close_list = []
        
        for bar in market_data[ticker]:
            close_list.append(bar.c)
            
            
        close_list = np.array(close_list, dtype = np.float64)
        ma = np.mean(close_list)
        last_price = close_list[4]
        
        print("Moving average :" + str(ma))
        print("Last price:" + str(last_price))
        
        
        df = twitter.create_data_frame()
        df = twitter.adding_prob_and_sentiment(df)
        alpha = twitter.average_sentiments(df)
        print('alpha:',alpha)
        
        if ma + 0.1 < last_price and not pos_held and alpha > 0 :
            print('BUY')
            api.submit_order(symbol = ticker, qty = 10, side = 'buy',type = 'market',time_in_force = 'gtc')
            pos_held = True
            
        elif ma - 0.1 > last_price and pos_held and alpha < 0:
            print('SELL')
            api.submit_order(symbol = ticker,qty = 10, side = 'sell',type = 'market',time_in_force = 'gtc')
            pos_held = False
        
        time.sleep(60)
    
    

if __name__ == "__main__":
    main()