import logging
from datetime import datetime
from dateutil import tz
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Homework:
    def __init__(self, access: Access):
        self._access = access

    async def get_homework(self, pupil):
        """Get howework"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        annee_url = urljoin(self._access.api_url, "/v1/etabs/zone/annee")
        params = {
            "aNotNull": "true",
            "ctx_etab": pupil['etab'],
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
        homework_url = urljoin(self._access.api_url, "/v1/travaux/liste")
        start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        params = {
            "aDateDebut": start.astimezone(tz.UTC).isoformat()[:-9],
            "aDateFin": annee_data['fin'][:-4],
            "aIdsUsers": pupil['uid'],
            "ctx_etab": pupil['etab'],
            "ctx_profil": self._access.profil,
        }
        res = await self._access.api_wrapper("get", homework_url, params=params)
        if res.status != 200:
            _LOGGER.error(
                "Error fetching Oze information notices: '%s'", res.reason
            )
            return
        return await res.json()
