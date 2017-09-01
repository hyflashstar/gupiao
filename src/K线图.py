# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:20:29 2017

@author: 53771
"""

import loadStock as ls
import tushare as ts
from matplotlib.dates import DateFormatter,WeekdayLocator,DayLocator,MONDAY,date2num
from matplotlib.finance import candlestick_ohlc
from datetime import datetime
import matplotlib.pyplot as plt
import pandas_candlestick_ohlc as pohlc


df=ls.read_hit_data('sh')
df2015=df['2012-09']

plotdat=pohlc.pandas_candlestick_ohlc(df2015)


df2012=df['2012']
Close=df2012.close
Open=df2012.open
C10p=Close-Open

Shape=[0,0,0]

lag1C10p=C10p.shift(1)
lag2C10p=C10p.shift(2)

for i  in range(3,len(C10p)):
    #上上日下跌进25%的线，昨日变化幅度在中线，当日变化幅大于上上日的一半
    if all([lag2C10p[i]<-11,abs(lag1C10p[i])<2,C10p[i]>6,abs(C10p[i])>abs(lag2C10p[i]*0.5)]):
        Shape.append(1)
    else:
        Shape.append(0)
        

lagOpen=Open.shift(1)
lagClose=Close.shift(1)
lag2Close=Close.shift(2)

Doji=[0,0,0]
for i in range(3,len(Open),1):
    #今天开盘高于昨日开盘，昨日开盘小于前日收盘，昨日收盘小于今天开盘，昨日收盘小于前日收盘
    if(all([lagOpen[i]<Open[i],lagOpen[i]<lag2Close[i],
            lagClose[i]<Open[i],lagClose[i]<lag2Close[i]])):
        Doji.append(1)
    else:
        Doji.append(0)


ret=Close/Close.shift(1)-1
lag1ret=ret.shift(1)
lag2ret=ret.shift(2)

Trend=[0,0,0]
for i in range(3,len(ret)):
    #连续两个交易日下跌
    if(all([lag1ret[i]<0,lag2ret[i]<0])):
        Trend.append(1)
    else:
        Trend.append(0)


StarSig=[]
for i in range(len(Trend)):
    if all([Shape[i]==1,Doji[i]==1,Trend[i]==1]):
        StarSig.append(1)
    else:
        StarSig.append(0)
        
for i in range(len(StarSig)):
    if StarSig[i]==1:
        print(df2012.index[i])




        
    