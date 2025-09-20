from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging

from .models import RecallByVehicle, ModelYear, Make, Model, RecallCampaign

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class RecallsAPI:
    """
    API for fetching NHTSA Recalls information.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the RecallsAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def get_recalls_by_vehicle(self, make: str, model: str, model_year: int) -> RecallByVehicle:
        """
        Get recalls for the required combination of Model Year, Make, and Model.

        Args:
            make (str): The make of the vehicle.
            model (str): The model of the vehicle.
            model_year (int): The model year of the vehicle.

        Returns:
            RecallByVehicle: A Pydantic model representing a list of recalls for the given vehicle.
        """
        url = f"/recalls/recallsByVehicle?make={make}&model={model}&modelYear={model_year}"
        response = await self.client._request("GET", url)
        return parse_obj_as(RecallByVehicle, response.json())

    async def get_all_model_years(self) -> ModelYear:
        """
        Request a list of available Model Years for a given product type (Vehicle) for recalls.

        Returns:
            ModelYear: A Pydantic model representing a list of available model years.
        """
        url = "/products/vehicle/modelYears?issueType=r"
        response = await self.client._request("GET", url)
        return parse_obj_as(ModelYear, response.json())

    async def get_all_makes_for_model_year(self, model_year: int) -> Make:
        """
        Request a list of vehicle Makes by providing a specific vehicle Model Year for recalls.

        Args:
            model_year (int): The model year to filter by.

        Returns:
            Make: A Pydantic model representing a list of vehicle makes for that model year.
        """
        url = f"/products/vehicle/makes?modelYear={model_year}&issueType=r"
        response = await self.client._request("GET", url)
        return parse_obj_as(Make, response.json())

    async def get_all_models_for_make_and_model_year(self, model_year: int, make: str) -> Model:
        """
        Request a list of vehicle Models by providing the vehicle Model Year and Make for recalls.

        Args:
            model_year (int): The model year to filter by.
            make (str): The make to filter by.

        Returns:
            Model: A Pydantic model representing a list of models for the given model year and make.
        """
        url = f"/products/vehicle/models?modelYear={model_year}&make={make}&issueType=r"
        response = await self.client._request("GET", url)
        return parse_obj_as(Model, response.json())

    async def get_recalls_by_campaign_number(self, campaign_number: str) -> RecallCampaign:
        """
        Get all recalls as part of a NHTSA recall campaign number.

        Args:
            campaign_number (str): The NHTSA recall campaign number.

        Returns:
            RecallCampaign: A Pydantic model representing a list of recalls for the specified campaign number.
        """
        url = f"/recalls/campaignNumber?campaignNumber={campaign_number}"
        response = await self.client._request("GET", url)
        return parse_obj_as(RecallCampaign, response.json())
