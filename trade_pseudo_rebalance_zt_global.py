#!/usr/bin/env python3.8

from decimal import Decimal
from time import time, sleep, strftime
from concurrent.futures import ThreadPoolExecutor
from functions_zt_global import functions_zt_rebalance as f
from config_key import API_KEY, SECRET_KEY


executor = ThreadPoolExecutor(10)

symbol_bull         =  'symbol=DASHBULL_USDT&size=1'
symbol_bear         =  'symbol=DASHBEAR_USDT&size=1'
symbol_asset_bull   =  "DASHBULL"
symbol_asset_bear   =  "DASHBEAR"
symbol_trade_bull   =  "DASHBULL_USDT"
symbol_trade_bear   =  "DASHBEAR_USDT"

multiplier_half_assets   = Decimal(1.25)
multiplier_surplus       = Decimal(0.5)
multiplier_trigger       = Decimal(1.0)
# r.a.a.o.u  !!! - requires available amount of usdt  !!!
multiplier_buy_bear      = Decimal(0.4)  ##  r.a.a.o.u  !!!
multiplier_buy_bull      = Decimal(0.4)  ##  r.a.a.o.u  !!!
##  the amount of usd from the available usdt pool 
usdt_strategy            = Decimal(20)    ## usdt available for strategy !!!



