import logging
import os
import requests
import yaml

from bs4 import BeautifulSoup as bs
from logtail import LogtailHandler
from string import Template
from typing import List


class LogConfig:
    token: str
    host: str
    level: str

    def __init__(self, token: str, host: str, level: str = "INFO"):
        self.tokne = token
        self.host = host
        if level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            self.level = level.upper()
        else:
            self.level = "INFO"

        handler = LogtailHandler(
            source_token="CzM5AQAyH8RmQUVqEficnDfm",
            host="https://s1257851.eu-nbg-2.betterstackdata.com",
        )

        logger = logging.getLogger()
        logger.setLevel(self.level)
        logger.addHandler(handler)


class Config:
    user: str
    region: str
    eurocore_url: str
    eurocore_user: str
    eurocore_password: str
    rmbpost_author: str
    rmbpost_template: str
    population_cache: str
    log_config: LogConfig

    def __init__(self, path: str):
        with open("./config.yml", "r") as in_file:
            data = yaml.safe_load(in_file)

        self.user = data["user"]
        self.region = data["region"]
        self.eurocore_url = data["eurocore_url"]
        self.eurocore_user = data["eurocore_user"]
        self.eurocore_password = data["eurocore_password"]
        self.rmbpost_author = data["rmbpost_author"]
        self.rmbpost_template = data["rmbpost_template"]
        self.population_cache = data["population_cache"]

        self.eurocore_url = self.eurocore_url.strip("/")

        self.log_config = LogConfig(
            data["log_config"]["token"],
            data["log_config"]["host"],
            data["log_config"]["level"],
        )


def get_old_pop(path: str) -> List[str] | None:
    if os.path.exists(path):
        with open(path, "r") as in_file:
            return in_file.read().splitlines()
    else:
        return None


def write_old_pop(path: str, pop: List[str]):
    with open(path, "w") as out_file:
        out_file.write("\n".join(pop))


def format_pings(nations: str) -> str:
    nations = [f"[nation]{nation}[/nation]" for nation in nations]

    if len(nations) == 1:
        return nations[0]
    elif len(nations) == 2:
        return " and ".join(nations)
    else:
        return ", ".join(nations[:-1]) + ", and " + nations[-1]


def login(url: str, username: str, password: str) -> str:
    url = f"{url}/login"

    data = {"username": username, "password": password}

    resp = requests.post(url=url, json=data)

    resp.raise_for_status()

    return resp.json()["token"]


def post(
    url: str,
    token: str,
    template_path: str,
    author: str,
    region: str,
    nations: List[str],
) -> int:
    url = f"{url}/rmbposts"

    headers = {"Authorization": f"Bearer {token}"}

    with open(template_path, "r") as in_file:
        text = Template(in_file.read())

    data = {
        "nation": author,
        "region": region,
        "text": text.substitute(nations=format_pings(nations)),
    }

    resp = requests.post(url=url, headers=headers, json=data)
    resp.raise_for_status()

    return resp.status_code


def main():
    config = Config("./config.yml")
    logging.info("running")

    pop = (
        bs(
            requests.get(
                f"https://www.nationstates.net/cgi-bin/api.cgi?region={config.region}&q=nations",
                headers={"User-Agent": config.user},
            ).text,
            "xml",
        )
        .find("NATIONS")
        .text.split(":")
    )

    old_pop = get_old_pop(config.population_cache)
    if not old_pop:
        logging.info(
            "file: %s does not exist, assuming first time run", config.population_cache
        )

        write_old_pop(config.population_cache, pop)
        return

    new_pop = [nation for nation in pop if nation not in old_pop]

    logging.info("new nations: %d", len(new_pop))
    if len(new_pop) == 0:
        return

    try:
        token = login(
            config.eurocore_url, config.eurocore_user, config.eurocore_password
        )
    except requests.HTTPError:
        logging.exception("unable to log in")

    try:
        post(
            config.eurocore_url,
            token,
            config.rmbpost_template,
            config.rmbpost_author,
            config.region,
            pop,
        )
    except requests.HTTPError:
        logging.exception("unable to post rmbpost")

    write_old_pop(config.population_cache, pop)


if __name__ == "__main__":
    main()
