# aorder
分析回测或实盘订单的工具


目前对接了vnpy的回测，需要在https://github.com/vnpy/vnpy/blob/16c616ece1597a5766bf2fb3529f5789958330b6/vnpy/trader/app/ctaStrategy/ctaBacktesting.py#L781
处添加一行代码`['resultList'] = resultList`

效果图：
![](https://github.com/JaysonAlbert/aorder/blob/master/aorder/fig.png)


## 图解：

1. 其中，红色三角做多，绿色三角做空，蓝色圆圈平仓


2. 从上到下依次为，k线图，成交量图，区间控制图，rsi指标图，atr指标图，ma-atr指标图，后三个指标图可以自定义。


3. 主图指标画在k线上，非主图指标另开小图。


4. 左边的滑块控制显示的下单的范围，如果勾选large than，则显示pnl大于某一值的下单，否则显示pnl小于某一值的下单。
