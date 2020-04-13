import requests
from logger import log
from config import config


def request(url: str = "", param={}, headers={}, method='get',json={}) -> dict:
    try:
        if method == 'post':
            if json:
                r = requests.post(url, json=json, headers=headers)
            else:
                r = requests.post(url, data=param, headers=headers)
        if method == 'get':
            r = requests.get(url, data=param, headers=headers)
        if method == 'delete':
            r = requests.delete(url, data=param, headers=headers)
        return r.json()
    except Exception as e:
        log(e)
        raise Exception(e,r)