while True:
    sleep(10)
    print(strftime("%D") + f'{" "*2}' + strftime("%H:%M:%S") + "\n")
    
    ############################################################################
    #
    #   DOWNLOAD THE BEST BID AND ASK
    #
    ############################################################################
    e_bull = executor.submit(f.bid_ask, (symbol_bull))
    e_bear = executor.submit(f.bid_ask, (symbol_bear))
    bid_bull, ask_bull = e_bull.result()
    bid_bear, ask_bear = e_bear.result()
    print("Bid  BULL   =  " f'{bid_bull}')
    print("Ask  BULL   =  " f'{ask_bull}' "\n")
    print("Bid  BEAR   =  " f'{bid_bear}')
    print("Ask  BEAR   =  " f'{ask_bear}' "\n")
    print(strftime("%D") + f'{" "*2}' + strftime("%H:%M:%S"))


    ############################################################################
    #
    #   ASSET VALUE CHECK
    #
    ############################################################################
    price_asset_bull = str(round(bid_bull * Decimal(0.99), 8))
    price_asset_bear = str(round(bid_bear * Decimal(0.99), 8))
    asset = f.asset(API_KEY, SECRET_KEY)
    asset_bull = Decimal(asset[symbol_asset_bull]['available']) * round(Decimal(price_asset_bull), 8)
    asset_bear = Decimal(asset[symbol_asset_bear]['available']) * round(Decimal(price_asset_bear), 8)
    print("Asset BULL  =  " f'{asset_bull}')
    print("Asset BEAR  =  " f'{asset_bear}' "\n")
    total_assets = asset_bull + asset_bear
    print("TOTAL ASSETS  =  " f'{total_assets}')
    half_assets = total_assets / int(2)
    print("Half assets   =  " f'{half_assets}' "\n")
    print("\n" * 2)
    
    
    ############################################################################
    #
    #   TRADE
    #
    ############################################################################
    trigger = half_assets * multiplier_half_assets    ##   in USDT
        #
        #
    if asset_bull > trigger:
        print("    1.    START:    BULL  >  BEAR ")
        ################################################
        # USDT for SELL
        ################################################
        surplus = asset_bull - half_assets    ##   in USDT
        usdt_sell = surplus * multiplier_surplus 

        ################################################
        # USDT for BUY
        ################################################
        ##
        #  1. you can with this solution:
        usdt_buy =  (trigger - asset_bear) * multiplier_buy_bear   # r.a.a.o.u !!!
        #
        multiplier_buy_bear *= Decimal(1.2)
        part_of_the_difference = (trigger - half_assets) * Decimal(0.5)
        #
        if usdt_buy + asset_bear > part_of_the_difference + half_assets: 
                    usdt_buy = part_of_the_difference + half_assets - asset_bear
                    multiplier_buy_bear = Decimal(0.4)
        ###################################
        usdt_strategy -= usdt_buy - usdt_sell     # r.a.a.o.u !!!
        print("USDT strategy  =  " f'{round(usdt_strategy, 4)}')  
        #
        if usdt_strategy <= int(5):
            usdt_buy = usdt_sell
        ##
        #  2. or simply this solution: 
        ## usdt_buy = usdt_sell
        
        ################################################
        # QUANTITY CALCULATION  AND  PRICE LIMIT
        ################################################   
        bull_price_derivative  = round(bid_bull * Decimal(1.00), 8)
        amount_bull = round(usdt_sell / bull_price_derivative, 2)   ##  SELL in quantities  
        price_bull  = round(bid_bull * Decimal(0.98), 8)
        #
        bear_price_derivative = round(ask_bear * Decimal(1.001), 8)
        amount_bear = round(usdt_buy / bear_price_derivative, 2)    ## BUY in quantities  
        price_bear  = round(ask_bear * Decimal(1.02), 8)
        
        ################################################
        # SENDING ORDERS
        ################################################
        # SELL
        e_trade_bull = executor.submit( f.trade, symbol_trade_bull,  str(1), str(price_bull),  
                                                 str(amount_bull),   API_KEY, SECRET_KEY )   
         # BUY
        e_trade_bear = executor.submit( f.trade, symbol_trade_bear, str(2), str(price_bear),
                                                 str(amount_bear), API_KEY, SECRET_KEY )    
        e_trade_bull.result()
        e_trade_bear.result()
        print("    1.    END:    BULL  >  BEAR ",  "\n"*3)
        #
        #
    elif asset_bear > trigger:
        print("    2.    START:    BEAR  >  BULL ")
        ################################################
        # USDT for SELL
        ################################################
        surplus = asset_bear - half_assets    ##   in USDT
        usdt_sell = surplus * multiplier_surplus  
        
        ################################################
        # USDT for BUY
        ################################################        
        ##
        #  1. you can with this solution:
        usdt_buy = (trigger - asset_bull) * multiplier_buy_bull   # r.a.a.o.u !!!
        #
        multiplier_buy_bull *= Decimal(1.2)
        part_of_the_difference = (trigger - half_assets) * Decimal(0.5)
        #
        if usdt_buy + asset_bull > part_of_the_difference + half_assets: 
                    usdt_buy = part_of_the_difference + half_assets - asset_bull
                    multiplier_buy_bull = Decimal(0.4)
        ##################################
        usdt_strategy -= usdt_buy - usdt_sell     # r.a.a.o.u !!!
        print("USDT strategy  =  " f'{round(usdt_strategy, 4)}')
        #
        if usdt_strategy <= int(5):
            usdt_buy = usdt_sell
        ##
        #  2. or simply this solution: 
        ## usdt_buy = usdt_sell
        
        ################################################
        # QUANTITY CALCULATION  AND  PRICE LIMIT
        ################################################   
        bear_price_derivative  = round(bid_bear * Decimal(1.00), 8)
        amount_bear = round(usdt_sell / bear_price_derivative, 2)    ## SELL in quantities   
        price_bear  = round(bid_bear * Decimal(0.98), 8)
        #
        bull_price_derivative  = round(ask_bull * Decimal(1.001), 8)
        amount_bull = round(usdt_buy / bull_price_derivative, 2)   ##  BUY in quantities  
        price_bull  = round(ask_bull * Decimal(1.02), 8)
       
        ################################################
        # SENDING ORDERS
        ################################################
        # SELL
        e_trade_bear = executor.submit( f.trade, symbol_trade_bear, str(1), str(price_bear),  
                                                 str(amount_bear), API_KEY, SECRET_KEY )
        # BUY
        e_trade_bull = executor.submit( f.trade, symbol_trade_bull,   str(2), str(price_bull),   
                                                 str(amount_bull),   API_KEY, SECRET_KEY )   
        e_trade_bear.result()
        e_trade_bull.result()
        print("    2.    END:    BEAR  >  BULL ",  "\n"*3)
    ############################################################################
    print("\n"*3)
# END
