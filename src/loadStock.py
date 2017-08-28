# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 14:18:15 2017

@author: 53771
"""
import pandas as pd
import tushare as ts

def save_hist_data(code):
    data=ts.get_k_data(code,start='2014-01-01')
    data.to_csv("./stock/"+code+'.csv')
    return data
    
def read_hit_data(code):
    try:
        df=pd.read_csv('./stock/'+code+'.csv',index_col='date')
        df.index=pd.to_datetime(df.index)
        df.sort_index(inplace=True)
    except IOError:
        df=save_hist_data(code)
    return df