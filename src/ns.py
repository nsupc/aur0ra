import requests

from bs4 import BeautifulSoup as bs
from typing import List


def get_population(user: str, region: str) -> List[str]:
    pop = bs(
        requests.get(
            f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=nations",
            headers={"User-Agent": user},
        ).text,
        "xml",
    ).find("NATIONS")

    if not pop:
        raise ValueError("unable to find `NATIONS` element")

    return pop.text.split(":")
