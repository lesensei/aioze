import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Event:
    def __init__(self, access: Access):
        self._access = access

    async def get_events(
        self,
        start_date: datetime,
        end_date: datetime = None,
        pupil=None,
        days: int = 1,
    ):
        """Get events for a given calendar (uid = student id)"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        # start = start_date or dt.start_of_local_day()
        end = end_date or (start_date + timedelta(days=days))
        _pupil = pupil or self._access.pupils[0]
        params = {
            "ctx_profil": self._access.profil,
            "ctx_etab": _pupil['etab'],
            "aDateDebut": start_date.astimezone().replace(microsecond=0).isoformat()[:-6]
            + "Z",
            "aDateFin": end.astimezone().replace(microsecond=0).isoformat()[:-6] + "Z",
            "aPupilles": _pupil['uid'],
            "aWithCurrent": "false",
            "aUais": _pupil['etab'],
        }
        cours_url = urljoin(self._access.api_url, "/v1/cours/me")
        _LOGGER.debug("Getting '%s' with params '%s'", cours_url, json.dumps(params))
        res = await self._access.api_wrapper("get", cours_url, params=params)
        if res.status != 200:
            _LOGGER.error("Error fetching Oze events for '%s': '%s'", _pupil['name'], res.reason)
            return
        return await res.json()
