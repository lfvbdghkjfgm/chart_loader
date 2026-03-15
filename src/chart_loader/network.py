from __future__ import annotations

from collections.abc import Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CHART_URL_TEMPLATE = "https://lukeairtool.net/viewchart.php?icao={icao}"


class ChartDownloadError(Exception):
    """Raised when chart download fails."""


def build_retry_session(retries: int = 3, backoff_factor: float = 1.0) -> requests.Session:
    retry_strategy = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_chart_pdf(
    icao: str,
    timeout: int = 20,
    session: requests.Session | None = None,
    get_request: Callable[..., requests.Response] | None = None,
) -> bytes:
    own_session = session is None
    active_session = session or build_retry_session()
    request_func = get_request or active_session.get
    url = CHART_URL_TEMPLATE.format(icao=icao)

    try:
        response = request_func(url, timeout=timeout)
    except requests.exceptions.Timeout as exc:
        raise ChartDownloadError(
            "Превышено время ожидания ответа от сервера. Попробуйте позже."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ChartDownloadError(f"Ошибка сети при загрузке чартов: {exc}") from exc
    finally:
        if own_session:
            active_session.close()

    if response.status_code >= 400:
        raise ChartDownloadError(f"Сервер вернул ошибку HTTP {response.status_code}.")

    content_type = response.headers.get("Content-Type", "").lower()
    if "application/pdf" not in content_type:
        if content_type:
            raise ChartDownloadError(
                f"Сервер вернул не PDF-файл (Content-Type: {content_type})."
            )
        raise ChartDownloadError("Сервер не указал Content-Type PDF.")

    return response.content

