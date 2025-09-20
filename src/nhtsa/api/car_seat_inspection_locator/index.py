from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging

from .models import CarSeatInspectionStationList

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class CarSeatInspectionLocatorAPI:
    """
    API for locating Car Seat Inspection Stations.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the CarSeatInspectionLocatorAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def get_stations_by_zip_code(self, zip_code: str, lang_spanish: bool = False, cps_week: bool = False) -> CarSeatInspectionStationList:
        """
        Make the request with a ZIP code to get the list of CSSIStations at the specific ZIP code only.

        Args:
            zip_code (str): The ZIP code to search for.
            lang_spanish (bool): If True, filters for Spanish-speaking stations.
            cps_week (bool): If True, filters for stations participating in CPS Week.

        Returns:
            CarSeatInspectionStationList: A Pydantic model representing a list of CSSI Stations.
        """
        url = f"/CSSIStation/zip/{zip_code}"
        if lang_spanish:
            url += "/lang/spanish"
        if cps_week:
            url += "/cpsweek"
        response = await self.client._request("GET", url)
        return parse_obj_as(CarSeatInspectionStationList, response.json())

    async def get_stations_by_state(self, state_abbreviation: str, lang_spanish: bool = False, cps_week: bool = False) -> CarSeatInspectionStationList:
        """
        Make the request with the state abbreviation to get the list of CSSIStations in that state only.

        Args:
            state_abbreviation (str): The two-letter state abbreviation.
            lang_spanish (bool): If True, filters for Spanish-speaking stations.
            cps_week (bool): If True, filters for stations participating in CPS Week.

        Returns:
            CarSeatInspectionStationList: A Pydantic model representing a list of CSSI Stations.
        """
        url = f"/CSSIStation/state/{state_abbreviation}"
        if lang_spanish:
            url += "/lang/spanish"
        if cps_week:
            url += "/cpsweek"
        response = await self.client._request("GET", url)
        return parse_obj_as(CarSeatInspectionStationList, response.json())

    async def get_stations_by_geo_location(self, lat: float, long: float, miles: int, lang_spanish: bool = False, cps_week: bool = False) -> CarSeatInspectionStationList:
        """
        Make the request with an interested latitude and longitude location along with the miles nearby
        to look out for CSSIStations.

        Args:
            lat (float): The latitude of the location.
            long (float): The longitude of the location.
            miles (int): The radius in miles to search within.
            lang_spanish (bool): If True, filters for Spanish-speaking stations.
            cps_week (bool): If True, filters for stations participating in CPS Week.

        Returns:
            CarSeatInspectionStationList: A Pydantic model representing a list of CSSI Stations.
        """
        url = f"/CSSIStation?lat={lat}&long={long}&miles={miles}"
        if lang_spanish:
            url += "/lang/spanish"
        if cps_week:
            url += "/cpsweek"
        response = await self.client._request("GET", url)
        return parse_obj_as(CarSeatInspectionStationList, response.json())
