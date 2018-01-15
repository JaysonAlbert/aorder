# encoding: UTF-8

"""
展示如何执行策略回测。
"""

from __future__ import division

from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME
import pandas as pd
from utils import plot_candles, plot_candles1
import talib
import numpy as np

if __name__ == '__main__':
    from vnpy.trader.app.ctaStrategy.strategy.strategyAtrRsi import AtrRsiStrategy

    # 创建回测引擎
    engine = BacktestingEngine()

    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.BAR_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20170601')

    # 设置产品相关参数
    engine.setSlippage(0.2)  # 股指1跳
    engine.setRate(0.3 / 10000)  # 万0.3
    engine.setSize(300)  # 股指合约大小
    engine.setPriceTick(0.2)  # 股指最小价格变动

    # 设置使用的历史数据库
    engine.setDatabase(MINUTE_DB_NAME, 'rb0000')

    # 在引擎中创建策略对象
    d = {'rsiLength': 4, 'atrLength': 25}
    engine.initStrategy(AtrRsiStrategy, d)

    engine.loadHistoryData()

    # 开始跑回测

    engine.loadHistoryData()

    engine.runBacktesting()

    # 显示回测结果
    engine.showBacktestingResult()

    # analysis
    engine.loadHistoryData()

    orders = pd.DataFrame([i.__dict__ for i in engine.calculateBacktestingResult()['resultList']])

    pricing = pd.DataFrame(list(engine.dbCursor))

    atr = talib.ATR(pricing.high.values, pricing.low.values, pricing.close.values, 25)

    atr_ma = pd.DataFrame(atr).rolling(25).mean()[0].values

    technicals = {
        'rsi': talib.RSI(pricing.close.values, 4),
        'atr': atr,
        'atr-ma': atr_ma
    }

    plot_candles1(pricing, volume_bars=True, orders=orders, technicals=technicals)
