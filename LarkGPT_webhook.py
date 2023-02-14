from aiohttp import web
import asyncio
import openai
from threading import Thread, current_thread
# import web
import json
import requests


class Seat:
    numOfSeat = 0

    def __init__(self, api):
        self.api = api
        self.maxToken = 256
        self.engie = "text-davinci-003"
        self.lock = 0

        self.user = None

        Seat.numOfSeat += 1

    def requestGpt(self, promote):
        if self.lock == 1:
            return "请等待..."
        self.lock = 1
        openai.api_key = self.api
        try:
            response = (
                openai.Completion.create(
                    engine=self.engie,
                    prompt=promote,
                    max_tokens=self.maxToken,
                    n=1,
                    stop=None,
                    temperature=0.3,
                )
                .get("choices")[0]
                .text
            )
        except:
            self.lock = 0
            return "[!]Sorry, Problems with OpenAI service, Please try again."
        self.lock = 0
        return response

    def sendBackUser(self, res):
        if (self.user is not None):
            send(self.user, res)



def handle_request(seat, message):
    #print("asking ai")
    # Get the response from OpenAI's GPT-3 API
    response = seat.requestGpt(message)
    #print("got msg from openai:", response)

    # Send the response back to the user
    seat.sendBackUser(response)

    #调整顺序
    seats.insert(0,seats.pop(seats.index(seat)))



async def listen_for_webhook(request):
    # print("coming!!!!!")
    if request.content_type == "application/json":
        message = await request.json()  # 提取消息内容
        #print(message)
        try:
            if (
                "header" in message
                and message["header"].get("event_type", None) == "im.message.receive_v1"
            ):
                # print("asking")
                open_id = message["event"]["sender"]["sender_id"]["open_id"]
                content = json.loads(message["event"]["message"]["content"])["text"]                                   
                for seat in seats:
                    if seat.user == open_id:#此用户有先前遗留的对话
                        Thread(target=handle_request, args=(seat, content)).start()
                        return web.Response()

                #新用户
                seats[Seat.numOfSeat-1].user = open_id
                Thread(target=handle_request, args=(seats[Seat.numOfSeat-1], content)).start()
                return web.Response(status=200)
                
            else:
                type = message["type"]  # 确定消息类型
                if type == "url_verification":
                    # print("verification!!!!")
                    token = message["token"]
                    if token == LARK_API_TOKEN:
                        challenge = {
                            "challenge": message["challenge"]}  # 提取消息内容
                        res = json.dumps(challenge)
                        return web.Response(text=res, content_type="application/json")
        except Exception as e:
            return web.Response(status=200)




def get_tenant(data):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url=url, data=json.dumps(data))
    tenant = json.loads(res.content.decode())
    return tenant["tenant_access_token"]


def send(open_id, msg):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    msgContent = {
        "text": msg.lstrip(),
    }
    req = {
        "receive_id": open_id,  # chat id
        "msg_type": "text",
        "content": json.dumps(msgContent),
    }
    payload = json.dumps(req)
    headers = {
        "Authorization": "Bearer " + get_tenant(AppProfile),  # your access token
        "Content-Type": "application/json",
    }
    response = requests.request(
        "POST", url, params=params, headers=headers, data=payload
    )


if __name__ == "__main__":

    #读取配置文件
    configPath = "./api_config.json"
    try:
        with open(configPath) as jsonFile:
            config = json.load(jsonFile)
        port = config["WebHook"]["port"]
        route = config["WebHook"]["route"]

        LARK_API_TOKEN = config["Bot"]["bot_api_token"]
        AppProfile = config["Bot"]["profile"]
        openaiKeyList=[]
        for apiDict in config["Api"]:
            if apiDict["api_token"] is not None and len(apiDict["api_token"]) > 10 and apiDict["available"] == True:
                openaiKeyList.append(apiDict["api_token"])

    except:
        port = 6666
        route = "/"
        LARK_API_TOKEN = ""
        openaiKeyList = []
        AppProfile = {
            "app_id": "",
            "app_secret": "",
        }  # 变更机器人时更改

    seats = []
    for key in openaiKeyList:
        seats.append(Seat(key))

    app = web.Application()
    app.add_routes([web.post(route, listen_for_webhook)])

    web.run_app(app, port=port)



