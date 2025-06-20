#!/usr/bin/python3

#  <xbar.title>Kodi</xbar.title>
#  <xbar.version>v0.1</xbar.version>
#  <xbar.author>Nathan Reynolds</xbar.author>
#  <xbar.author.github>nathforge</xbar.author.github>
#  <xbar.dependencies>python</xbar.dependencies>
#  <xbar.var>string(VAR_URL="http://localhost:8080/"): Kodi remote control HTTP URL</xbar.var>
#  <xbar.var>string(VAR_USERNAME=""): Remote control username</xbar.var>
#  <xbar.var>string(VAR_PASSWORD=""): Remote control password</xbar.var>
#  <xbar.var>string(VAR_LOG_FILENAME=""): Log location (optional, used for developers)</xbar.var>

import argparse
import base64
import dataclasses
import json
import logging
import logging.config
import os
import os.path
import shlex
import sys
import urllib.request
from datetime import timedelta
from typing import TypedDict

# Icon from https://www.streamlinehq.com/icons/download/kodi--31088
ICON = "PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBpZD0iS29kaS0tU3RyZWFtbGluZS1TaW1wbGUtSWNvbnMiIGhlaWdodD0iMjQiIHdpZHRoPSIyNCI+CiAgPGRlc2M+CiAgICBLb2RpIFN0cmVhbWxpbmUgSWNvbjogaHR0cHM6Ly9zdHJlYW1saW5laHEuY29tCiAgPC9kZXNjPgogIDx0aXRsZT5Lb2RpPC90aXRsZT4KICA8cGF0aCBkPSJNMTIuMDMgMC4wNDdjLTAuMjI2IDAgLTAuNDUyIDAuMTA3IC0wLjY2OSAwLjMyNCAtMC45MjIgMC45MjIgLTEuODQyIDEuODQ1IC0yLjc2MyAyLjc2OCAtMC4yMzMgMC4yMzMgLTAuNDU1IDAuNDggLTAuNzAzIDAuNjk1IC0wLjMxIDAuMjY3IC0wLjQwNSAwLjU4MyAtMC4zOTkgMC45ODggMC4wMiAxLjM5OSAwLjAwOCAyLjc5OSAwLjAwOCA0LjE5OCAwIDEuNDUzIC0wLjAwMiAyLjkwNyAwIDQuMzYgMCAwLjExIDAuMDAyIDAuMjIzIDAuMDMgMC4zMjcgMC4wODcgMC4zMzcgMC4zMDMgMC4zOTMgMC41NDYgMC4xNSAxLjMxIC0xLjMxIDIuNjE4IC0yLjYyMiAzLjkyOCAtMy45MzNsNC40NDkgLTQuNDUzYzAuNDMgLTAuNDMxIDAuNDMgLTAuOTA1IDAgLTEuMzM2TDEyLjY5NyAwLjM3Yy0wLjIxNiAtMC4yMTcgLTAuNDQyIC0wLjMyNCAtMC42NjggLTAuMzI0em03LjIyNCA3LjIzYy0wLjIyMyAwIC0wLjQ0NSAwLjEwNCAtMC42NSAwLjMwOUwxNC44MiAxMS4zN2MtMC40MjggMC40MjkgLTAuNDI3IDAuODk1IDAgMS4zMjJsMy43NiAzLjc2NmMwLjQ0IDAuNDQgMC45MDggMC40NCAxLjM0NiAwLjAwMiAxLjIxNSAtMS4yMTYgMi40MjcgLTIuNDMzIDMuNjQ0IC0zLjY0NyAwLjE4MiAtMC4xOCAwLjM1MyAtMC4zNjQgMC40MyAtMC42MTV2LTAuMzNjLTAuMDc3IC0wLjI1MSAtMC4yNDYgLTAuNDM2IC0wLjQyOCAtMC42MTcgLTEuMjI0IC0xLjIyIC0yLjQ0MyAtMi40NDUgLTMuNjY2IC0zLjY2OCAtMC4yMDUgLTAuMjA1IC0wLjQyOSAtMC4zMDcgLTAuNjUyIC0wLjMwN3pNNC4xOCA3LjYxMWMtMC4wODYgMC4wMTQgLTAuMTQ1IDAuMDk0IC0wLjIwNyAwLjE1N0wwLjIwOSAxMS41NzJjLTAuMjggMC4yODQgLTAuMjc4IDAuNjc3IDAuMDA0IDAuOTZsMi4wNDMgMi4wNDZjMC41OSAwLjU5IDEuMTc3IDEuMTgyIDEuNzY3IDEuNzcyIDAuMTY5IDAuMTY4IDAuMzMgMC4xMzkgMC40MTYgLTAuMDg0IDAuMDQ0IC0wLjExNCAwLjA2MiAtMC4yNDIgMC4wNjMgLTAuMzY0IDAuMDA0IC0xLjI4MyAwLjAwNCAtMi41NjcgMC4wMDQgLTMuODUxaC0wLjAwMlY4LjE4NGMwIC0wLjA4NSAtMC4wMSAtMC4xNjkgLTAuMDIyIC0wLjI1MiAtMC4wMTkgLTAuMTM1IC0wLjA3MiAtMC4yNTggLTAuMjA3IC0wLjMwOWEwLjE4NiAwLjE4NiAwIDAgMCAtMC4wOTUgLTAuMDEyem03LjkwOCA2LjgzOGMtMC4yMjQgMCAtMC40NDcgMC4xMDYgLTAuNjU2IDAuMzE1TDcuNjYgMTguNTM3Yy0wLjQzMyAwLjQzNCAtMC40MzMgMC44OTkgMC4wMDIgMS4zMzQgMS4yMTUgMS4yMTYgMi40MyAyLjQzIDMuNjQzIDMuNjQ5IDAuMTggMC4xOCAwLjM2MSAwLjM1NCAwLjYxMSAwLjQzM2gwLjMzYzAuMjQ0IC0wLjA2OSAwLjQyMyAtMC4yMjYgMC41OTggLTAuNDAyIDEuMjIyIC0xLjIzIDIuNDUgLTIuNDUzIDMuNjc2IC0zLjY4IDAuNDMgLTAuNDMgMC40MjcgLTAuOTA1IC0wLjAwNCAtMS4zMzhsLTMuNzcyIC0zLjc3M2MtMC4yMDggLTAuMjA4IC0wLjQzMiAtMC4zMTEgLTAuNjU2IC0wLjMxeiIgZmlsbD0iIzAwMDAwMCIgc3Ryb2tlLXdpZHRoPSIxIj48L3BhdGg+Cjwvc3ZnPg=="


