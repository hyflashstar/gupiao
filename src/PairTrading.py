# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 20:35:51 2017

@author: 53771
"""

import re
import pandas as pd
import numpy as np
import statsmodels.api as sm
from  arch.unitroot import ADF

class PairTrading:
    def SSD(self,priceX,priceY):
        if priceX is None or priceY is None:
            print('缺少价格序列')
        returnX=(priceX-priceX.shift(1))/priceX.shift(1)[1:]
        returnY=(priceY-priceY.shift(1))/priceY.shift(1)[1:]
        standardX=(returnX+1).cumprod()
        standardY=(returnY+1).cumprod()
        SSD=np.sum((standardX-standardY)**2)
        return SSD
    
    def SSDSpread(self,priceX,priceY):
        if priceX is None or priceY is None:
            print('缺少价格序列')
        returnX=(priceX-priceX.shift(1))/priceX.shift(1)[1:]
        returnY=(priceY-priceY.shift(1))/priceY.shift(1)[1:]
        standardX=(returnX+1).cumprod()
        standardY=(returnY+1).cumprod()
        spread=standardY-standardX
        return spread
    def Cointegration(self,priceX,priceY):
        if priceX is None or priceY is None:
            print('缺少价格序列')
        priceX=np.log(priceX)
        priceY=np.log(priceY)
        results=sm.OLS(priceY,sm.add_constant(priceX)).fit()
        resid=results.resid
        adfSpread=ADF(resid)
        if adfSpread.pvalue>=0.05:
            print('''交易价格不具有协整关系.
                  P-value of ADF text: %f
                  Coefficients of regression:
                  Intercept : %f
                  Beta: %f
                  ''' % (adfSpread.pvalue,results.params[0],results.params[1]))
            return(None)
        else:
            print('''交易价格具有协整关系.
                  P-value of ADF text: %f
                  Coefficients of regression:
                  Intercept : %f
                  Beta: %f
                  ''' % (adfSpread.pvalue,results.params[0],results.params[1])) 
            return(results.params[0],results.params[1],adfSpread.pvalue)
    def CointegrationSpread(self,priceX,priceY,formPeriod,tradePeriod):
        if priceX is None or priceY is None:
            print('缺少价格序列')
        if not(re.fullmatch('\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}',formPeriod) 
        or re.fullmatch('\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}',tradePeriod)):
            print('形成期或交易期错误.')
        formX=priceX[formPeriod.split(':')[0]:formPeriod.split(':')[1]]
        formY=priceY[formPeriod.split(':')[0]:formPeriod.split(':')[1]]
        
        coefficients=self.Cointegration(formX,formY)
        if coefficients is None:
            print ('未形成协整关系，无法配对.')
        else:
            spread=(np.log(priceY[tradePeriod.split(':')[0]:tradePeriod.split(':')[1]])
            -coefficients[0]-coefficients[1]*np.log(priceX[tradePeriod.split(':')[0]:
                tradePeriod.split(':')[1]]))
            return spread
    def calBound(self,priceX,priceY,method,formPeriod,width=1.5):
        if not(re.fullmatch('\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}',formPeriod)):
            print('形成期错误.')
        
        if method=='SSD':
            spread=self.SSDSpread(priceX[formPeriod.split(':')[0]:
                formPeriod.split(':')[1]],
                priceY[formPeriod.split(':')[0]:
                formPeriod.split(':')[1]])
            mu=np.mean(spread)
            sd=np.std(spread)
            UpperBound=mu+width*sd
            LowerBound=mu=width*sd
            return (UpperBound,LowerBound)
        elif method=='Cointegration':
            spread=self.CointegrationSpread(priceX,priceY,formPeriod,formPeriod)
            mu=np.mean(spread)
            sd=np.std(spread)
            UpperBound=mu+width*sd
            LowerBound=mu-width*sd
            return(UpperBound,LowerBound)
        else:
            print('不存在该方法，请选择"SSD"或是"Cointegration"')
        
            
            
            
