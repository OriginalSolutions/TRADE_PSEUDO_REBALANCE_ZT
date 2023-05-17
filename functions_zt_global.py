#!/usr/bin/env python3.8

import pandas as pd 
import copy  
import requests    
from decimal import Decimal 
import json 
import hashlib 
from urllib.parse import urljoin, urlencode 


class functions_zt_rebalance:
    @classmethod
    def  bid_ask(cls, symbol_bid_ask: str):
        base_url = "https://www.ztb.im"    
        contex = "/api/v1/depth"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        long =  symbol_bid_ask
        ticker = requests.request('GET', base_url + contex  + "?" + long, headers=headers)
        ticker = ticker.json()    #  response.text
        bid = Decimal(ticker['bids'][0][0])
        ask = Decimal(ticker['asks'][0][0])
        return [bid, ask]
        
    @classmethod
    def  trade(cls, symbol_trade: str, side: str, price_trade: str, amount: str, API_KEY: str, SECRET_KEY: str):
        base_url = "https://www.ztb.im" 
        contex = "/api/v1/private/trade/limit"    
        headers = {
            'X-SITE-ID' : str(1),
            'Content-type' : 'application/x-www-form-urlencoded'
        }
        params = {
            "amount": amount,  
            ## "api_key" : API_KEY,    # 1 #  if it is uncommented ... 
            "market": symbol_trade,
            "price": price_trade,   
            "side": side  
        }
        ##    START COMMENTED #  ...  this, this must be commented out
        params['api_key'] = API_KEY 
        params = cls.sort_dictionary(params)
        ##    END COMMENTED #  ... this, this must be commented out
        params_bis = copy.deepcopy(params)
        params_bis["secret_key"] = SECRET_KEY
        query_string = urlencode(params_bis)
        params['sign'] = hashlib.md5(query_string.encode("utf-8")).hexdigest().upper()
        url = urljoin(base_url, contex)
        #
        cls.try_requests_post(url, headers, params, timeout=5)

    @classmethod
    def  asset(cls, API_KEY: str, SECRET_KEY: str):  
        base_url = "https://www.ztb.im" 
        contex = "/api/v1/private/user"
        headers = {
            'X-SITE-ID' : str(1),
            'Content-type' : 'application/x-www-form-urlencoded'
        }
        params = {
        }
        params['api_key'] = API_KEY
        params_bis = copy.deepcopy(params)
        params_bis["secret_key"] = SECRET_KEY
        query_string = urlencode(params_bis)
        params['sign'] = hashlib.md5(query_string.encode("utf-8")).hexdigest().upper()
        url = urljoin(base_url, contex)
        #
        response = cls.try_requests_post(url, headers, params, timeout=5)
        asset = response['result']
        return asset
    
    @staticmethod
    def try_requests_post(url, headers, params, timeout):
        try:
            response = requests.post(url=url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            print(response.status_code)
            # print(response.json())    #  response.text
            ###     return response.json()
        except requests.exceptions.HTTPError as ehttp:
            print(ehttp)
            print(response.status_code)
            print(response.content)
        except requests.exceptions.ConnectionError as econnect:
            print(econnect)
        except requests.exceptions.Timeout as etime:
            print(etime)
        except requests.exceptions.RequestException as re:
            print(re)
        return response.json()
        
    @staticmethod
    def sort_dictionary(dictionary):
        s = pd.Series(dictionary, name='DateValue')
        s.index.name = 'Name'
        s = s.reset_index()
        df = pd.DataFrame(s)
        df = df.sort_values(by='Name')
        d = dict.fromkeys(df["Name"])
        params = dict(zip(d, df["DateValue"]))
        return params
# END