from json import dumps
import logging
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Grade:
    def __init__(self, access: Access):
        self._access = access

    async def get_grades(self, pupil):
        """Get grade averages for a given student"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        # https://api-enc.hauts-de-seine.fr/v1/viescolaire/EHNotesFamille?aEleveIds=6123d148a14ce70e0ca6f797&ctx_etab=0920077J&ctx_profil=RESPONSABLE_ELEVE
        params = {
            "ctx_profil": self._access.profil,
            "ctx_etab": self._access.etab,
            "aEleveIds": pupil['uid']
        }
        grades_url = urljoin(self._access.api_url, "/v1/viescolaire/EHNotesFamille")
        _LOGGER.debug("Getting '%s' with params '%s'", grades_url, dumps(params))
        res = await self._access.api_wrapper("get", grades_url, params=params)
        if res.status != 200:
            _LOGGER.error("Error fetching grades: '%s'", res.reason)
            return
        return await res.json()
