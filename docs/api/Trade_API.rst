.. note::

  Futu OpenAPI 文档已于2020年10月16日全新升级，请移步至 `新文档 <https://openapi.futunn.com/futu-api-doc/>`_

  旧的github文档将不再更新，并于2020年11月16日正式停止访问。

===========
交易API
===========

一分钟上手
==============

如下范例，创建api交易对象，先调用unlock_trade对交易解锁，然后调用place_order下单，以700.0价格，买100股腾讯00700，最后关闭对象。

注意交易对象区分港股美股。

.. code:: python

    from futu import *
    pwd_unlock = '123456'
    trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
    print(trd_ctx.unlock_trade(pwd_unlock))
    print(trd_ctx.place_order(price=700.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY))
    trd_ctx.close()

接口类对象
==============

OpenHKTradeContext（港股交易）、OpenUSTradeContext（美股交易）、OpenHKCCTradeContext(A股通)、OpenCNTradeContext（A股交易）、OpenFutureTradeContext（期货交易）-交易接口类

核心接口：

- `get_acc_list`
- `unlock_trade`
- `accinfo_query`
- `position_list_query`
- `place_order`
- `order_list_query`
- `modify_order`
- `deal_list_query`
- `history_order_list_query`
- `history_deal_list_query`
- `acctradinginfo_query`

其中对你做美股量化先期最可能相关的是：

1. `get_acc_list`
2. `unlock_trade`
3. `accinfo_query`
4. `position_list_query`
5. `place_order`
