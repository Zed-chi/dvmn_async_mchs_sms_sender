from environs import Env
import json
import trio
import httpx
import aiofiles


API_URL = "https://smsc.ru/sys/send.php"
STATUS_URL = "https://smsc.ru/sys/status.php"
env = Env()
env.read_env()
login = env.str("LOGIN")
password = env.str("PASSWORD")
message = "Hello"
test_phone = env.str("TESTPHONE")
phones = [test_phone,]
test_id = 123


async def send_sms_async():
    params = {
        "login":login,
        "psw":password,
        "phones":",".join(phones),
        "mes":message,
        "fmt":3,
        "id":test_id,
        "op":1,
        "all":1,
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(API_URL, params=params)
        res.raise_for_status()
        print(res.status_code)
        print(res.json())
        with open("out.txt", "a", encoding="utf-8") as file:
            file.write(json.dumps(res.json()))
            file.write("\n")


async def check_sms_status(phone, sms_id):
    params = {
        "login":login,
        "psw":password,
        "phone":phone,
        "id":sms_id,
        "fmt":3,
        "all":0,
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(STATUS_URL, params=params)
        res.raise_for_status()
        print(res.status_code)
        print(res.json())

    async with await trio.open_file("out.txt", "a", encoding="utf-8") as file:
            await file.write(json.dumps(res.json()))
            await file.write("\n")

#trio.run(send_sms_async)
trio.run(check_sms_status, test_phone, test_id)
