import json
import ssl

import hishel
import httpx
from PyQt5.uic.Compiler.qobjectcreator import logger
from tenacity import retry, retry_if_exception_type

controller = hishel.Controller(
    cacheable_methods=["GET", "POST"],
    cacheable_status_codes=[200],
    allow_stale=True,
    always_revalidate=True,
)

ssl_context = ssl.create_default_context()
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

transport = httpx.HTTPTransport(retries=3)
storage = hishel.FileStorage()

requests = hishel.CacheClient(
    controller=controller,
    http2=True,
    verify=ssl_context,
    transport=transport,
    storage=storage,
)


class ServiceError(Exception):
    def __init__(self, service, params, message):
        self.params = params
        self.message = message
        self.service = service
        super().__init__(self.message)

    def __str__(self):
        return f"Ocurrio un error: {self.params}"


@retry(
    retry=retry_if_exception_type(httpx.TimeoutException)
    | retry_if_exception_type(httpx.ReadTimeout)
    | retry_if_exception_type(httpx.WriteTimeout)
)
def request(method, url, headers=None, extensions=None):
    if isinstance(headers, str) and headers != "":
        headers = json.loads(headers)
    if extensions is None:
        extensions = {"force_cache": True}
    response = requests.request(method, url=url.replace("%3F", "?"), headers=headers, extensions=extensions)

    try:
        body = response.json()
        if response.status_code != 200:
            return json.dumps(body)
        logger.info(body)
        return json.dumps(body)
    except Exception as e:
        logger.warn(url+str(e))
        return json.dumps({"error": str(e)})


def post(url, headers=None):
    return request("POST", url, headers)


def http_get(url, headers=None):
    return request("GET", url, headers)
