import logging
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Notification:
    def __init__(self, access: Access):
        self._access = access

    async def get_notifications(self, pupil=None):
        """Get notifications"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        annee_url = urljoin(self._access.api_url, "/v1/etabs/zone/annee")
        _pupil = pupil or self._access.pupils[0]
        params = {
            "aNotNull": "true",
            "ctx_etab": _pupil['etab'],
            "ctx_profil": self._access.profil,
        }
        res = await self._access.api_wrapper("get", annee_url, params=params)
        if res.status != 200:
            _LOGGER.error(
                "Error fetching Oze year data: '%s'", res.reason
            )
            return
        annee_data = await res.json()
        _LOGGER.debug("Année: %s", annee_data)
        notifications_url = urljoin(self._access.api_url, "/v1/notifications")
        params = {
            "aDateFin": annee_data['fin'],
            "aDateDebut": annee_data['debut'],
            "range": "0-20",
            "ctx_etab": _pupil['etab'],
            "ctx_profil": self._access.profil,
        }
        res = await self._access.api_wrapper("get", notifications_url, params=params)
        if res.status != 200:
            _LOGGER.error(
                "Error fetching Oze notifications: '%s'", res.reason
            )
            return
        return await res.json()
