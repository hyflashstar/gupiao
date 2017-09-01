# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 16:24:32 2017

@author: 53771
"""

import loadStock as ls
import tushare as ts
from datetime import datetime
import matplotlib.pyplot as plt
import pandas_candlestick_ohlc as pohlc
import pandas as pd

ssec=ls.read_hit_data('sh')
ssec2011=ssec['2012']

Close11=ssec2011.close
Open11=ssec2011.open

lagClose11=Close11.shift(1)
lagOpen11=Open11.shift(1)
Cloud=pd.Series(0,index=Close11.index)
for i in range(1,len(Close11)):
    if all([Close11[i]<Open11[i],#当时收盘价小于开盘价（当日跌）
            lagClose11[i]>lagOpen11[i],#昨日收盘价大于昨天开盘价(昨日涨)
            Open11[i]>lagClose11[i],#今天开盘价高于昨天收盘价
            Close11[i]<0.5*(lagClose11[i]+lagOpen11[i]),#今天收盘价低于昨日开盘介与收盘价的中线
            Close11[i]>lagOpen11[i]#当日收盘价大于昨日开盘价       
            ]):
        Cloud[i]=1
    
Trend=pd.Series(0,index=Close11.index)
for i in range(2,len(Close11)):
    if Close11[i-1]>Close11[i-2]>Close11[i-3]:
        Trend[i]=1
        

darkCloud=Cloud+Trend


pohlc.pandas_candlestick_ohlc(ssec['2012-07'])
            
    