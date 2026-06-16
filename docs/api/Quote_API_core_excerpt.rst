.. note::

  Futu OpenAPI 文档已于2020年10月16日全新升级，请移步至 `新文档 <https://openapi.futunn.com/futu-api-doc/>`_

  旧的github文档将不再更新，并于2020年11月16日正式停止访问。

========
行情API 核心摘录
========

这份文件是我从官方 `Quote_API.rst` 中抓下来的第一批核心内容，优先保留你做美股因子挖掘最常用的接口说明。

重点接口
--------

- `get_stock_basicinfo`
- `request_history_kline`
- `get_market_snapshot`
- `get_rt_data`
- `get_plate_stock`
- `get_plate_list`
- `subscribe`
- `unsubscribe`

`request_history_kline`
~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: request_history_kline(self, code, start=None, end=None, ktype=KLType.K_DAY, autype=AuType.QFQ, fields=[KL_FIELD.ALL], max_count=1000, page_req_key=None, extended_time=False)

获取K线，不需要事先下载K线数据。

- `code`：股票代码
- `start` / `end`：时间范围
- `ktype`：K线类型
- `autype`：复权类型
- `fields`：返回字段
- `max_count`：单次最大返回点数
- `page_req_key`：分页 key
- `extended_time`：是否允许美股盘前盘后数据

返回列包括：

- `code`
- `time_key`
- `open`
- `close`
- `high`
- `low`
- `pe_ratio`
- `turnover_rate`
- `volume`
- `turnover`
- `change_rate`
- `last_close`

`get_market_snapshot`
~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_market_snapshot(self, code_list)

获取市场快照。

常用返回列包括：

- `code`
- `update_time`
- `last_price`
- `open_price`
- `high_price`
- `low_price`
- `prev_close_price`
- `volume`
- `turnover`
- `turnover_rate`
- `pe_ratio`
- `pb_ratio`
- `pe_ttm_ratio`
- `ask_price`
- `bid_price`
- `ask_vol`
- `bid_vol`
- `pre_price`
- `after_price`

`get_stock_basicinfo`
~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_stock_basicinfo(self, market, stock_type=SecurityType.STOCK, code_list=None)

获取指定市场中特定类型的股票基本信息。

常用字段：

- `code`
- `name`
- `lot_size`
- `stock_type`
- `listing_date`
- `stock_id`
- `delisting`

`get_plate_list`
~~~~~~~~~~~~~~~~

..  py:function:: get_plate_list(self, market, plate_class)

获取板块集合下的子板块列表。

`get_plate_stock`
~~~~~~~~~~~~~~~~~

..  py:function:: get_plate_stock(self, plate_code, sort_field=SortField.CODE, ascend=True)

获取特定板块下的股票列表。

对美股你现在最有用的是文档里给出的这个板块代码：

- `US.USAALL`：全部美股

`subscribe`
~~~~~~~~~~~

..  py:function:: subscribe(self, code_list, subtype_list, is_first_push=True, subscribe_push=True, is_detailed_orderbook=False)

订阅实时数据。

`unsubscribe`
~~~~~~~~~~~~~

..  py:function:: unsubscribe(self, code_list, subtype_list, unsubscribe_all=False)

取消订阅。
