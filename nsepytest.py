# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 12:30:19 2015
@author: SW274998
"""

from nsepy.archives import get_price_history_csv

with open('sbin.csv','w') as fp:
    get_price_history_csv(fp, 'SBIN', start = '01-01-2013', end = '31-12-2013')

#with open('LT.csv','w') as fp:
#    get_price_history_csv(fp, 'LT', start = '01-01-2014', end = '20-01-2014')
