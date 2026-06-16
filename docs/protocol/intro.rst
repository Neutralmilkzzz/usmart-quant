.. note::

  Futu OpenAPI 文档已于2020年10月16日全新升级，请移步至 `新文档 <https://openapi.futunn.com/futu-api-doc/>`_ 

  旧的github文档将不再更新，并于2020年11月16日正式停止访问。

协议接口
====================
+ FutuOpenD是futu-api项目的网关客户端，在本机或云端成功运行后，第三方应用即可通过约定的TCP协议与之通讯，从而达到调用指定行情和交易接口的目的。
+ py-futu-api 可以简化在python编程上协议通讯的复杂度，其他语言接口正在陆续开发中……

特点
-------

+ 基于TCP传输协议实现，稳定高效。
+ 支持protobuf/json两种协议格式， 灵活接入。
+ 协议设计支持加密、数据校验及回放功击保护，安全可靠。

协议请求流程
-------------

* 建立连接
* 初始化连接
* 请求数据或接收推送数据
* 定时发送 KeepAlive 保持连接

协议头结构
~~~~~~~~~~~~~~~

.. code-block:: bash

    struct APIProtoHeader
    {
        u8_t szHeaderFlag[2];
        u32_t nProtoID;
        u8_t nProtoFmtType;
        u8_t nProtoVer;
        u32_t nSerialNo;
        u32_t nBodyLen;
        u8_t arrBodySHA1[20];
        u8_t arrReserved[8];
    };

==============
字段             说明
==============
szHeaderFlag     包头起始标志，固定为“FT”
nProtoID         协议ID
nProtoFmtType    协议格式类型，0为Protobuf格式，1为Json格式
nProtoVer        协议版本，用于迭代兼容, 目前填0
nSerialNo        包序列号，用于对应请求包和回包, 要求递增
nBodyLen         包体长度
arrBodySHA1      包体原始数据(解密后)的SHA1哈希值
arrReserved      保留8字节扩展
==============
