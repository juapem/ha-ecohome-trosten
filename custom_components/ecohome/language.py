"""Language the Eco-Home API uses for parameter and mode names.

The ecohome library always requests nl_NL, for which the API has no parameter
name translations and falls back to Portuguese. We rewrite the language of the
requests a client makes after logging in; login itself keeps nl_NL, because the
library recognizes a wrong password by its (localized) error message.
"""

import httpx
from homeassistant.core import HomeAssistant

from ecohome import AsyncEcoHomeClient

# Languages for which the API returns translated parameter names.
LANGUAGES: dict[str, str] = {
    "en_US": "English",
    "es_ES": "Español",
    "de_DE": "Deutsch",
    "fr_FR": "Français",
    "it_IT": "Italiano",
    "pt_PT": "Português (Portugal)",
    "pt_BR": "Português (Brasil)",
}
DEFAULT_LANGUAGE = "en_US"


def default_language(hass: HomeAssistant) -> str:
    """The API language matching Home Assistant's language, if there is one."""
    ha_language = (hass.config.language or "").replace("-", "_")
    if ha_language in LANGUAGES:
        return ha_language
    base = ha_language.split("_")[0]
    return next((code for code in LANGUAGES if code.startswith(f"{base}_")), DEFAULT_LANGUAGE)


def apply_language(client: AsyncEcoHomeClient, language: str) -> AsyncEcoHomeClient:
    async def set_language(request: httpx.Request) -> None:
        request.url = request.url.copy_set_param("lang", language)
        request.headers["Accept-Language"] = language.replace("_", "-")

    make_http = client._http

    async def _http(timeout=None) -> httpx.AsyncClient:
        http = await make_http(timeout)
        http.event_hooks["request"].append(set_language)
        return http

    client._http = _http  # type: ignore[method-assign]
    return client
