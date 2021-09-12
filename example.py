import argparse
import asyncio

import aioredis
import trio
import trio_asyncio

from db import Database


def create_argparser():
    parser = argparse.ArgumentParser(
        description="Redis database usage example"
    )
    parser.add_argument(
        "--address",
        default="redis://localhost:6379",
        action="store",
        dest="redis_uri",
        help="Redis URI",
    )
    parser.add_argument(
        "--password",
        action="store",
        dest="redis_password",
        help="Redis db password",
    )
    return parser


async def main():
    parser = create_argparser()
    args = parser.parse_args()

    asyncio._set_running_loop(asyncio.get_event_loop())

    redis = await trio_asyncio.run_aio_coroutine(
        aioredis.create_redis_pool(
            address="redis://localhost:6379", encoding="utf-8"
        )
    )

    try:

        db = Database(redis)

        sms_id = "2"

        phones = [
            "+7 999 519 05 57",
            "911",
            "112",
        ]
        text = "Вечером будет шторм!"

        await trio_asyncio.run_aio_coroutine(
            db.add_sms_mailing(sms_id, phones, text)
        )

        sms_ids = await trio_asyncio.run_aio_coroutine(db.list_sms_mailings())
        print("Registered mailings ids", sms_ids)

        pending_sms_list = await trio_asyncio.run_aio_coroutine(
            db.get_pending_sms_list()
        )
        print("pending:")
        print(pending_sms_list)

        await trio_asyncio.run_aio_coroutine(
            db.update_sms_status_in_bulk(
                [
                    # [sms_id, phone_number, status]
                    [sms_id, "112", "failed"],
                    [sms_id, "911", "pending"],
                    [sms_id, "+7 999 519 05 57", "delivered"],
                    # following statuses are available: failed, pending, delivered
                ]
            )
        )

        pending_sms_list = await trio_asyncio.run_aio_coroutine(
            db.get_pending_sms_list()
        )
        print("pending:")
        print(pending_sms_list)

        sms_mailings = await trio_asyncio.run_aio_coroutine(
            db.get_sms_mailings("2")
        )
        print("sms_mailings")
        print(sms_mailings)

        async def send():
            while True:
                await trio.sleep(1)
                await trio_asyncio.run_aio_coroutine(
                    redis.publish("updates", sms_id)
                )

        async def listen():
            *_, channel = await trio_asyncio.run_aio_coroutine(
                redis.subscribe("updates")
            )

            while True:
                raw_message = await channel.get()

                if not raw_message:
                    raise ConnectionError("Connection was lost")

                message = raw_message.decode("utf-8")
                print("Got message:", message)

        async with trio.open_nursery() as n:
            n.start_soon(send)
            n.start_soon(listen)

    finally:
        redis.close()
        await trio_asyncio.run_aio_coroutine(redis.wait_closed())


async def run_server():
    async with trio_asyncio.open_loop():
        await main()


if __name__ == "__main__":
    trio_asyncio.run(run_server)
