# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 14:18:15 2017

@author: 53771
"""
import pandas as pd
import tushare as ts
import fileInfo as fi
import numpy as np

def save_hist_data(code):
    data=ts.get_k_data(code,start='2011-01-01')
    data.to_csv("./stock/"+code+'.csv')
    #data.index=pd.to_datetime(data.index)
    #data.sort_index(inplace=True)
    #return data
    
def read_hit_data(code):
    try:
        df=pd.read_csv('./stock/'+code+'.csv',index_col='date')
        df.index=pd.to_datetime(df.index)
        df.sort_index(inplace=True)
    except IOError:
        save_hist_data(code)
        df=pd.read_csv('./stock/'+code+'.csv',index_col='date')
        df.index=pd.to_datetime(df.index)
        df.sort_index(inplace=True)
    return df


#取得行业信息数据,如果存储的信息超过了一天就重新获取
def read_industry(day=1):
    try:
        if(fi.get_FileModifyTime_betweenNow("./stock/industry.csv").days<day):
            industry=pd.read_csv("./stock/industry.csv",index_col=0,dtype={'code':np.string_})
        else:
            industry=save_industry()
    except IOError:
        industry=save_industry()
    return industry
    

def save_industry():
    industry=ts.get_industry_classified()
    industry.to_csv("./stock/industry.csv",encoding="utf-8")
    return industry
    