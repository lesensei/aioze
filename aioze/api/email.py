import json
import logging
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Email:
    def __init__(self, access: Access):
        self._access = access

    async def get_emails(self):
        """Get events for a given calendar (uid = student id)"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        params = {
            "pFolderId": "/inbox",
            "pIncludeRead": "true",
            "pIncludeUnread": "true",
            "pIncludeWithAttach": "true",
            "pIncludeWithout": "true",
            "pSortPattern": "dt_inv",
            "pPageSize": "15",
            "ctx_profil": self._access.profil,
            "ctx_etab": self._access.etab,
        }
        cours_url = urljoin(self._access.api_url, "/v1/email/messages")
        _LOGGER.debug("Getting '%s' with params '%s'", cours_url, json.dumps(params))
        res = await self._access.api_wrapper("get", cours_url, params=params)
        if res.status != 200:
            _LOGGER.error("Error fetching Oze emails: '%s'", res.reason)
            return
        return await res.json()
