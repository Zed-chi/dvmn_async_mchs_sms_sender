from enum import Enum
from typing import Dict, List
from unittest.mock import MagicMock
from xmlrpc.client import Boolean

import httpx


class SmscApiError(Exception):
    pass


class API_methods(Enum):
    send_message = "send"
    check_status = "status"


class Smsc_manager:
    """Менеджер сервиса SMSC
    Аргументы:
        login (str): Логин SMSC.
        password (str): Пароль SMSC.
    """

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.SEND_URL = "https://smsc.ru/sys/send.php"
        self.STAT_URL = "https://smsc.ru/sys/status.php"

    def check_params(self, method: str, params_to_check: Dict):
        """Валидация параметров"""
        send_params = ["phones", "mes"]
        stat_params = ["phone", "id"]
        params = (
            send_params if method == API_methods.send_message else stat_params
        )
        for i in params:
            if i not in params_to_check or not params_to_check[i]:
                raise SmscApiError("Params Error")

    async def request_smsc(self, method:API_methods, request_params:Dict, mock:Boolean=False)->Dict:
        """Шлет запросы на SMSC.ru сервис.

        Аргументы:
            method (str): Методы описанные в API_methods - рассылка или статус.
            request_params (dict): Параметры требуемые для запроса.
            mock(Bool): Имитация запроса
        Returns:
            dict: Response from SMSC API.
        Raises:
            SmscApiError: If SMSC API response status is not 200.

        Examples:
            >>> request_smsc("send", "my_login", "my_password", {"phones": "+79123456789"})
            {"cnt": 1, "id": 24}
            >>> request_smsc("status", "my_login", "my_password", {"phone": "+79123456789", "id": "24"})
            {'status': 1, 'last_date': '28.12.2019 19:20:22', 'last_timestamp': 1577550022}
        """

        params = {
            "login": self.login,
            "psw": self.password,
            "fmt": 3,
            "all": 0,
        }

        if method not in [API_methods.send_message, API_methods.check_status]:
            raise SmscApiError("Wrong Method")

        if method == API_methods.send_message:
            if mock:
                return {"id": 256, "cnt": 1}
            api_url = self.SEND_URL
            self.check_params(method, request_params)
        else:
            if mock:
                return {
                    "status": -1,
                    "last_date": "20.01.2022 20:18:32",
                    "last_timestamp": 1642699112,
                }
            api_url = self.STAT_URL
            self.check_params(method, request_params)

        params.update(request_params)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(api_url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise SmscApiError(e)
