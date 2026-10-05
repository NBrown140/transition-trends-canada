import time

import requests


def download(url: str, attempts: int = 5, timeout: float = 60) -> bytes:
    """Download a file, retrying on connection errors, stalls and truncated responses.

    `timeout` bounds each socket read (not the whole transfer), so a stalled
    server fails fast instead of hanging the CI job.
    """
    for attempt in range(1, attempts + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                content = b"".join(r.iter_content(chunk_size=1 << 20))
                expected = r.headers.get("Content-Length")
                if expected is not None and "Content-Encoding" not in r.headers and len(content) != int(expected):
                    raise IOError(f"Incomplete download: got {len(content)} of {expected} bytes")
                return content
        except (requests.RequestException, IOError) as e:
            if attempt == attempts:
                raise
            wait = 10 * attempt
            print(f"Download of {url} failed ({e}), retrying in {wait}s ({attempt}/{attempts})")
            time.sleep(wait)
