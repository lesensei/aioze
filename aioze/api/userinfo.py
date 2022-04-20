import logging
from typing import Any, List
from urllib.parse import urljoin

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class UserInfo:
    def __init__(self, access: Access):
        self._access = access

    async def get_user_info(self):
        """Get authenticated user information"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        user_info_url = urljoin(self._access.api_url, "v1/users/me")
        _LOGGER.debug("Getting '%s'", user_info_url)
        res = await self._access.api_wrapper("get", user_info_url)
        if res.status != 200:
            _LOGGER.error("Error fetching Oze user information: '%s'", res.reason)
            return
        return await res.json()

    @staticmethod
    def get_pupils_from_userinfo(user_info: dict[str, Any]) -> List[dict[str, str]]:
        pupils = []
        for pupil in user_info['relations']:
            pupils.append({
                "uid": pupil['user']['id'],
                "last_name": pupil['user']['nom'],
                "first_name": pupil['user']['prenom'],
                "etab": user_info['currentUai']
            })
        return pupils
