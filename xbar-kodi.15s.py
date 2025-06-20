#!/usr/bin/env python3

#  <xbar.title>Kodi</xbar.title>
#  <xbar.version>v0.1</xbar.version>
#  <xbar.author>Nathan Reynolds</xbar.author>
#  <xbar.author.github>nathforge</xbar.author.github>
#  <xbar.dependencies>python</xbar.dependencies>
#  <xbar.var>string(VAR_URL="http://localhost:8080/"): Kodi remote control HTTP URL</xbar.var>
#  <xbar.var>string(VAR_USERNAME=""): Remote control username</xbar.var>
#  <xbar.var>string(VAR_PASSWORD=""): Remote control password</xbar.var>
#  <xbar.var>string(VAR_LOG_FILENAME=""): Log location (optional, used for developers)</xbar.var>

import base64
import dataclasses
import json
import logging
import logging.config
import os
import sys
import urllib.request

# Icon from https://www.streamlinehq.com/icons/download/kodi--31088
ICON = "PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBpZD0iS29kaS0tU3RyZWFtbGluZS1TaW1wbGUtSWNvbnMiIGhlaWdodD0iMjQiIHdpZHRoPSIyNCI+CiAgPGRlc2M+CiAgICBLb2RpIFN0cmVhbWxpbmUgSWNvbjogaHR0cHM6Ly9zdHJlYW1saW5laHEuY29tCiAgPC9kZXNjPgogIDx0aXRsZT5Lb2RpPC90aXRsZT4KICA8cGF0aCBkPSJNMTIuMDMgMC4wNDdjLTAuMjI2IDAgLTAuNDUyIDAuMTA3IC0wLjY2OSAwLjMyNCAtMC45MjIgMC45MjIgLTEuODQyIDEuODQ1IC0yLjc2MyAyLjc2OCAtMC4yMzMgMC4yMzMgLTAuNDU1IDAuNDggLTAuNzAzIDAuNjk1IC0wLjMxIDAuMjY3IC0wLjQwNSAwLjU4MyAtMC4zOTkgMC45ODggMC4wMiAxLjM5OSAwLjAwOCAyLjc5OSAwLjAwOCA0LjE5OCAwIDEuNDUzIC0wLjAwMiAyLjkwNyAwIDQuMzYgMCAwLjExIDAuMDAyIDAuMjIzIDAuMDMgMC4zMjcgMC4wODcgMC4zMzcgMC4zMDMgMC4zOTMgMC41NDYgMC4xNSAxLjMxIC0xLjMxIDIuNjE4IC0yLjYyMiAzLjkyOCAtMy45MzNsNC40NDkgLTQuNDUzYzAuNDMgLTAuNDMxIDAuNDMgLTAuOTA1IDAgLTEuMzM2TDEyLjY5NyAwLjM3Yy0wLjIxNiAtMC4yMTcgLTAuNDQyIC0wLjMyNCAtMC42NjggLTAuMzI0em03LjIyNCA3LjIzYy0wLjIyMyAwIC0wLjQ0NSAwLjEwNCAtMC42NSAwLjMwOUwxNC44MiAxMS4zN2MtMC40MjggMC40MjkgLTAuNDI3IDAuODk1IDAgMS4zMjJsMy43NiAzLjc2NmMwLjQ0IDAuNDQgMC45MDggMC40NCAxLjM0NiAwLjAwMiAxLjIxNSAtMS4yMTYgMi40MjcgLTIuNDMzIDMuNjQ0IC0zLjY0NyAwLjE4MiAtMC4xOCAwLjM1MyAtMC4zNjQgMC40MyAtMC42MTV2LTAuMzNjLTAuMDc3IC0wLjI1MSAtMC4yNDYgLTAuNDM2IC0wLjQyOCAtMC42MTcgLTEuMjI0IC0xLjIyIC0yLjQ0MyAtMi40NDUgLTMuNjY2IC0zLjY2OCAtMC4yMDUgLTAuMjA1IC0wLjQyOSAtMC4zMDcgLTAuNjUyIC0wLjMwN3pNNC4xOCA3LjYxMWMtMC4wODYgMC4wMTQgLTAuMTQ1IDAuMDk0IC0wLjIwNyAwLjE1N0wwLjIwOSAxMS41NzJjLTAuMjggMC4yODQgLTAuMjc4IDAuNjc3IDAuMDA0IDAuOTZsMi4wNDMgMi4wNDZjMC41OSAwLjU5IDEuMTc3IDEuMTgyIDEuNzY3IDEuNzcyIDAuMTY5IDAuMTY4IDAuMzMgMC4xMzkgMC40MTYgLTAuMDg0IDAuMDQ0IC0wLjExNCAwLjA2MiAtMC4yNDIgMC4wNjMgLTAuMzY0IDAuMDA0IC0xLjI4MyAwLjAwNCAtMi41NjcgMC4wMDQgLTMuODUxaC0wLjAwMlY4LjE4NGMwIC0wLjA4NSAtMC4wMSAtMC4xNjkgLTAuMDIyIC0wLjI1MiAtMC4wMTkgLTAuMTM1IC0wLjA3MiAtMC4yNTggLTAuMjA3IC0wLjMwOWEwLjE4NiAwLjE4NiAwIDAgMCAtMC4wOTUgLTAuMDEyem03LjkwOCA2LjgzOGMtMC4yMjQgMCAtMC40NDcgMC4xMDYgLTAuNjU2IDAuMzE1TDcuNjYgMTguNTM3Yy0wLjQzMyAwLjQzNCAtMC40MzMgMC44OTkgMC4wMDIgMS4zMzQgMS4yMTUgMS4yMTYgMi40MyAyLjQzIDMuNjQzIDMuNjQ5IDAuMTggMC4xOCAwLjM2MSAwLjM1NCAwLjYxMSAwLjQzM2gwLjMzYzAuMjQ0IC0wLjA2OSAwLjQyMyAtMC4yMjYgMC41OTggLTAuNDAyIDEuMjIyIC0xLjIzIDIuNDUgLTIuNDUzIDMuNjc2IC0zLjY4IDAuNDMgLTAuNDMgMC40MjcgLTAuOTA1IC0wLjAwNCAtMS4zMzhsLTMuNzcyIC0zLjc3M2MtMC4yMDggLTAuMjA4IC0wLjQzMiAtMC4zMTEgLTAuNjU2IC0wLjMxeiIgZmlsbD0iIzAwMDAwMCIgc3Ryb2tlLXdpZHRoPSIxIj48L3BhdGg+Cjwvc3ZnPg=="


