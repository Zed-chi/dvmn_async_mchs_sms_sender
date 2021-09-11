import aioredis
import argparse

from db import Database
import trio_asyncio
import trio


def create_argparser():
    parser = argparse.ArgumentParser(description='Redis database usage example')
    parser.add_argument('--address',default="redis://localhost:6379", action='store', dest='redis_uri', help='Redis URI')
    parser.add_argument('--password',action='store', dest='redis_password', help='Redis db password')

    return parser


async def main():
    parser = create_argparser()
    args = parser.parse_args()

    async with trio_asyncio.open_loop():
        redis = await trio_asyncio.run_aio_coroutine(
                aioredis.create_redis_pool(
                args.redis_uri,
                password=args.redis_password,
                encoding='utf-8',
            )
        )
        try:
            db = Database(redis)
            sms_id = '1'
            phones = [
                '+7 999 519 05 57',
                '911',
                '112',
            ]
            text = 'Вечером будет шторм!'
            await trio_asyncio.aio_as_trio(db.add_sms_mailing)(
                sms_id, phones, text
            )
            

            sms_ids = await trio_asyncio.aio_as_trio(
                db.list_sms_mailings
            )()
            print('Registered mailings ids', sms_ids)

            pending_sms_list = await trio_asyncio.aio_as_trio(
                db.get_pending_sms_list
            )()        
            print('pending:')
            print(pending_sms_list)

            await trio_asyncio.aio_as_trio(
                db.update_sms_status_in_bulk
            )([
                # [sms_id, phone_number, status]
                [sms_id, '112', 'failed'],
                [sms_id, '911', 'pending'],
                [sms_id, '+7 999 519 05 57', 'delivered'],
                # following statuses are available: failed, pending, delivered
                ])
            

            pending_sms_list = await trio_asyncio.aio_as_trio(
                db.get_pending_sms_list
            )()
            
            print('pending:')
            print(pending_sms_list)

            sms_mailings = await trio_asyncio.aio_as_trio(
                db.get_sms_mailings
            )('1')
            
            print('sms_mailings')
            print(sms_mailings)

            async def send():
                while True:                
                    await trio.sleep(1)                
                    await trio_asyncio.aio_as_trio(
                        redis.publish
                    )('updates', sms_id)

            async def listen():
                *_, channel = await trio_asyncio.run_aio_coroutine(
                    redis.subscribe('updates')
                )

                while True:
                    raw_message = await trio_asyncio.run_aio_coroutine(
                        channel.get()
                    )                    

                    if not raw_message:
                        raise ConnectionError('Connection was lost')

                    message = raw_message.decode('utf-8')
                    print('Got message:', message)

            async with trio.open_nursery() as nursery:
                nursery.start_soon(send)
                nursery.start_soon(listen)

        finally:
            redis.close()        
            
            await trio_asyncio.aio_as_trio(
                redis.wait_closed
            )()
        


async def async_main_wrapper(*args):    
    async with trio_asyncio.open_loop() as loop:        
        await trio_asyncio.aio_as_trio(main)


if __name__ == '__main__':
    trio.run(main)
