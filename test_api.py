from environs import Env
from api import request_smsc
import trio
from unittest.mock import MagicMock
import asyncio



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


request_smsc("send", login, password, send_params)
