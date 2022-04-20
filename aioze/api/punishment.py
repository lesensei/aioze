import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Punishment:
    def __init__(self, access: Access):
        self._access = access

    async def get_punishments(
        self,
        pupil,
        start_date: datetime,
        end_date: datetime = None,
        days: int = 1
    ):
        """Get punishments for a given pupil (uid = student id)"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        # start = start_date or dt.start_of_local_day()
        end = end_date or (start_date + timedelta(days=days))
        params = {
            "ctx_profil": self._access.profil,
            "ctx_etab": pupil['etab'],
            "aUserId": pupil['uid'],
            "aDateDebut": start_date.astimezone().replace(microsecond=0).isoformat()[:-6]
            + "Z",
            "aDateFin": end.astimezone().replace(microsecond=0).isoformat()[:-6] + "Z",
            "aIsPunitionNonExecutee": "true",
        }
        punish_url = urljoin(self._access.api_url, "/v1/viescolaire/punition")
        _LOGGER.debug("Getting '%s' with params '%s'", punish_url, json.dumps(params))
        res = await self._access.api_wrapper("get", punish_url, params=params)
        if res.status != 200:
            _LOGGER.error(
                "Error fetching Oze punishments for '%s': '%s'", pupil['name'], res.reason
            )
            return
        return await res.json()
