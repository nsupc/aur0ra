import requests

from string import Template
from typing import List

from .utils import format_pings


def login(url: str, username: str, password: str) -> str:
    url = f"{url}/login"

    data = {"username": username, "password": password}

    resp = requests.post(url=url, json=data)

    resp.raise_for_status()

    return resp.json()["token"]


def post(
    url: str,
    token: str,
    template: Template,
    author: str,
    region: str,
    nations: List[str],
) -> int:
    url = f"{url}/rmbposts"

    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "nation": author,
        "region": region,
        "text": template.substitute(nations=format_pings(nations)),
    }

    resp = requests.post(url=url, headers=headers, json=data)
    resp.raise_for_status()

    return resp.status_code
