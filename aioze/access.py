import asyncio
import socket
import aiohttp
import async_timeout
import logging
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__package__)


class Access:
    """Connection control."""

    def __init__(self, session: aiohttp.ClientSession, base_url, api_url, username, password, timeout):
        """Init class."""
        self.session = session
        self.base_url = base_url
        self.api_url = api_url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.profil = None

    async def is_authenticated(self) -> bool:
        """Check if session is authenticated to the OzE instance"""
        res = await self.api_wrapper("get", urljoin(self.api_url, "v1/users/me"))
        _LOGGER.debug("res: %s", res)
        _LOGGER.debug("req: %s", res.request_info)
        if res.status != 200:
            return False
        info: dict = await res.json()
        self.profil = info['currentProfil']['codeProfil']
        _LOGGER.debug("JSON result: '%s'", info)
        return True

    async def authenticate(self) -> bool:
        """Authenticate to the OzE instance"""
        if await self.is_authenticated():
            return True
        # Get the necessary cookies (in my testing, both GETs seemed to be needed)
        res = await self.api_wrapper("get", self.base_url)
        _LOGGER.debug("res: %s", res)
        _LOGGER.debug("req: %s", res.request_info)
        res = await self.api_wrapper("get", urljoin(self.base_url, "my.policy"))
        _LOGGER.debug("res: %s", res)
        _LOGGER.debug("req: %s", res.request_info)
        # POST login information
        res = await self.api_wrapper(
            "post",
            urljoin(self.base_url, "my.policy"),
            data={
                "username": self.username,
                "password": self.password,
                "fakepassword": "fake",
                "private": "prive",
                "vhost": "standard",
                "SubmitCreds.x": "196",
                "SubmitCreds.y": "26",
            },
        )
        _LOGGER.debug("res: %s", res)
        _LOGGER.debug("req: %s", res.request_info)
        return await self.is_authenticated()

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}, params: dict = {}
    ) -> aiohttp.ClientResponse:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(self.timeout):
                if method == "get":
                    return await self.session.get(url, headers=headers, params=params, allow_redirects=False)

                elif method == "post":
                    return await self.session.post(url, headers=headers, data=data, allow_redirects=False)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )
            raise

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
            raise

        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
            raise

        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
            raise
