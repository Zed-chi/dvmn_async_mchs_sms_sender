import asyncio

import trio
from environs import Env
from hypercorn.config import Config as HyperConfig
from hypercorn.trio import serve
from pydantic.error_wrappers import ValidationError
from quart import jsonify, render_template, request, websocket
from quart_trio import QuartTrio
from redis import asyncio as aioredis
from trio_asyncio import aio_as_trio, open_loop

from db import Database
from smsc_api import API_methods, Smsc_manager
from utils import Mailing, State, create_argparser, transform_mailing


env = Env()
env.read_env()


parser = create_argparser()
args = parser.parse_args()
state = State
phones = [
    "+7 999 519 05 57",
    "911",
    "112",
]
app = QuartTrio(__name__)


@app.before_serving
async def init():
    state.redis = await aio_as_trio(aioredis.from_url)(
        args.redis_uri, decode_responses=True
    )
    state.db = Database(state.redis)
    state.smsc = Smsc_manager(env.str("login"), env.str("password"))


@app.after_serving
async def close():
    await aio_as_trio(state.redis.close)()


@app.route("/")
async def index():
    return await render_template("./index.html")


@app.websocket("/ws")
async def ws():
    while True:
        sms_ids = await aio_as_trio(state.db.list_sms_mailings)()
        sms_mailings = await aio_as_trio(state.db.get_sms_mailings)(*sms_ids)
        transformed_mailings = [transform_mailing(x) for x in sms_mailings]

        message = {
            "msgType": "SMSMailingStatus",
            "SMSMailings": transformed_mailings,
        }
        await websocket.send_json(message)
        await trio.sleep(1)


@app.route("/send/", methods=["POST"])
async def create():
    try:
        form = await request.form
        mailing = Mailing(message=form["text"])
        smsc_response = await state.smsc.request_smsc(
            API_methods.send_message,
            {"mes": mailing.message, "phones": phones},
            mock=True,
        )
        await aio_as_trio(state.db.add_sms_mailing)(
            smsc_response["id"], phones, form["text"]
        )

        if "errorMessage" in smsc_response:
            return jsonify({"errorMessage": smsc_response["errorMessage"]})
        return jsonify(smsc_response)
    except ValidationError:
        return jsonify({"errorMessage": "Empty text"})


async def async_main():
    async with open_loop():
        asyncio._set_running_loop(asyncio.get_event_loop())
        config = HyperConfig()
        config.bind = ["127.0.0.1:5000"]
        config.use_reloader = True
        await serve(app, config)


if __name__ == "__main__":
    try:
        trio.run(async_main)
    except KeyboardInterrupt:
        print("Aborted, bye!")
