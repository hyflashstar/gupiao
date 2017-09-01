# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 11:13:15 2017

@author: 53771
"""

# 导入画图蜡烛图所需模块
from matplotlib.dates import DateFormatter
from matplotlib.dates import WeekdayLocator
from matplotlib.dates import MONDAY
from matplotlib.dates import DayLocator
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import date2num
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# 定义画图函数
def pandas_candlestick_ohlc(dat,stick='day',otherseries=None):
    """
    参数dat：pandas DataFrame对象采用datetime64指数，和浮点数列
    “开盘价”，“最高价”，“收盘价”，“最低价”
    参数stick：一个字符串或数字只是的时间段覆盖单一的蜡杆。有效
    地字符串输入包括“day”，“week”，“month”，“year”（默认是day）
    和任何数字输入，该数字表明一段时间内包括的交易日
    参数otherseries：一个可迭代的，它将被强制转换为一个列表，包含dat包
    含的其他series将被回执为线条的列
    这将显示一个存储在dat中的股票数据的日本蜡烛K线图
    """
    mondays = WeekdayLocator(MONDAY) # 每周一的主要刻度
    alldays = DayLocator()  # 每周日的次要此刻度
    dayFormatter = DateFormatter("%d")
    
    # 创建一个新的DataFrame，包含按色呼入制定的每个阶段的OHLC数据
    transdat = dat.loc[:,["open","high","low","close"]]
    if type(stick) == str:
        if stick == "day":
            plotdat = transdat
            stick = 1
        elif stick in ['week','month','year']:
            if stick == 'week':
                transdat['week'] = pd.to_datetime(transdat.index).map(
                    lambda x: x.isocalendar()[1])  #确定周 
            elif stick == 'month':
                transdat['month'] = pd.to_datetime(transdat.index).map(
                    lambda x: x.month)  # 确定月
            transdat['year'] = pd.to_datetime(transdat.index).map(
                lambda x: x.isocalendar()[0])   # 确定年
            
            # 按年和其他适当变量分组
            grouped = transdat.groupby(list(set(['year',stick])))
            
            # 创建将要包含绘图的空数据框
            plotdat = pd.DataFrame({"open":[],"high":[],"low":[],"close":[]})
            for name, group in grouped:
                plotdat = plotdat.append(pd.DataFrame({"open":group.iloc[0,0],
                                                     "high":max(group.high),
                                                     "low":min(group.low),
                                                     "close":group.iloc[-1,3]},
                                                     index = [group.index[0]]))
            if stick == "week":
                stick = 5
            elif stick == "month": 
                stick = 30
            elif stick == "year":
                stick = 365
    elif type(stick) == int and stick >=1:
        transdat["stick"] = [np.float(i/stick) for i in range(len(transdat.index))]
        grouped = transdat.groupby("stick")

        # 创建将要包含绘图的空数据框
        plotdat = pd.DataFrame({"open":[],"high":[],"low":[],"close":[]})
        grouped = transdat.groupby('stick')
        for name,group in grouped:
            plotdat = plotdat.append(pd.DataFrame({"open": group.iloc[0,0],
                                                  "high": max(group.high),
                                                  "low": min(group.low),
                                                  "close": group.iloc[-1,3]},
                                                 index = [group.index[0]]))
    else:
        raise ValueError('Valid inputs to argument "stick" include the strings "day","week","month","year",or a positive integer')

    # 设置plot参数，包括用绘制的轴线对象ax
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    if plotdat.index[-1] - plotdat.index[0] < pd.Timedelta('730 days'):
        weekFormatter = DateFormatter("%b %d")  # 例如，1月12
        ax.xaxis.set_major_locator(mondays)
        ax.xaxis.set_minor_locator(alldays)
    else:
        weekFormatter = DateFormatter("%b %d,%Y")
    ax.xaxis.set_major_formatter(weekFormatter)
    ax.grid(True)

    # 创建K线图
    candlestick_ohlc(ax,list(zip(list(date2num(plotdat.index.tolist())),
                                 plotdat["open"].tolist(),
                                 plotdat["high"].tolist(),
                                 plotdat["low"].tolist(),
                                 plotdat["close"].tolist())),
                     colorup = "r",colordown='g')

    # 绘制其他series（如移动平均线）作为线
    if otherseries != None:
        if type(otherseries) != list:
            otherseries = [otherseries]
        dat.loc[:,otherseries].plot(ax=ax,lw=1.3,grid=True)

    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(),rotation=45,
            horizontalalignment='right')
    plt.show()