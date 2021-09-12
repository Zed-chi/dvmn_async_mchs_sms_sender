import asyncio
import json
from time import time_ns

import aioredis
from quart import Quart, Response, render_template, request, websocket

from db import Database

app = Quart(__name__)
server = {"redis": None, "db": None}
phones = ["123", "234", "345"]

loop = asyncio.get_event_loop()

server["redis"] = loop.run_until_complete(
    aioredis.create_redis_pool(
        address="redis://localhost:6379",
        encoding="utf-8",
    )
)


print(server["redis"])
server["db"] = Database(server["redis"])


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/send/", methods=["POST"])
async def create():
    form = await request.form
    text = form["text"]
    await server["db"].add_sms_mailing(
        sms_id=str(time_ns()), phones=phones, text=text
    )

    return json.dumps({"status": "ok"})


@app.websocket("/ws")
async def ws():
    while True:
        ids = await server["db"].list_sms_mailings()
        mails = [qwe(x) for x in ids]
        await websocket.send(
            json.dumps({"msgType": "SMSMailingStatus", "SMSMailings": mails})
        )
        await asyncio.sleep(1)


def qwe(x):
    return {
        "timestamp": 1123131392.734,
        "SMSText": "xxx",
        "mailingId": str(x),
        "totalSMSAmount": 345,
        "deliveredSMSAmount": 47,
        "failedSMSAmount": 5,
    }


if __name__ == "__main__":
    app.run(port=5000, loop=loop)
