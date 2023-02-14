# GPT-Lark

将OpenAI GPT接入飞书机器人，不依赖机器人框架，单文件实现的多线程飞书机器人与WebHook消息订阅。

## 使用
0. 在飞书开放平台申请机器人应用，订阅消息相关事件。

1. 将`api_config_example.json`文件改名为`api_config.json`，并按照示例配置飞书后台信息、服务器信息、GPT API。

2. 使用pip安装依赖 `python3.x -m pip install aiohttp openai`。

3. 运行 `python3.x ./LarkGPT_webhook.py`。

4. 在运行的情况下，完成飞书平台`请求地址配置`。

### 飞书机器人信息

``` json
"Bot":{
        "profile":{
            "app_id":"",        
            "app_secret":""
        },
        "bot_api_token":""      #Verification Token
}
```
前两者可以在`凭证与基础信息`中找到，`Verification Token`在`事件订阅`中。

### 服务器信息

``` json
"WebHook":{
        "port": 6666,
        "route": "/"
    }
```
默认的请求地址是`http://ip:port/route`，在默认情况下为`http://ip:6666/`。

### GPT API

``` json
"Api":[
        {
            "api_token": "",
            "owner": "",
            "available": true
            
        },
        {
            "api_token": "",
            "owner": "",
            "available": true
        },
        {
            "api_token": "",
            "owner": "",
            "available": true
        }
    ]

```
将从OpenAI申请到的GPT token填入`api_token`字段，可以将`available`设置为false以暂停使用某个token，`owner`目前仅做标识用。

可以填入多个token，以提升并发服务能力。

## 功能概述

项目通过单个文件，实现了飞书WebHook消息订阅，请求地址配置验证。
在部署完毕后，用户通过与组织内的机器人单聊即可调用GPT.

