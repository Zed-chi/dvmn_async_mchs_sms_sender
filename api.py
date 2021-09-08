import httpx


class SmscApiError(Exception):
    pass


async def request_smsc(method, login, password, payload):
    """Send request to SMSC.ru service.
    
    Args:
        method (str): API method. E.g. 'send' or 'status'.
        login (str): Login for account on SMSC.
        password (str): Password for account on SMSC.
        payload (dict): Additional request params, override default ones.
    Returns:
        dict: Response from SMSC API.
    Raises:
        SmscApiError: If SMSC API response status is not 200 or it has `"ERROR" in response.
        
    Examples:
        >>> request_smsc("send", "my_login", "my_password", {"phones": "+79123456789"})
        {"cnt": 1, "id": 24}
        >>> request_smsc("status", "my_login", "my_password", {"phone": "+79123456789", "id": "24"})
        {'status': 1, 'last_date': '28.12.2019 19:20:22', 'last_timestamp': 1577550022}
    """    
    payload["login"] = login
    payload["psw"] = password

    if method not in ["send", "status"]:
        raise SmscApiError("Wrong Method")

    if method == "send":
        api_url = "https://smsc.ru/sys/send.php"
    else:
        api_url = "https://smsc.ru/sys/status.php"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, params=payload)
        response.raise_for_status()

        if response.status_code != 200:
            raise SmscApiError(f"Status code is {response.status_code}")
        
        response_dict = response.json()
        
        if "error" in response_dict:
            raise SmscApiError(f"Error: {response_dict['error']}")
    
        return response_dict
