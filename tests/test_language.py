from unittest.mock import patch

import httpx
import pytest
from ecohome import AsyncEcoHomeClient

from custom_components.ecohome.language import apply_language, default_language


@pytest.mark.parametrize(
    ("ha_language", "expected"),
    [
        ("es", "es_ES"),
        ("pt-BR", "pt_BR"),
        ("pt", "pt_PT"),
        ("en-GB", "en_US"),
        ("nl", "en_US"),  # the API has no Dutch parameter names
    ],
)
async def test_default_language_follows_home_assistant(hass, ha_language, expected):
    hass.config.language = ha_language
    assert default_language(hass) == expected


async def test_apply_language_rewrites_api_requests():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"errorCode": 200, "objectResult": []})

    real_async_client = httpx.AsyncClient

    def async_client(**kwargs):
        return real_async_client(transport=httpx.MockTransport(handler), **kwargs)

    client = apply_language(AsyncEcoHomeClient(token="token"), "es_ES")
    with patch("ecohome.client.httpx.AsyncClient", side_effect=async_client):
        await client.get_param_list("WM1A23012982", 0)

    assert requests[0].url.params["lang"] == "es_ES"
    assert requests[0].headers["Accept-Language"] == "es-ES"
