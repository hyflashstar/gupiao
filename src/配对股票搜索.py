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
formPeriod='2016-06-01:2017-01-03'
#tradePeriod='2017-01-01:2017-08-25'

#Close=Close['2016']

#Closet=Close[tradePeriod.split(':')[0] : tradePeriod.split(':')[1]]


industry=ls.read_industry()
industry1=industry.copy()
industry1['code1']=industry1['code']
industry1['name1']=industry1['name']
industry1['c_name1']=industry1['c_name']
industry1=industry1.loc[:,['code1','name1','c_name1']]

df=pd.DataFrame(columns=['code','code1', 'alpha','beta','p-value','mu','sd','c_sd','c1_sd'])
for i in range(0,Close.shape[1]-1):
    for z in range(i+1,Close.shape[1]):
        c=Close.iloc[:,[i,z]]
        c=c.dropna(axis=0)
        
        CloseY=c[lastYearPeriod.split(':')[0]:lastYearPeriod.split(':')[1]]
        Closef=c[formPeriod.split(':')[0]:formPeriod.split(':')[1]]
        if(Closef.shape[0]>0 and CloseY.shape[0]>0):
            dis=(pt.Cointegration(Closef.iloc[:,0],Closef.iloc[:,1]))
            if(dis):
                #再次计算上一年的相关性
                last_year_dis=(pt.Cointegration(CloseY.iloc[:,0],CloseY.iloc[:,1]))
                if(last_year_dis):
                    spreadf=pt.CointegrationSpread(c.iloc[:,0],c.iloc[:,1],formPeriod,formPeriod)
                    mu=np.mean(spreadf)
                    sd=np.std(spreadf)
                    df.loc[df.shape[0]+1]={'code':sz50s.iloc[i]['code'],'code1':sz50s.iloc[z]['code'],
                          'alpha':dis[0],'beta':dis[1],'p-value':dis[2],'mu':mu,'sd':sd,'c_sd':np.log(Close.iloc[:,i]).std(),'c1_sd':np.log(Close.iloc[:,z]).std()}

#select=df[(df['dis']>0)]
select=df[df['alpha']>0]
select=pd.merge(select,industry,how='left',on=['code'])
select=pd.merge(select,industry1,how='left',on=['code1'])
    
    #先只取同行业的来算
select=select[select['c_name']==select['c_name1']]

#同行业的



