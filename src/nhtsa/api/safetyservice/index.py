from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging

from .models import SafetyRatingModelYear, SafetyRatingMake, SafetyRatingModel, VehicleVariant, SafetyRatingResult

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class SafetyServiceAPI:
    """
    API for fetching NHTSA Safety Ratings information.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the SafetyServiceAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def get_vehicle_variants(self, model_year: int, make: str, model: str) -> VehicleVariant:
        """
        Get available vehicle variants for a selected Model Year, Make, and Model.

        Args:
            model_year (int): The model year of the vehicle.
            make (str): The make of the vehicle.
            model (str): The model of the vehicle.

        Returns:
            VehicleVariant: A Pydantic model representing the vehicle variants.
        """
        url = f"/SafetyRatings/modelyear/{model_year}/make/{make}/model/{model}"
        response = await self.client._request("GET", url)
        return parse_obj_as(VehicleVariant, response.json())

    async def get_safety_ratings_by_vehicle_id(self, vehicle_id: int) -> SafetyRatingResult:
        """
        Get the Safety Ratings for the selected vehicle variant by Vehicle Id.

        Args:
            vehicle_id (int): The unique ID of the vehicle variant.

        Returns:
            SafetyRatingResult: A Pydantic model representing the safety ratings for the given vehicle variant.
        """
        url = f"/SafetyRatings/VehicleId/{vehicle_id}"
        response = await self.client._request("GET", url)
        return parse_obj_as(SafetyRatingResult, response.json())

    async def get_all_model_years(self) -> SafetyRatingModelYear:
        """
        Request a list of available Model Years for a given product type (Vehicle).

        Returns:
            SafetyRatingModelYear: A Pydantic model representing a list of available model years.
        """
        url = "/SafetyRatings"
        response = await self.client._request("GET", url)
        return parse_obj_as(SafetyRatingModelYear, response.json())

    async def get_all_makes_for_model_year(self, model_year: int) -> SafetyRatingMake:
        """
        Request a list of vehicle Makes by providing a specific vehicle Model Year.

        Args:
            model_year (int): The model year to filter by.

        Returns:
            SafetyRatingMake: A Pydantic model representing a list of vehicle makes for that model year.
        """
        url = f"/SafetyRatings/modelyear/{model_year}"
        response = await self.client._request("GET", url)
        return parse_obj_as(SafetyRatingMake, response.json())

    async def get_all_models_for_make_and_model_year(self, model_year: int, make: str) -> SafetyRatingModel:
        """
        Request a list of vehicle Models by providing the vehicle Model Year and Make.

        Args:
            model_year (int): The model year to filter by.
            make (str): The make to filter by.

        Returns:
            SafetyRatingModel: A Pydantic model representing a list of models for the given model year and make.
        """
        url = f"/SafetyRatings/modelyear/{model_year}/make/{make}"
        response = await self.client._request("GET", url)
        return parse_obj_as(SafetyRatingModel, response.json())
