from environs import Env
import requests
import trio
import httpx


API_URL = "https://smsc.ru/sys/send.php"
env = Env()
env.read_env()
login = env.str("LOGIN")
password = env.str("PASSWORD")
message = "Hello"
test_phone = env.str("TESTPHONE")
phones = [test_phone,]
params = {
    "login":login,
    "psw":password,
    "phones":",".join(phones),
    "mes":message,
}

def send_sms():
    requests.post(API_URL, params=params)

async def send_sms_async():
    async with httpx.AsyncClient() as client:
        res = await client.get("http://ya.ru")
        res.raise_for_status()
        print(res.status_code)
        print(res.text)


trio.run(send_sms_async)