# ping.py
import os
import logging
import socket
from typing import Any, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Optional: prefer IPv4 to avoid IPv6 blackholes
# System-wide way is /etc/gai.conf, but this is a simple process-level nudge:
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined]
LOG_FILE = "ping.log"
log = logging.getLogger(__name__)
def setup_logger() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True)

PING_URL = os.getenv("PING_URL", "https://aisenseapi.com/services/v1/ping")
DEFAULT_TIMEOUT = (5, 10)  # (connect_timeout, read_timeout) seconds

def _session() -> requests.Session:
    s = requests.Session()

    # Retry on transient network / TLS / 5xx errors
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.5,                  # exponential backoff: 0.5, 1, 2, 4...
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET","POST","PUT","DELETE","HEAD","OPTIONS","TRACE"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    # Optional: if you have a corporate proxy, requests respects HTTPS_PROXY/NO_PROXY env vars.
    # Ensure NO_PROXY includes your internal hosts if needed.
    return s

def call_ping_api() -> Dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "ping-bot/1.0",
    }

    try:
        with _session() as s:
            resp = s.get(PING_URL, headers=headers, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            return resp.json() if "application/json" in resp.headers.get("content-type","").lower() else {"text": resp.text}

    except requests.exceptions.SSLError as e:
        # TLS-level error (certs, handshake). Log the root cause.
        log.exception("TLS handshake failed: %s", e)
        raise
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
        log.exception("Network timeout connecting to %s: %s", PING_URL, e)
        raise
    except requests.exceptions.ConnectionError as e:
        # DNS issues, refused connections, IPv6 blackholes, etc.
        log.exception("Connection error to %s: %s", PING_URL, e)
        raise
    except Exception as e:
        log.exception("Unexpected error calling %s: %s", PING_URL, e)
        raise

def main():
    log.info("Ping start.")
    payload = call_ping_api()
    log.info("Ping payload: %r", payload)

if __name__ == "__main__":
    setup_logger()
    main()