from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging
from datetime import date

from ...lib.models import APIResponse, Error, Meta, Pagination

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class BiomechanicsTestDatabaseAPI:
    """
    API for programmatic access to the NHTSA Biomechanics Test Database.
    Base URL: /nhtsa/biomechanics/
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the BiomechanicsTestDatabaseAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client
        self.base_path = "/nhtsa/biomechanics" # Specific path for this API on the NRD server

    async def find_biomechanics_documents_by_test_no(self, test_no: str) -> APIResponse:
        """
        Retrieves biomechanics documents by test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-documents/test-no/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_all_test_data(self, page_number: Optional[int] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> APIResponse:
        """
        Retrieves all biomechanics test data.

        Args:
            page_number (Optional[int]): The page number for pagination.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results"
        params = {"count": count}
        if page_number is not None:
            params["pageNumber"] = page_number
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_test_data_by_test_reference_no(self, test_reference_no: str) -> APIResponse:
        """
        Retrieves biomechanics test data by test reference number.

        Args:
            test_reference_no (str): The test reference number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/test-reference-no/{test_reference_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_test_data_by_test_no(self, test_no: str) -> APIResponse:
        """
        Retrieves biomechanics test data by test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/test-no/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_occupant_types(self) -> APIResponse:
        """
        Retrieves available occupant types for biomechanics tests.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/occupant-types"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_json_export_metadata(self, test_no: str) -> APIResponse:
        """
        Retrieves JSON export metadata for a given biomechanics test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/metadata/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_test_details(self, test_no: str) -> APIResponse:
        """
        Retrieves test details for a given biomechanics test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-test-detail/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_restraint_information(self, test_no: str) -> APIResponse:
        """
        Retrieves restraint information for a given biomechanics test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-restraint-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_multimedia_files(self, test_no: str) -> APIResponse:
        """
        Retrieves multimedia files for a given biomechanics test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-multimedia-files/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_instrumentation_information(self, test_no: str, page_number: Optional[int] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> APIResponse:
        """
        Retrieves instrumentation information for a given biomechanics test number.

        Args:
            test_no (str): The test number.
            page_number (Optional[int]): The page number for pagination.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-instrumentation-info/{test_no}"
        params = {"count": count}
        if page_number is not None:
            params["pageNumber"] = page_number
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_instrumentation_detail_information(self, curve_no: int, test_no: int) -> APIResponse:
        """
        Retrieves detailed instrumentation information for a specific curve and biomechanics test number.

        Args:
            curve_no (int): The curve number.
            test_no (int): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-instrumentation-detail-info/{curve_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_dummy_occupant_information(self, test_no: str) -> APIResponse:
        """
        Retrieves dummy occupant information for a given biomechanics test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-dummy-occupant-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_biological_occupant_information(self, test_no: str) -> APIResponse:
        """
        Retrieves biological occupant information for a given biomechanics test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/get-biological-occupant-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def search_test_data(
        self,
        page_number: Optional[int] = None,
        test_no_from: Optional[int] = None,
        test_no_to: Optional[int] = None,
        test_date_from: Optional[date] = None,
        test_date_to: Optional[date] = None,
        impact_angle_from: Optional[int] = None,
        impact_angle_to: Optional[int] = None,
        closing_speed_from: Optional[float] = None,
        closing_speed_to: Optional[float] = None,
        test_configuration: Optional[str] = None,
        test_ref_number: Optional[str] = None,
        occupant_type: Optional[List[str]] = None,
        contract: Optional[str] = None,
        test_performer: Optional[str] = None,
        order_by: Optional[str] = None,
        count: int = 20,
        sort_by: Optional[str] = None
    ) -> APIResponse:
        """
        Searches for biomechanics test data based on various criteria.

        Args:
            page_number (Optional[int]): The page number for pagination.
            test_no_from (Optional[int]): Test number from.
            test_no_to (Optional[int]): Test number to.
            test_date_from (Optional[date]): Test date from (YYYY-MM-DD).
            test_date_to (Optional[date]): Test date to (YYYY-MM-DD).
            impact_angle_from (Optional[int]): Impact angle from.
            impact_angle_to (Optional[int]): Impact angle to.
            closing_speed_from (Optional[float]): Closing speed from.
            closing_speed_to (Optional[float]): Closing speed to.
            test_configuration (Optional[str]): Test configuration.
            test_ref_number (Optional[str]): Test reference number (supports pattern search).
            occupant_type (Optional[List[str]]): List of occupant types.
            contract (Optional[str]): Contract (supports pattern search).
            test_performer (Optional[str]): Test performer.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/biomechanics-database-test-results/by-search"
        params = {"count": count}
        if page_number is not None:
            params["pageNumber"] = page_number
        if test_no_from is not None:
            params["testNoFrom"] = test_no_from
        if test_no_to is not None:
            params["testNoTo"] = test_no_to
        if test_date_from:
            params["testDateFrom"] = test_date_from.isoformat()
        if test_date_to:
            params["testDateTo"] = test_date_to.isoformat()
        if impact_angle_from is not None:
            params["impactAngleFrom"] = impact_angle_from
        if impact_angle_to is not None:
            params["impactAngleTo"] = impact_angle_to
        if closing_speed_from is not None:
            params["closingSpeedFrom"] = closing_speed_from
        if closing_speed_to is not None:
            params["closingSpeedTo"] = closing_speed_to
        if test_configuration:
            params["testConfiguration"] = test_configuration
        if test_ref_number:
            params["testRefNumber"] = test_ref_number
        if occupant_type:
            params["occupantType"] = occupant_type
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
