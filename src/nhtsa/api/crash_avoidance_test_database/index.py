
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from pydantic import parse_obj_as
import logging
from datetime import datetime

from ...lib.models import APIResponse, Error, Meta, Pagination
from .models import NhtsaCaDbTestData, CurveData

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class CrashAvoidanceTestDatabaseAPI:
    """
    API for programmatic access to the NHTSA Crash Avoidance Test Database (CADB).
    Base URL: /nhtsa/cadb/
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the CrashAvoidanceTestDatabaseAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client
        self.base_path = "/nhtsa/cadb" # Specific path for this API on the NRD server

    async def get_test_data_by_id(self, test_id: int) -> NhtsaCaDbTestData:
        """
        Retrieves test data for a specific test ID.

        Args:
            test_id (int): The ID of the test.

        Returns:
            NhtsaCaDbTestData: A Pydantic model representing the test data.
        """
        url = f"{self.base_path}/api/v1/{test_id}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(NhtsaCaDbTestData, response.json())

    async def get_section_data(self, test_id: int, section: str) -> NhtsaCaDbTestData:
        """
        Retrieves data for a specific section within a test ID.

        Args:
            test_id (int): The ID of the test.
            section (str): The section name.

        Returns:
            NhtsaCaDbTestData: A Pydantic model representing the test data for the section.
        """
        url = f"{self.base_path}/api/v1/getsectiondata/{test_id}/{section}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(NhtsaCaDbTestData, response.json())

    async def get_all_test_data(self) -> List[NhtsaCaDbTestData]:
        """
        Retrieves all crash avoidance test data.

        Returns:
            List[NhtsaCaDbTestData]: A list of Pydantic models representing all test data.
        """
        url = f"{self.base_path}/api/v1/ca-database-test-results"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(List[NhtsaCaDbTestData], response.json())

    async def get_all_documents(self, test_id: int) -> Dict[str, List[Any]]:
        """
        Retrieves all documents for a given test ID.

        Args:
            test_id (int): The ID of the test.

        Returns:
            Dict[str, List[Any]]: A dictionary where keys are document categories and values are lists of documents.
        """
        url = f"{self.base_path}/api/v1/ca-database-test-results/documents/{test_id}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(Dict[str, List[Any]], response.json())

    async def get_all_curve_data_for_test(self, test_id: int) -> List[CurveData]:
        """
        Retrieves all curve data for a given test ID.

        Args:
            test_id (int): The ID of the test.

        Returns:
            List[CurveData]: A list of Pydantic models representing curve data.
        """
        url = f"{self.base_path}/api/v1/ca-database-test-results/curve-data/{test_id}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(List[CurveData], response.json())

    async def get_all_curve_data_for_test_and_curve(self, test_id: int, curve_no: int) -> CurveData:
        """
        Retrieves all curve data for a specific test ID and curve number.

        Args:
            test_id (int): The ID of the test.
            curve_no (int): The curve number.

        Returns:
            CurveData: A Pydantic model representing the curve data.
        """
        url = f"{self.base_path}/api/v1/ca-database-test-results/curve-data/{test_id}/{curve_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(CurveData, response.json())

    async def search_test_data(
        self,
        page_number: Optional[int] = None,
        test_date_from: Optional[datetime] = None,
        test_date_to: Optional[datetime] = None,
        model_year_from: Optional[int] = None,
        model_year_to: Optional[int] = None,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        test_no_from: Optional[int] = None,
        test_no_to: Optional[int] = None,
        test_configuration: Optional[str] = None,
        title: Optional[str] = None,
        vehicle_classification: Optional[str] = None,
        test_ref_number: Optional[str] = None,
        test_type: Optional[str] = None,
        target_type: Optional[str] = None,
        contract: Optional[str] = None,
        test_performer: Optional[str] = None,
        order_by: Optional[str] = None,
        count: int = 20,
        sort_by: Optional[str] = None
    ) -> APIResponse:
        """
        Searches for crash avoidance test data based on various criteria.

        Args:
            page_number (Optional[int]): The page number for pagination.
            test_date_from (Optional[datetime]): Test date from (ISO 8601 format).
            test_date_to (Optional[datetime]): Test date to (ISO 8601 format).
            model_year_from (Optional[int]): Model year from.
            model_year_to (Optional[int]): Model year to.
            vehicle_make (Optional[str]): Vehicle make.
            vehicle_model (Optional[str]): Vehicle model.
            test_no_from (Optional[int]): Test number from.
            test_no_to (Optional[int]): Test number to.
            test_configuration (Optional[str]): Test configuration.
            title (Optional[str]): Title.
            vehicle_classification (Optional[str]): Vehicle classification.
            test_ref_number (Optional[str]): Test reference number (supports pattern search).
            test_type (Optional[str]): Test type.
            target_type (Optional[str]): Target type.
            contract (Optional[str]): Contract (supports pattern search).
            test_performer (Optional[str]): Test performer.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/ca-database-test-results/by-search"
        params = {"count": count}
        if page_number is not None:
            params["pageNumber"] = page_number
        if test_date_from:
            params["testDateFrom"] = test_date_from.isoformat()
        if test_date_to:
            params["testDateTo"] = test_date_to.isoformat()
        if model_year_from is not None:
            params["modelYearFrom"] = model_year_from
        if model_year_to is not None:
            params["modelYearTo"] = model_year_to
        if vehicle_make:
            params["vehicleMake"] = vehicle_make
        if vehicle_model:
            params["vehicleModel"] = vehicle_model
        if test_no_from is not None:
            params["testNoFrom"] = test_no_from
        if test_no_to is not None:
            params["testNoTo"] = test_no_to
        if test_configuration:
            params["testConfiguration"] = test_configuration
        if title:
            params["title"] = title
        if vehicle_classification:
            params["vehicleClassification"] = vehicle_classification
        if test_ref_number:
            params["testRefNumber"] = test_ref_number
        if test_type:
            params["testType"] = test_type
        if target_type:
            params["targetType"] = target_type
        if contract:
            params["contract"] = contract
        if test_performer:
            params["testPerformer"] = test_performer
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by

        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())
