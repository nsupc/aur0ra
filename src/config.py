import logging
import sys
import yaml

from logtail import LogtailHandler
from os.path import abspath, dirname, join
from string import Template
from typing import Literal, Optional

logger = logging.getLogger("main")


class LogConfig:
    token: Optional[str]
    host: Optional[str]
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    def __init__(
        self,
        token: str | None = None,
        host: str | None = None,
        level: str = "INFO",
    ):
        self.token = token
        self.host = host

        level = level.upper()

        if level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            self.level = level  # type: ignore
        else:
            self.level = "INFO"

        if self.host and self.token:
            handler = LogtailHandler(
                source_token=self.token,
                host=self.host,
            )
        else:
            handler = logging.StreamHandler()

        logger.setLevel(self.level)
        logger.addHandler(handler)


class Eurocore:
    url: str
    user: str
    password: str

    def __init__(self, url: str, user: str, password: str) -> None:
        self.url = url
        self.user = user
        self.password = password

        self.url = self.url.strip("/")


class Rmbpost:
    author: str
    template: Template

    def __init__(self, author: str, template: Template):
        self.author = author
        self.template = template

    @classmethod
    def from_file(cls, author: str, path: str):
        with open(path, "r") as in_file:
            return cls(author, Template(in_file.read()))


class Config:
    user: str
    region: str
    population_cache: str
    eurocore: Eurocore
    rmbpost: Rmbpost
    log_config: LogConfig

    def __init__(
        self,
        user: str,
        region: str,
        population_cache: str,
        eurocore_url: str,
        eurocore_user: str,
        eurocore_password: str,
        rmbpost_author: str,
        rmbpost_template_path: str,
        log_token: Optional[str] = None,
        log_endpoint: Optional[str] = None,
        log_level: str = "INFO",
    ):
        self.user = user
        self.region = region
        self.population_cache = population_cache
        self.eurocore = Eurocore(eurocore_url, eurocore_user, eurocore_password)
        self.rmbpost = Rmbpost.from_file(rmbpost_author, rmbpost_template_path)
        self.log_config = LogConfig(log_token, log_endpoint, log_level)

    @classmethod
    def from_yml(cls, path: str = join(dirname(abspath(__file__)), "config.yml")):
        with open(path, "r") as in_file:
            data = yaml.safe_load(in_file)

        if not data:
            logger.fatal("no data found in file: %s", path)
            sys.exit(1)

        eurocore = data["eurocore"]
        rmbpost = data["rmbpost"]
        log = data["log"]

        return cls(
            data["user"],
            data["region"],
            data["population_cache_path"],
            eurocore["url"],
            eurocore["user"],
            eurocore["password"],
            rmbpost["author"],
            rmbpost["template_path"],
            log.get("token"),
            log.get("host"),
            log["level"],
        )
