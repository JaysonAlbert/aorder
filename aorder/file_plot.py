# encoding: UTF-8

from __future__ import division

from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME
import pandas as pd
from utils import plot_candles1

file_name = 'bu_zf.csv'

columns = ['volume', 'entryDate','entryTime', 'entryPrice', 'exitDate','exitTime', 'exitPrice','absPos'
       ,'pnl', 'commission']
orders = pd.read_csv(file_name,header=None,names=columns, dtype={'entryDate':str,
                                                                  'entryTime':str,
                                                                  'exitDate':str,
                                                                  'exitTime':str})

orders['entryDt'] = pd.to_datetime(orders['entryDate'] + ' ' + orders['entryTime'])
orders['exixtDt'] = pd.to_datetime(orders['exitDate'] + ' ' + orders['exitTime'])

engine = BacktestingEngine()
engine.setBacktestingMode(engine.BAR_MODE)

engine.setStartDate(str(orders.entryDate.values[0]))

engine.setDatabase(MINUTE_DB_NAME,file_name.split('_')[0] + '0000')

engine.loadHistoryData()

pricing = pd.DataFrame(list(engine.dbCursor))

plot_candles1(pricing, volume_bars=True, orders=orders)