def main():
    _Main()()


class _Main:
    def __call__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--url", default=os.getenv("VAR_URL"), required=not os.getenv("VAR_URL")
        )
        parser.add_argument("--username", default=os.getenv("VAR_USERNAME"))
        parser.add_argument("--password", default=os.getenv("VAR_PASSWORD"))
        parser.add_argument("--log-filename", default=os.getenv("VAR_LOG_FILENAME"))
        subparsers = parser.add_subparsers(dest="command")
        set_status_parser = subparsers.add_parser("set-status")
        set_status_parser.add_argument("status", choices=["playing", "paused"])
        args = parser.parse_args()

        cmd_kwargs = dict(args._get_kwargs())
        cmd_name = cmd_kwargs.pop("command")
        url = cmd_kwargs.pop("url")
        username = cmd_kwargs.pop("username")
        password = cmd_kwargs.pop("password")
        log_filename = cmd_kwargs.pop("log_filename")

        self._config = Config(url, username, password, log_filename)

        setup_logging(self._config)

        self._logger = logging.getLogger(f"{__name__}.main")

        self._logger.debug(
            f"config={dataclasses.replace(self._config, password='<REDACTED>')}"
        )

        self._kodi_rpc = KodiRpc(
            self._config.url.rstrip("/") + "/jsonrpc",
            self._config.username,
            self._config.password,
        )

        cmd_func = {
            None: self._cmd_default,
            "set-status": self._cmd_set_status,
        }[cmd_name]

        self._logger.debug(f"calling {cmd_func.__name__}({cmd_kwargs})")

        cmd_func(**cmd_kwargs)

    def _cmd_default(self):
        self_abspath = os.path.abspath(sys.argv[0])

        first_active_player_id = self._get_first_active_player_id()

        status = "inactive"
        playing_title = None
        time = None
        total_time = None
        if first_active_player_id is not None:
            properties = self._kodi_rpc.call(
                "Player.GetProperties",
                playerid=first_active_player_id,
                properties=["speed", "time", "totaltime"],
            )

            item = self._kodi_rpc.call(
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

            time = timedelta_from_kodi_time(properties["time"])
            total_time = timedelta_from_kodi_time(properties["totaltime"])
            speed = properties["speed"]

            status = "playing" if speed > 0 else "paused"

            if item["type"] == "episode":
                self._logger.debug("Constructing title for tvshow")
                playing_title = f"{item['showtitle']} S{item['season']:02d}E{item['episode']:02d}: {item['title']}"
            elif item["type"] == "movie":
                self._logger.debug("Constructing title for movies")
                playing_title = f"{item['title']} ({item['year']})"
            elif item["title"]:
                self._logger.debug(
                    "Constructing title for item with a 'title' property"
                )
                playing_title = item["title"]
            elif item["label"]:
                self._logger.debug(
                    "Constructing title for item with a 'label' property"
                )
                playing_title = item["label"]

        self._output(f"| templateImage={ICON}")
        self._output("---")
        if status in {"playing", "paused"}:
            if playing_title is not None:
                self._output(
                    f"{playing_title.replace('|', '')} | href={self._config.url}"
                )
            else:
                self._output(f"<Unknown title> | href={self._config.url}")

            if status == "playing":
                status_title = "▶️ Playing (click to pause)"
                action_status = "paused"
            elif status == "paused":
                status_title = "⏸️ Paused (click to play)"
                action_status = "playing"
            else:
                raise ValueError("Unexpected status")

            self_params = [
                f"--url={self._config.url}",
                f"--username={self._config.username}",
                f"--password={self._config.password}",
                f"--log-filename={self._config.log_filename}",
                "set-status",
                action_status,
            ]
            self._output(
                f"{status_title} | color=#feeeee {self._self_params_str(*self_params)}"
            )

            if time is not None and total_time is not None:
                remaining = total_time - time
                self._output(
                    f"{format_timedelta_hms(time)} / {format_timedelta_hms(total_time)} "
                    f"({format_timedelta_hms(remaining)} remaining) | "
                    "color=#9f9f9e"
                )
        else:
            self._output(f"Not playing | href={self._config.url}")

    def _cmd_set_status(self, status):
        first_active_player_id = self._get_first_active_player_id()

        if not first_active_player_id:
            return

        self._kodi_rpc.call(
            "Player.PlayPause",
            playerid=first_active_player_id,
            play=status == "playing",
        )

    def _output(self, line: str):
        print(line)
        self._logger.debug(f"Output: {line}")

    def _get_first_active_player_id(self):
        active_players = self._kodi_rpc.call("Player.GetActivePlayers")
        if active_players:
            return active_players[0]["playerid"]
        else:
            return None

    def _self_params_str(self, *args):
        kwargs = {"shell": os.path.abspath(sys.argv[0])}
        for i, arg in enumerate(args):
            kwargs[f"param{i + 1}"] = arg
        return " ".join(f"{key}={shlex.quote(value)}" for key, value in kwargs.items())


@dataclasses.dataclass
class Config:
    url: str
    username: str
    password: str
    log_filename: str


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
        self._logger = logging.getLogger(f"{__name__}.{type(self).__name__}")

    def call(self, method, *args, **kwargs):
        if args and kwargs:
            raise ValueError(
                "*args or **kwargs can be passed to Kodi RPC, but not both"
            )

        req_headers = {"Content-Type": "application/json"}

        if self._username or self._password:
            username_password = f"{self._username}:{self._password}"
            req_headers["Authorization"] = (
                f"Basic {base64.b64encode(username_password.encode()).decode()}"
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

        redacted_req_headers = dict(
            (key, "<REDACTED>" if key in {"Authorization"} else value)
            for (key, value) in req_headers.items()
        )
        self._logger.debug(
            f"request headers={redacted_req_headers} payload={req_payload}"
        )

        with urllib.request.urlopen(req) as res:
            res_status = res.status
            res_headers = res.headers
            res_content_type = res_headers.get("Content-Type")
            res_body = res.read()

            self._logger.debug(
                f"response status={res_status} headers={dict(res_headers)} body={res_body}"
            )

            if not 200 <= res_status <= 299:
                raise Exception(f"Unexpected HTTP {res.status} with body {res_body!r}")

            if res_content_type != "application/json":
                raise Exception(f"Unexpected content-type {res_content_type!r}")

            res_payload = json.loads(res_body)

            res_error = res_payload.get("error")
            if res_error:
                res_error_code = res_error.get("code")
                res_error_message = res_error.get("message")
                res_data = res_error.get("data")
                raise Exception(res_error_code, res_error_message, res_data)

            return res_payload["result"]


class KodiTime(TypedDict):
    hours: int
    minutes: int
    seconds: int
    milliseconds: int


def timedelta_from_kodi_time(time: KodiTime):
    return timedelta(
        hours=time["hours"],
        minutes=time["minutes"],
        seconds=time["seconds"],
        milliseconds=time["milliseconds"],
    )


def format_timedelta_hms(timedelta: timedelta):
    ts = timedelta.total_seconds()
    h = int(ts) // (60 * 60)
    m = (int(ts) // 60) % 60
    s = int(ts) % 60
    return f"{h}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    main()
