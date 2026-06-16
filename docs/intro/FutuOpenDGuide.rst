.. note::

  Futu OpenAPI 文档已于2020年10月16日全新升级，请移步至 `新文档 <https://openapi.futunn.com/futu-api-doc/>`_

  旧的github文档将不再更新，并于2020年11月16日正式停止访问。

=================
FutuOpenD使用说明
=================

基本介绍
----------

FutuOpenD是futu-api的网关程序，运行于客户本机或服务器，负责中转协议请求到富途后台，并将处理后的数据返回给协议请求连接。

FutuOpenD目前提供两种安装执行形式，用户可根据自身需求选择任一方式。

1. 命令行形式：提供命令行执行程序，需自行进行部分配置，适合熟悉度高或无界面化需求的用户；
2. 可视化形式：提供界面化应用程序，操作便捷，尤其适合入门用户。

下载安装
----------

方式1：`富途官网下载 <https://www.futunn.com/download/openAPI>`_

FutuOpenD配置
--------------

命令行FutuOpenD启动配置文件使用XML格式。

核心配置项包括：

- `ip`：监听地址
- `api_port`：API 协议接收端口
- `push_proto_type`：PB/Json 推送格式
- `rsa_private_key`：RSA 私钥路径
- `login_account`：登录帐号
- `login_pwd` / `login_pwd_md5`：登录密码
- `log_level`：日志级别
- `simulate_trade`：是否启用模拟交易
- `websocket_ip` / `websocket_port`：WebSocket 服务监听

启动命令行参数
---------------

传参格式：`-key=value`

例如：

.. code-block:: bash

    FutuOpenD.exe -login_account=100000 -login_pwd=123456 -lang=en
