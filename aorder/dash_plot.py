# -*- coding: utf-8 -*-

from __future__ import division

import dash
import dash_core_components as dcc
import dash_html_components as html

"""
展示如何执行策略回测。
"""

from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME
import pandas as pd
from utils import plot_candles, plot_trade
import talib
import numpy as np

def generate_graph(df):
    INCREASING_COLOR = '#17BECF'
    DECREASING_COLOR = '#7F7F7F'

    data = [dict(
        type='candlestick',
        open=df.Open,
        high=df.High,
        low=df.Low,
        close=df.Close,
        x=df.index,
        yaxis='y2',
        name='GS',
        increasing=dict(line=dict(color=INCREASING_COLOR)),
        decreasing=dict(line=dict(color=DECREASING_COLOR)),
    )]

    layout = dict()

    fig = dict(data=data, layout=layout)

    fig['layout'] = dict()
    fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
    fig['layout']['xaxis'] = dict(rangeselector=dict(visible=True))
    fig['layout']['yaxis'] = dict(domain=[0, 0.2], showticklabels=False)
    fig['layout']['yaxis2'] = dict(domain=[0.2, 0.8])
    fig['layout']['legend'] = dict(orientation='h', y=0.9, x=0.3, yanchor='bottom')
    fig['layout']['margin'] = dict(t=40, b=40, r=40, l=40)

    rangeselector = dict(
        visibe=True,
        x=0, y=0.9,
        bgcolor='rgba(150, 200, 250, 0.4)',
        font=dict(size=13),
        buttons=list([
            dict(count=1,
                 label='reset',
                 step='all'),
            dict(count=1,
                 label='1yr',
                 step='year',
                 stepmode='backward'),
            dict(count=3,
                 label='3 mo',
                 step='month',
                 stepmode='backward'),
            dict(count=1,
                 label='1 mo',
                 step='month',
                 stepmode='backward'),
            dict(step='all')
        ]))

    fig['layout']['xaxis']['rangeselector'] = rangeselector

    def movingaverage(interval, window_size=10):
        window = np.ones(int(window_size)) / float(window_size)
        return np.convolve(interval, window, 'same')

    mv_y = movingaverage(df.Close)
    mv_x = list(df.index)

    # Clip the ends
    mv_x = mv_x[5:-5]
    mv_y = mv_y[5:-5]

    fig['data'].append(dict(x=mv_x, y=mv_y, type='scatter', mode='lines',
                            line=dict(width=1),
                            marker=dict(color='#E377C2'),
                            yaxis='y2', name='Moving Average'))

    colors = []

    for i in range(len(df.Close)):
        if i != 0:
            if df.Close[i] > df.Close[i - 1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)

    fig['data'].append(dict(x=df.index, y=df.Volume,
                            marker=dict(color=colors),
                            type='bar', yaxis='y', name='Volume'))

    def bbands(price, window_size=10, num_of_std=5):
        rolling_mean = price.rolling(window=window_size).mean()
        rolling_std = price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return rolling_mean, upper_band, lower_band

    bb_avg, bb_upper, bb_lower = bbands(df.Close)

    fig['data'].append(dict(x=df.index, y=bb_upper, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#ccc'), hoverinfo='none',
                            legendgroup='Bollinger Bands', name='Bollinger Bands'))

    fig['data'].append(dict(x=df.index, y=bb_lower, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#ccc'), hoverinfo='none',
                            legendgroup='Bollinger Bands', showlegend=False))

    return fig

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

    df = pd.DataFrame(list(engine.dbCursor)).rename(
        columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}).set_index('datetime')

    # df.index = map(lambda x: x.strftime("%Y%m%d %H:%M:%S"), df.datetime)

    app = dash.Dash()

    app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='example-graph',
            figure=generate_graph(df[:1000])
        )
    ])

    app.run_server(debug=True)
