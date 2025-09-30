#!/usr/bin/env python3
"""Call the aiSense ping API and log the response payload."""

from __future__ import annotations

import json
import logging
import sys
import urllib.error
import urllib.request

API_URL = "https://aisenseapi.com/services/v1/ping"
LOG_FILE = "ping.log"


def setup_logger() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def call_ping_api() -> str:
    request = urllib.request.Request(API_URL, method="GET")
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = response.read().decode(response.headers.get_content_charset("utf-8"))
    return payload


def main() -> int:
    setup_logger()
    try:
        payload = call_ping_api()
    except urllib.error.URLError as exc:
        logging.exception("Failed to call %s", API_URL)
        return 1

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        logging.info("API response: %s", payload)
    else:
        logging.info("API response: %s", json.dumps(parsed))

    return 0


if __name__ == "__main__":
    sys.exit(main())


