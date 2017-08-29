# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 11:27:56 2017

@author: 53771
"""

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


formPeriod='2017-01-01:2017-06-01'
#tradePeriod='2017-01-01:2017-06-01'
tradePeriod='2017-06-01:2017-08-25'

priceA=Close['601186']
priceB=Close['601211']

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
        elif prcLevel[i-1]==2 and prcLevel[i]==3:#关系脱离平仓
            signal[i]=3
        elif prcLevel[i-1]==-2 and prcLevel[i]==-3:#关系脱离平仓
            signal[i]=-3
    return(signal)
    
signal=TradeSig(prcLevel)
position=[signal[0]]
ns=len(signal)



for i in range(1,ns):
    position.append(position[-1])
    if signal[i]!=0:
        position[i]=signal[i]

position=pd.Series(position,index=CoSpreadT.index)

'''
1.按均衡方式持股 0.5 0.5的比例方式
2然后在价差过大时进行仓位调整，处理掉估值较高的股票,购入股价较低的股票
3.在价位回复正常后，重新按仓位持股 
'''
def Trade(priceX,priceY,position):
    n=len(position)
    #money=2000
    cash=[2000]
    beta=0.5
    shareY=pd.Series(np.zeros(n),index=position.index)
    shareX=pd.Series(np.zeros(n),index=position.index)
    shareX[0]=0
    shareY[0]=0
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
        elif(abs(position[i-1])!=1 and position[i-1]!=0 and abs(position[i])==1):#重新调整持股比例
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
            
account=Trade(priceAt,priceBt,position)
#account.iloc[:,[0,1,3,4]].plot(style=['--','-',':'])   

account['priceX']=(2000/priceAt[0])*priceAt
account['priceY']=(2000/priceBt[0])*priceBt

account.loc[:,['Asset','priceX','priceY','ShareX','ShareY']].plot()
      
            
            
            
            
            

            
        