from environs import Env
import requests


API_URL = "https://smsc.ru/sys/send.php"
env = Env()
env.read_env()
login = env.str("LOGIN")
password = env.str("PASSWORD")
message = "Hello"
test_phone = env.str("TESTPHONE")
phones = [test_phone,]

requests.post(API_URL, params={
    "login":login,
    "psw":password,
    "phones":",".join(phones),
    "mes":message,
})