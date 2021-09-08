import asyncio
from environs import Env
#from api import request_smsc
from quart import render_template, websocket, request, Quart
from unittest.mock import MagicMock
import json


mock = MagicMock()


env = Env()
env.read_env()


login = env.str("LOGIN")
password = env.str("PASSWORD")
message = "Внимание, вечером будет шторм!"
test_phone = env.str("TESTPHONE")
phones = [test_phone,]
test_id = 123

status_params = {
    "login":login,
    "psw":password,
    "phone":test_phone,
    "id":test_id,
    "fmt":3,
    "all":0,
    "charset":"utf-8",
}

send_params = {    
    #"phones":",".join(phones),
    "mes":message,
    "fmt":3,
    "id":test_id,
    "op":1,
    "all":1,
    "charset":"utf-8",
}

def request_smsc(*args):       
    return mock(return_value={'id': 123, 'cnt': 1})



#app = QuartTrio(__name__)
app = Quart(__name__)


@app.route("/")
async def index():
    return await render_template("index.html")

@app.route("/send/", methods=["POST"])
async def send_sms():
    form = await request.form
    message = form["text"]
    if message:
        send_params = {    
            "phones":",".join(phones),
            "mes":message,
            "fmt":3,
            "id":test_id,
            "op":1,
            "all":1,
            "charset":"utf-8",
        }
        response = request_smsc("send", login , password, send_params)
        print(response)

    return {
    "errorMessage": "Потеряно соединение с SMSC.ru"
    }

@app.websocket("/ws")
async def ws():
    for i in range (100):
        result = {
            "msgType": "SMSMailingStatus",
            "SMSMailings": [
                {
                "timestamp": 1123131392.734,
                "SMSText": "Сегодня гроза! Будьте осторожны!",
                "mailingId": "1",
                "totalSMSAmount": 100,
                "deliveredSMSAmount": i,
                "failedSMSAmount": 0,
                },
            ]
        }
        await websocket.send(json.dumps(result))
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.run()    
