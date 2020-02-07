#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 15:48:36 2020

@author: samoaa
"""

import pandas as pd 
df = pd.read_csv('data.csv',delimiter=';')
df_sample = df[['code_churn','authors', 'time']]
df_sample['time'] = pd.to_datetime(df_sample['time'])
df_sample['time'] = df_sample['time'].dt.date
df_sample['week'] =0
for i in range(len(df_sample)):
    df_sample['week'][i]= df_sample['time'][i].isocalendar()[1]
    
df_agg = df_sample.groupby('week')['code_churn'].sum()
df_agg[df_agg < 0] = 0

import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy.stats as stats
# histogram
plt.bar(df_agg.index,df_agg)
# qq plot 
fig = sm.qqplot(df_agg, stats.t, distargs=(4,))
plt.show()
