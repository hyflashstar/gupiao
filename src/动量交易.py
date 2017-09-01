# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 18:05:30 2017

@author: 53771
"""
import loadStock as ls
import tushare as ts
from datetime import datetime
import matplotlib.pyplot as plt
import pandas_candlestick_ohlc as pohlc
import pandas as pd


Vanke=ls.read_hit_data('000001')