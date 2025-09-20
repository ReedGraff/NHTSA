
from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging

from ...lib.models import APIResponse, Error, Meta, Pagination
from .models import TestPerformer, NCode, ModelLookup, FilterClass, CodeDecode

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class NhtsaDatabaseCodeLibraryAPI:
    """
    API for programmatic access to the NHTSA Database Code Library.
    This includes codes and descriptions for data fields defined in the NHTSA Test Reference Guides.
    Base URL for these endpoints starts from the root of the NRD server (/).
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the NhtsaDatabaseCodeLibraryAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client
        self.base_path = "/nhtsa/nhtsadb" # Specific path for this API on the NRD server

    async def get_test_performers(self, database: str) -> APIResponse:
        """
        Retrieves test performers for a given database.

        Args:
            database (str): The database name (e.g., "vehicle", "biomechanics").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/testPerformers/{database}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def list_all_codes(self) -> APIResponse:
        """
        Lists all available NHTSA codes.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/ncodes"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_model_by_make_and_model_id(self, make: str, model: str) -> APIResponse:
        """
        Finds a model by make and model ID.

        Args:
            make (str): The make of the vehicle.
            model (str): The model ID.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/model/{make}/{model}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def list_models_by_make(self, make: str) -> APIResponse:
        """
        Lists models for a given make.

        Args:
            make (str): The make of the vehicle.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/model/list/{make}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def list_all_models(self) -> APIResponse:
        """
        Lists all available models.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/model/"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def list_by_code_name(self, code_name: str) -> APIResponse:
        """
        Lists codes by code name.

        Args:
            code_name (str): The name of the code.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/list/{code_name}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_filter_class(self, senatt: str, sentyp: str, units: str) -> APIResponse:
        """
        Finds filter class information.

        Args:
            senatt (str): Sensor attribute.
            sentyp (str): Sensor type.
            units (str): Units.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/filterclass/{senatt}/{sentyp}/{units}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def decode_by_code_name_and_code(self, code_name: str, code: str) -> APIResponse:
        """
        Decodes a code by code name and code value.

        Args:
            code_name (str): The name of the code.
            code (str): The code value.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/decode/{code_name}/{code}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())