def main():
    try:
        config = Config.from_env()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        exit(1)

    setup_logging(config)
    logger = logging.getLogger(f"{__name__}.main")

    logger.debug(f"config={dataclasses.replace(config, password='<REDACTED>')}")

    kodi_rpc = KodiRpc(
        config.url.rstrip("/") + "/jsonrpc", config.username, config.password
    )

    active_players = kodi_rpc.call("Player.GetActivePlayers")
    logger.debug(f"active_players={active_players}")

    playing_title = None
    if active_players:
        first_active_player_id = active_players[0]["playerid"]
        logger.debug(f"first_active_player_id={first_active_player_id}")

        item = kodi_rpc.call(
            "Player.GetItem",
            playerid=first_active_player_id,
            properties=[
                "episode",
                "season",
                "showtitle",
                "title",
                "year",
            ],
        )["item"]
        logger.debug(f"item={item}")

        if item["type"] == "episode":
            playing_title = f"{item['showtitle']} S{item['season']:02d}E{item['episode']:02d}: {item['title']}"
        elif item["type"] == "movie":
            playing_title = f"{item['title']} ({item['year']})"
        else:
            playing_title = item["title"]

    print(f"| templateImage={ICON}")
    print("---")
    if playing_title:
        print(f"{playing_title.replace('|', '')} | href={config.url}")
    else:
        print(f"Inactive | href={config.url}")


@dataclasses.dataclass
class Config:
    url: str
    username: str
    password: str
    log_filename: str

    @classmethod
    def from_env(cls):
        url = os.getenv("VAR_URL")
        username = os.getenv("VAR_USERNAME") or ""
        password = os.getenv("VAR_PASSWORD") or ""
        log_filename = os.getenv("VAR_LOG_FILENAME") or ""

        if not url:
            raise ValueError("URL must be set")

        return cls(url, username, password, log_filename)


def setup_logging(config: Config):
    log_config = {
        "version": 1,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "DEBUG",
            },
        },
    }

    if config.log_filename:
        log_config["handlers"]["file"] = {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": config.log_filename,
        }
        log_config["loggers"][""]["handlers"].append("file")

    logging.config.dictConfig(log_config)


class KodiRpc:
    _url: str
    _username: str
    _password: str

    def __init__(self, url: str, username: str, password: str):
        self._url = url
        self._username = username
        self._password = password

    def call(self, method, *args, **kwargs):
        if args and kwargs:
            raise ValueError(
                "*args or **kwargs can be passed to Kodi RPC, but not both"
            )

        req_headers = {"Content-Type": "application/json"}

        if self._username or self._password:
            username_password = f"{self._username}:{self._password}"
            req_headers["Authorization"] = (
                f"Basic {base64.b64encode(username_password.encode())}"
            )

        req_payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 1,
            "params": args or kwargs,
        }

        req = urllib.request.Request(
            self._url,
            json.dumps(req_payload).encode("ascii"),
            req_headers,
        )

        with urllib.request.urlopen(req) as res:
            res_content_type = res.headers.get("Content-Type")
            res_body = res.read()

            if not 200 <= res.status <= 299:
                raise Exception(f"Unexpected HTTP {res.status} with body {res_body!r}")

            if res_content_type != "application/json":
                raise Exception(f"Unexpected content-type {res_content_type!r}")

            res_payload = json.loads(res_body)

            res_error = res_payload.get("error")
            if res_error:
                res_error_code = res_error.get("code")
                res_error_message = res_error.get("message")
                raise Exception(
                    f"{res_error_code}: {res_error_message}",
                    res_error_code,
                    res_error_message,
                )

            return res_payload["result"]


if __name__ == "__main__":
    main()
