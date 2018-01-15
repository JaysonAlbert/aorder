# aorder
分析回测或实盘订单的工具


目前对接了vnpy的回测，需要在https://github.com/vnpy/vnpy/blob/16c616ece1597a5766bf2fb3529f5789958330b6/vnpy/trader/app/ctaStrategy/ctaBacktesting.py#L781
处添加一行代码`['resultList'] = resultList`
