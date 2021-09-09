"""
Сценарий тестирования:

    Положить в Redis свой номер телефона
    Вытащить запись по ключу
    Вывести в терминал

"""

import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set('testphone', '123456789')

print(r.get("testphone").decode())
