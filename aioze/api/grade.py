from json import dumps
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import dateparser

from aioze.access import Access

_LOGGER = logging.getLogger(__package__)


class Grade:
    def __init__(self, access: Access):
        self._access = access

    async def get_grades(self):
        """Get grade averages for a given student"""
        if not await self._access.is_authenticated():
            await self._access.authenticate()
        params = {
            "ctx_profil": self._access.profil,
            "ctx_etab": self._access.etab,
        }
        auth_url = urljoin(self._access.api_url, "/v1/config/EH%20Notes%20Parents")
        _LOGGER.debug("Getting '%s' with params '%s'", auth_url, dumps(params))
        res = await self._access.api_wrapper("get", auth_url, params=params)
        if res.status != 200:
            _LOGGER.error("Error fetching proxySSO auth ID: '%s'", res.reason)
            return
        json = await res.json()
        authId = json["autorisationId"]
        params = {
            "uai": self._access.etab,
            "projet": "OZE_HDS",
            "fonction": "TUT",
        }
        proxy_url = urljoin(self._access.base_url, f"/cas/proxySSO/{authId}")
        _LOGGER.debug("Getting '%s' with params '%s'", proxy_url, dumps(params))
        res = await self._access.api_wrapper("get", proxy_url, params=params)
        if res.status != 302:
            _LOGGER.error("Error calling proxySSO at '%s': '%s'", res.request_info.url, res.reason)
            return
        grades_url = res.headers.get("Location")
        _LOGGER.debug("Getting '%s'", grades_url)
        res = await self._access.api_wrapper("get", grades_url)
        if res.status != 302:
            _LOGGER.error("Error getting grades URL at '%s': '%s'", res.request_info.url, res.reason)
            return
        grades_url = res.headers.get("Location")
        _LOGGER.debug("Getting '%s'", grades_url)
        res = await self._access.api_wrapper("get", grades_url)
        if res.status != 302:
            _LOGGER.error("Error getting grades URL with session at '%s': '%s'", res.request_info.url, res.reason)
            return
        login_url = res.headers.get("Location")
        _LOGGER.debug("Getting '%s'", login_url)
        res = await self._access.api_wrapper("get", login_url)
        if res.status != 302:
            _LOGGER.error("Error getting login URL at '%s': '%s'", res.request_info.url, res.reason)
            return
        auth_url = res.headers.get("Location")
        _LOGGER.debug("Getting '%s'", auth_url)
        res = await self._access.api_wrapper("get", auth_url)
        if res.status != 302:
            _LOGGER.error("Error getting auth URL at '%s': '%s'", res.request_info.url, res.reason)
            return
        grades_url = urljoin(self._access.base_url, "/eh/parent/listeNotes.jsp")
        _LOGGER.debug("Getting '%s'", grades_url)
        res = await self._access.api_wrapper("get", grades_url)
        if res.status != 200:
            _LOGGER.error("Error getting grades at '%s': '%s'", res.request_info.url, res.reason)
            return
        gradesHtml = BeautifulSoup(await res.text(), 'html.parser')
        courses = []
        for courseHtml in gradesHtml.select('.tableaunotes'):
            course = {}
            course['label'] = courseHtml.select_one('tr:first-of-type > td > a').string
            course['grades'] = []
            for gradeHtml in courseHtml.select('tr[id^=ligne]'):
                grade = {}
                grade['label'] = gradeHtml.select_one('td:first-of-type').string
                gradeDate = list(gradeHtml.select_one('td:nth-of-type(3)').stripped_strings)[0]
                gradeDate = dateparser.parse(gradeDate, languages=['fr'])
                grade['date'] = gradeDate
                gradeList = list(gradeHtml.select_one('td:nth-of-type(4)').stripped_strings)
                grade['grade'] = (gradeList[-2] if gradeList[-1] == '/20)' else gradeList[0])
                course['grades'].append(grade)
            course['mean'] = list(courseHtml.select_one('tr:last-of-type > td:nth-of-type(2)').stripped_strings)[0]
            courses.append(course)
        return courses
