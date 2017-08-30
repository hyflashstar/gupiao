# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 14:50:59 2017

@author: 53771
"""

import loadStock as ls
import PairTrading as pairTrading
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

#账户初始资金
cash=[10000]
tradePeriod="2017-01-03:2017-01-03"
startDate=tradePeriod.split(':')[0]
endDate=tradePeriod.split(':')[1]


#获取两个的价格曲线
pt=pairTrading.PairTrading()



def pairingStock(Close,firstPeriod,secondPeriod):
    df=pd.DataFrame(columns=['code','code1', 'alpha','beta','mu','sd'])
    CloseF=Close[firstPeriod.split(':')[0]:firstPeriod.split(':')[1]]
    CloseS=Close[secondPeriod.split(':')[0]:secondPeriod.split(':')[1]]
    for i in range(0,Close.shape[1]-1):
        for z in range(i+1,Close.shape[1]):
            dis=(pt.Cointegration(CloseF.iloc[:,i],CloseF.iloc[:,z]))#计算第一个时间段的相关性
            if(dis):
                #再次计算第二个时间段的相关性
                last_year_dis=(pt.Cointegration(CloseS.iloc[:,i],CloseS.iloc[:,z]))
                if(last_year_dis):
                    spreadf=pt.CointegrationSpread(Close.iloc[:,i],Close.iloc[:,z],firstPeriod,firstPeriod)
                    mu=np.mean(spreadf)
                    sd=np.std(spreadf)
                    df.loc[df.shape[0]+1]={'code':sz50s.iloc[i]['code'],'code1':sz50s.iloc[z]['code'],
                          'alpha':dis[0],'beta':dis[1],'mu':mu,'sd':sd}

    select=df[df['alpha']>0]
    
    #取得行业相关性，同行业认同
    
    
    return select
    


#获取交易记录,才收盘价代表当日价格（现在用上证50的来做试验，降低数量级）
sz50s=ts.get_sz50s()
#industtry=ts.get_industry_classified()
pt=pairTrading.PairTrading()
Close=pd.DataFrame()
#Close.index=c000001.index
for index,row in sz50s.iterrows():
    data=ls.read_hit_data(row['code'])
    #Close.index=data.index
    Close[row['code']]=data['close']
    
trade=Close[startDate:endDate]
for index,row in trade.iterrows():
    #计算前6个月符合配对交易的规则的
    delta = dt.timedelta(days=183)
    six_months_ago = index - delta
    s=six_months_ago.strftime('%Y-%m-%d')
    e=index.strftime('%Y-%m-%d')
    firstPeriod=s+":"+e
    secondPeriod='2016-01-01:2017-01-01' 
    #print(firstPeriod)
    select=pairingStock(Close,firstPeriod,secondPeriod).sort_values('sd')
    
    
    

    
    #选出当前时间点符合交易规则的股票
    
    
    #模拟交易
    

