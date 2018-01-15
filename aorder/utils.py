import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_candles(pricing, title=None, volume_bars=False, color_function=None, technicals=None):
    """ Plots a candlestick chart using quantopian pricing data.

    Author: Daniel Treiman

    Args:
      pricing: A pandas dataframe with columns ['open_price', 'close_price', 'high', 'low', 'volume']
      title: An optional title for the chart
      volume_bars: If True, plots volume bars
      color_function: A function which, given a row index and price series, returns a candle color.
      technicals: A list of additional data series to add to the chart.  Must be the same length as pricing.
    """

    def default_color(index, open_price, close_price, low, high):
        return 'r' if open_price[index] > close_price[index] else 'g'

    color_function = color_function or default_color
    technicals = technicals or []
    open_price = pricing['open']
    close_price = pricing['close']
    low = pricing['low']
    high = pricing['high']
    oc_min = pd.concat([open_price, close_price], axis=1).min(axis=1)
    oc_max = pd.concat([open_price, close_price], axis=1).max(axis=1)

    if volume_bars:
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax1 = plt.subplots(1, 1)
    if title:
        ax1.set_title(title)
    x = np.arange(len(pricing))
    candle_colors = [color_function(i, open_price, close_price, low, high) for i in x]
    candles = ax1.bar(x, oc_max - oc_min, bottom=oc_min, color=candle_colors, linewidth=0)
    lines = ax1.vlines(x + 0.4, low, high, color=candle_colors, linewidth=1)
    ax1.xaxis.grid(False)
    ax1.xaxis.set_tick_params(which='major', length=3.0, direction='in', top='off')
    # Assume minute frequency if first two bars are in the same day.
    frequency = 'minute' if (pricing.index[1] - pricing.index[0]).days == 0 else 'day'
    time_format = '%d-%m-%Y'
    if frequency == 'minute':
        time_format = '%H:%M'
    # Set X axis tick labels.
    plt.xticks(x, [date.strftime(time_format) for date in pricing.index], rotation='vertical')
    for indicator in technicals:
        ax1.plot(x, indicator)

    if volume_bars:
        volume = pricing['volume']
        volume_scale = None
        scaled_volume = volume
        if volume.max() > 1000000:
            volume_scale = 'M'
            scaled_volume = volume / 1000000
        elif volume.max() > 1000:
            volume_scale = 'K'
            scaled_volume = volume / 1000
        ax2.bar(x, scaled_volume, color=candle_colors)
        volume_title = 'Volume'
        if volume_scale:
            volume_title = 'Volume (%s)' % volume_scale
        ax2.set_title(volume_title)
        ax2.xaxis.grid(False)
    plt.show()


def plot_candles1(df, *args, **kwargs):
    import pandas as pd
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtGui
    import numpy as np

    class BarGraph(pg.BarGraphItem):
        def __init__(self, **opts):
            super(BarGraph, self).__init__()

            self.df = opts.pop('df', None)

        def mouseClickEvent(self, event):
            print(event)

    orders = kwargs.pop('orders', None)
    technicals = kwargs.pop('technicals', {})

    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()
    label = pg.LabelItem(justify='right')
    win.addItem(label)

    p1 = win.addPlot(row=1, col=0)
    p3 = win.addPlot(row=2, col=0)
    p2 = win.addPlot(row=4, col=0)
    p3.setXLink(p1)

    win.ci.layout.setRowStretchFactor(1, 10)
    win.ci.layout.setRowStretchFactor(2, 0.1)

    region = pg.LinearRegionItem()
    region.setZValue(10)

    p2.addItem(region, ignoreBounds=True)

    # pg.dbg()
    # p1.setAutoVisible(y=True)

    brushes = (df.close - df.open).apply(lambda x: 'r' if x >= 0 else 'g')

    scale = 1
    length = len(df.index)
    x1 = np.arange(length) * scale
    width1 = scale * 0.8
    width2 = scale * 0.01

    bg = pg.BarGraphItem(x=x1, y0=df.open, y1=df.close, width=width1, brushes=brushes)
    bg1 = pg.BarGraphItem(x=x1, y0=df.low, y1=df.high, width=width2, brushes=brushes)
    p1.addItem(bg)
    p1.addItem(bg1)

    if orders is not None and not orders.empty:
        entryXs = df.datetime.searchsorted(orders.entryDt)
        entryYs = orders.entryPrice
        exitXs = df.datetime.searchsorted(orders.exitDt)
        exitYs = orders.exitPrice
        p1.plot(entryXs[orders.volume == 1],
                entryYs[orders.volume == 1].values,
                pen=None,
                symbolBrush=(255, 0, 0),
                symbol='t')
        p1.plot(entryXs[orders.volume == -1],
                entryYs[orders.volume == -1].values,
                pen=None,
                symbolBrush=(0, 255, 0),
                symbol='t')
        p1.plot(exitXs,
                exitYs.values,
                pen=None,
                symbolBrush=(0, 0, 255),
                )

    main_low = df.low.min()
    if len(technicals) != 0:
        for key,tech in technicals.iteritems():
            tech = np.nan_to_num(tech)
            if main_low > tech.max():
                win.nextRow()
                tmp = win.addPlot(title=key)
                tmp.setXLink(p1)
                tmp.plot(x1,tech,)
            else:
                p1.plot(x1,tech)

    vol = pg.BarGraphItem(x=x1, width=width1, height=df.volume, brushes=brushes)
    p3.addItem(vol)

    bg3 = pg.BarGraphItem(x=x1, y0=df.open, y1=df.close, width=width1, brushes=brushes)
    bg4 = pg.BarGraphItem(x=x1, y0=df.low, y1=df.high, width=width2, brushes=brushes)
    p2.addItem(bg3)
    p2.addItem(bg4)

    def update():
        region.setZValue(10)
        minX, maxX = region.getRegion()
        iminX = int(minX)
        if iminX < 0:
            iminX = 0
        imaxX = int(maxX)
        if imaxX < 0:
            imaxX = 0.1 * length

        if imaxX > length:
            imaxX = length
        if iminX > length:
            iminX = length * 0.9
        tmp = df[iminX:imaxX]

        p1.setXRange(minX, maxX, padding=0)
        p1.setYRange(tmp.low.min(), tmp.high.max(), padding=0)
        p3.setYRange(0, tmp.volume.max(), padding=0)

    region.sigRegionChanged.connect(update)

    def updateRegion(window, viewRange):
        rgn = viewRange[0]
        region.setRegion(rgn)

    p1.sigRangeChanged.connect(updateRegion)

    region.setRegion([0.1 * length, 0.2 * length])

    # cross hair
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    p1.addItem(vLine, ignoreBounds=True)
    p1.addItem(hLine, ignoreBounds=True)

    vb = p1.vb

    def mouseMoved(evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if p1.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(df):
                label.setText(
                    "<span style='color: red'>open=%0.1f, <span style='color: red'>high=%0.1f</span>, <span style='color: red'>low=%0.1f</span>,  <span style='color: red'>close=%0.1f</span>,   <span style='color: red'>volume=%0.1f</span>" % (
                        df.iloc[index].open, df.iloc[index].high, df.iloc[index].low, df.iloc[index].close,
                        df.iloc[index].volume))
            vLine.setPos(mousePoint.x())
            hLine.setPos(mousePoint.y())

    proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
