# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 15:05:53 2017

@author: 53771
"""

import loadStock as ls
import PairTrading as pairTrading
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


sz50s=ts.get_sz50s()
#sz50s=sz50s[0:2]

Close=pd.DataFrame()
#Close.index=c000001.index
for index,row in sz50s.iterrows():
    data=ls.read_hit_data(row['code'])
    #Close.index=data.index
    Close[row['code']]=data['close']


formPeriod='2015-01-01:2016-01-01'
tradePeriod='2016-01-01:2016-06-30'

priceA=Close['601988']
priceB=Close['600000']

priceAf=priceA[formPeriod.split(':')[0]:formPeriod.split(':')[1]]
priceBf=priceB[formPeriod.split(':')[0]:formPeriod.split(':')[1]]
priceAt=priceA[tradePeriod.split(':')[0]:tradePeriod.split(':')[1]]
priceBt=priceB[tradePeriod.split(':')[0]:tradePeriod.split(':')[1]]

pt=pairTrading.PairTrading()
alpha,beta=pt.Cointegration(priceAf,priceBf)
spreadf=pt.CointegrationSpread(priceA,priceB,formPeriod,formPeriod)
mu=np.mean(spreadf)
sd=np.std(spreadf)

CoSpreadT=np.log(priceBt)-beta*np.log(priceAt)-alpha

CoSpreadT.plot()
plt.title('交易期价差序列（协整配对）')
plt.axhline(y=mu,color='black')
plt.axhline(y=mu+0.2*sd,color='blue',ls='-',lw=2)
plt.axhline(y=mu-0.2*sd,color='blue',ls='-',lw=2)
plt.axhline(y=mu+1.5*sd,color='green',ls='--',lw=2.5)
plt.axhline(y=mu-1.5*sd,color='green',ls='--',lw=2.5)
plt.axhline(y=mu+2.5*sd,color='red',ls="-.",lw=3)
plt.axhline(y=mu-2.5*sd,color='red',ls="-.",lw=3)

level=(float('-inf'),mu-2.5*sd,mu-1.5*sd,mu-0.2*sd,mu+0.2*sd,mu+1.5*sd,mu+2.5*sd,float('inf'))
prcLevel=pd.cut(CoSpreadT,level,labels=False)-3

#prcLevel.plot()


def TradeSig(prcLevel):
    n=len(prcLevel)
    signal=np.zeros(n)
    for i in range(1,n):
        if prcLevel[i-1]==1 and prcLevel[i]==2:#上穿建
            signal[i]=1
        elif prcLevel[i-1]==-1 and prcLevel[i]==-2:#下穿建
            signal[i]=-1
        elif prcLevel[i-1]==1 and prcLevel[i]<1:#平仓线
            signal[i]=2
        elif prcLevel[i-1]==-1 and prcLevel[i]>-1:#下平仓
            signal[i]=-2
        elif prcLevel[i-1]==2 and prcLevel[i]>2:#关系脱离平仓
            signal[i]=3
        elif prcLevel[i-1]==-2 and prcLevel[i]<-2:#关系脱离平仓
            signal[i]=-3
    return(signal)


signal=TradeSig(prcLevel) 
ns=len(signal)
position=[signal[0]]


for i in range(1,ns):
    position.append(position[-1])
    if signal[i]==1:
        position[i]=1
    elif signal[i]==-1:
        position[i]=-1
    elif signal[i]==2 and position[i-1]==1:
        position[i]=0
    elif signal[i]==-2 and position[i-1]==-1:
        position[i]=0
    elif signal[i]==3:
        position[i]=0
    elif signal[i]==-3:
        position[i]=0

position=pd.Series(position,index=CoSpreadT.index)


#A股无法做空，所以只能在价值高估的时候卖出，价值低估时买入，这要求操作的股票要在恒定价值内波动       
def TradeSim(priceX,priceY,position):
    n=len(position)
    shareY=pd.Series(np.zeros(n),index=position.index)
    shareX=pd.Series(np.zeros(n),index=position.index)
    cash=[2000]
    for i in range(1,n):
        shareX[i]=(shareX[i-1])
        shareY[i]=(shareY[i-1])
        cash.append(cash[i-1])
        if position[i-1]==0 and position[i]==1:#卖出X,买入Y
            shareX[i]=0
            shareY[i]=(cash[i-1]+((shareX[i-1]-shareX[i])*priceX[i]))/priceY[i]
            cash[i]=cash[i-1]-(shareY[i]*priceY[i]+shareX[i]*priceX[i])
        elif position[i-1]==0 and position[i]==-1:#买入X,卖出Y
            shareY[i]=0
            shareX[i]=(cash[i-1]+((shareY[i-1]-shareY[i])*priceY[i]))/priceX[i]
            cash[i]=cash[i-1]-(shareY[i]*priceY[i]+shareX[i]*priceX[i])
        elif position[i-1]==1 and position[i]==0:
            shareX[i]=0
            shareY[i]=0
            cash[i]=cash[i-1]+(shareY[i-1]*priceY[i]+shareX[i-1]*priceX[i])
        elif position[i-1]==-1 and position[i]==0:
            shareX[i]=0
            shareY[i]=0
            cash[i]=cash[i-1]+(shareY[i-1]*priceY[i]+shareX[i-1]*priceX[i])
    cash=pd.Series(cash,index=position.index)
    asset=cash+shareY*priceY+shareX*priceX
    account=pd.DataFrame({'Position':position,'ShareY':shareY,'ShareX':shareX,
                          'Cash':cash,'Asset':asset})
    return(account)

account=TradeSim(priceAt,priceBt,position)
account.iloc[:,[0,1,3,4]].plot(style=['--','-',':'])

    
           
   
