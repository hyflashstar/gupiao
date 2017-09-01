# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 18:10:45 2017

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
tradePeriod="2016-01-01:2017-08-01"
startDate=tradePeriod.split(':')[0]
endDate=tradePeriod.split(':')[1]

#加入
pt=pairTrading.PairTrading()

sz50s=ts.get_sz50s()

Close=pd.DataFrame()
#Close.index=c000001.index
for index,row in sz50s.iterrows():
    data=ls.read_hit_data(row['code'])
    #Close.index=data.index
    Close[row['code']]=data['close']

Close=Close.loc[:,['600958','601788']]
Close=Close.dropna(axis=0)    
trade=Close[startDate:endDate]

df=pd.DataFrame(columns=['date','alpha','beta','p-value','mu','sd','CoSpreadT','prcLevel','xz'])

alpha,beta,p,mu,sd,CoSpreadT,prcLevel=0.0,0.0,0.0,0.0,0.0,0.0,0.0

for index,row in trade.iterrows(): 
    #计算前6个月符合配对交易的规则的
    delta = dt.timedelta(days=365)
    six_months_ago = index - delta
    s=six_months_ago.strftime('%Y-%m-%d')
    e=index.strftime('%Y-%m-%d')
    firstPeriod=s+":"+e
    
    CloseF=Close[firstPeriod.split(':')[0]:firstPeriod.split(':')[1]]
    dis=(pt.Cointegration(CloseF.iloc[:,0],CloseF.iloc[:,1]))
    
    if(dis):
        alpha=dis[0]
        beta=dis[1]
        p=dis[2]
        priceAt=(Close.loc[index,:][0])
        priceBt=(Close.loc[index,:][1])
        CoSpreadT=np.log(priceBt)-beta*np.log(priceAt)-alpha
        spreadf=pt.CointegrationSpread(Close.iloc[:,0],Close.iloc[:,1],firstPeriod,firstPeriod)
        mu=np.mean(spreadf)
        sd=np.std(spreadf)
        level=(float('-inf'),mu-2.5*sd,mu-1.5*sd,mu-0.2*sd,mu+0.2*sd,mu+1.5*sd,mu+2.5*sd,float('inf'))
        prcLevel=pd.cut(CoSpreadT,level,labels=False)-3
        
        df.loc[df.shape[0]+1]={'date':index,
                          'alpha':alpha,'beta':beta,'p-value':p,'mu':mu,'sd':sd,
                          'CoSpreadT':CoSpreadT,'prcLevel':prcLevel,'xz':1}
    else:
        df.loc[df.shape[0]+1]={'date':index,
                  'alpha':alpha,'beta':beta,'p-value':p,'mu':mu,'sd':sd,
                  'CoSpreadT':CoSpreadT,'prcLevel':prcLevel,'xz':0}
        
def TradeSig(prcLevel):
    n=len(prcLevel)
    signal=np.zeros(n)
    for i in range(1,n):
        if prcLevel[i-1]==1 and prcLevel[i]==2:#上穿建
            signal[i]=2
        elif prcLevel[i-1]==-1 and prcLevel[i]==-2:#下穿建
            signal[i]=-2
        elif prcLevel[i-1]>=1 and prcLevel[i]==0:#平仓线
            signal[i]=1
        elif prcLevel[i-1]<=-1 and prcLevel[i]==0:#下平仓
            signal[i]=-1
        elif prcLevel[i-1]<=2 and prcLevel[i]==3:#关系脱离平仓
            signal[i]=3
        elif prcLevel[i-1]>=-2 and prcLevel[i]==-3:#关系脱离平仓
            signal[i]=-3
    return(signal)


prcLevel=list(df['prcLevel'])
 
signal=TradeSig(prcLevel)
position=[signal[0]]
ns=len(signal)



for i in range(1,ns):
    position.append(position[-1])
    if signal[i]!=0:
        position[i]=signal[i]

position=pd.Series(position,index=trade.index)

'''
1.按均衡方式持股 0.5 0.5的比例方式
2然后在价差过大时进行仓位调整，处理掉估值较高的股票,购入股价较低的股票
3.在价位回复正常后，重新按仓位持股 
'''
def Trade(priceX,priceY,position):
    n=len(position)
    money=2000
    cash=[0]
    beta=0.5
    shareY=pd.Series(np.zeros(n),index=position.index)
    shareX=pd.Series(np.zeros(n),index=position.index)
    shareX[0]=(money*beta)/priceX[0]
    shareY[0]=(money*(1-beta))/priceY[0];
    for i in range(1,n):
        shareX[i]=(shareX[i-1])
        shareY[i]=(shareY[i-1])
        cash.append(cash[i-1])
        if(position[i-1]<2 and position[i]==2):#卖出Y股,钱全部买X股
            shareY[i]=0
            shareX[i]=(cash[i-1]+shareY[i-1]*priceY[i]+shareX[i-1]*priceX[i])/priceX[i]
            cash[i]=0
        elif(position[i-1]>-2 and position[i]==-2):#卖出X，钱全部买Y股
            shareX[i]=0
            shareY[i]=(cash[i-1]+shareX[i-1]*priceX[i]+shareY[i-1]*priceY[i])/priceY[i]
            cash[i]=0
        elif(abs(position[i-1])!=1 and abs(position[i])==1):#重新调整持股比例
            now_money=cash[i-1]+shareX[i-1]*priceX[i]+shareY[i-1]*priceY[i]
            shareX[i]=(now_money*beta)/priceX[i];
            shareY[i]=(now_money*(1-beta))/priceY[i];
            cash[i]=0
        '''
        elif(abs(position[i])==3):
            shareX[i]=0
            shareY[i]=0
            cash[i]=cash[i-1]+shareX[i-1]*priceX[i]+shareY[i-1]*priceY[i]
            '''

    cash=pd.Series(cash,index=position.index)
    asset=cash+shareY*priceY+shareX*priceX
    account=pd.DataFrame({'Position':position,'ShareY':shareY,'ShareX':shareX,
                          'Cash':cash,'Asset':asset})
    return(account)
            
account=Trade(trade.iloc[:,0],trade.iloc[:,1],position)
#account.iloc[:,[0,1,3,4]].plot(style=['--','-',':'])   

account['priceX']=(2000/trade.iloc[0,0])*trade.iloc[:,0]
account['priceY']=(2000/trade.iloc[0,1])*trade.iloc[:,1]

account.loc[:,['Asset','priceX','priceY','ShareX','ShareY']].plot()
    