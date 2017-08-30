# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 17:06:52 2017

@author: 53771
"""

import loadStock as ls
import PairTrading as pairTrading
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sz50s=ts.get_sz50s()
#industtry=ts.get_industry_classified()
pt=pairTrading.PairTrading()
Close=pd.DataFrame()
#Close.index=c000001.index
for index,row in sz50s.iterrows():
    data=ls.read_hit_data(row['code'])
    #Close.index=data.index
    Close[row['code']]=data['close']

lastYearPeriod='2016-01-01:2017-01-01' 
formPeriod='2017-01-01:2017-06-01'
tradePeriod='2017-01-01:2017-08-25'

#Close=Close['2016']
CloseY=Close[lastYearPeriod.split(':')[0]:lastYearPeriod.split(':')[1]]
Closef=Close[formPeriod.split(':')[0]:formPeriod.split(':')[1]]
Closet=Close[tradePeriod.split(':')[0] : tradePeriod.split(':')[1]]


df=pd.DataFrame(columns=['code','code1', 'alpha','beta','mu','sd'])
for i in range(0,Close.shape[1]-1):
    for z in range(i+1,Close.shape[1]):
        dis=(pt.Cointegration(Closef.iloc[:,i],Closef.iloc[:,z]))
        if(dis):
            #再次计算上一年的相关性
            last_year_dis=(pt.Cointegration(CloseY.iloc[:,i],CloseY.iloc[:,z]))
            if(last_year_dis):
                spreadf=pt.CointegrationSpread(Close.iloc[:,i],Close.iloc[:,z],formPeriod,formPeriod)
                mu=np.mean(spreadf)
                sd=np.std(spreadf)
                df.loc[df.shape[0]+1]={'code':sz50s.iloc[i]['code'],'code1':sz50s.iloc[z]['code'],
                      'alpha':dis[0],'beta':dis[1],'mu':mu,'sd':sd}

#select=df[(df['dis']>0)]
select=df[df['alpha']>0]

#同行业的



