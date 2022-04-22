import logging
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Information:
    def __init__(self, access: Access):
        self._access = access

    async def get_informations(self, pupil = None):
        # pylint: disable=unused-argument
        """Get information notices"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        info_url = urljoin(self._access.api_url, "/v1/information/lecteur")
        params = {
            "start": 0,
            "limit": 10,
            "activeState": 0,
            "periodTypeSelected": "CURRENTYEAR",
            "allInformations": "false",
            "ctx_etab": self._access.etab,
            "ctx_profil": self._access.profil,
        }
        res = await self._access.api_wrapper("get", info_url, params=params)
        if res.status != 200:
            _LOGGER.error(
                "Error fetching Oze information notices: '%s'", res.reason
            )
            return
        return await res.json()
