import asyncio
import json
from time import time_ns

import aioredis
import trio
import trio_asyncio
from hypercorn.config import Config as HyperConfig
from hypercorn.trio import serve
from quart import Response, render_template, request, websocket
from quart_trio import QuartTrio

from db import Database
from utils import State, create_argparser, mail_conversion

parser = create_argparser()
args = parser.parse_args()
app = QuartTrio(__name__)
state = State
phones = ["123", "234", "345"]


@app.before_serving
async def init():
    state.redis = await trio_asyncio.run_aio_coroutine(
        aioredis.create_redis_pool(
            address=args.redis_uri,
            password=args.redis_password,
            encoding="utf-8",
        )
    )
    state.db = Database(state.redis)


@app.after_serving
async def close():
    if state.redis is not None:
        state.redis.close()
        await trio_asyncio.run_aio_coroutine(state.redis.wait_closed())


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route(
    "/send/",
    methods=[
        "POST",
    ],
)
async def create_sms_mailing():
    try:
        form = await request.form
        text = form.get("text", None)
        if text is None:
            raise ValueError("Empty sms text")

        await trio_asyncio.run_aio_coroutine(
            state.db.add_sms_mailing(time_ns(), phones, text)
        )
        return Response(json.dumps({"status": "ok"}), status=201)
    except Exception as e:
        print(e)
        return Response(json.dumps({"errorMessage": e}), status=500)


@app.websocket("/ws")
async def ws():
    while True:
        try:
            ids = await trio_asyncio.aio_as_trio(state.db.list_sms_mailings)()

            mailings = [
                await trio_asyncio.run_aio_coroutine(
                    state.db.get_sms_mailings(x)
                )
                for x in ids
            ]
            transformed_mailings = [mail_conversion(x[0]) for x in mailings]

            await websocket.send(
                json.dumps(
                    {
                        "msgType": "SMSMailingStatus",
                        "SMSMailings": transformed_mailings,
                    }
                )
            )
            await trio.sleep(2)
        except Exception as e:
            print(e)


async def run_server():

    async with trio_asyncio.open_loop():
        asyncio._set_running_loop(asyncio.get_event_loop())
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True

        await serve(app, config)


if __name__ == "__main__":
    trio.run(run_server)