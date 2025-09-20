from typing import TYPE_CHECKING, List, Optional, Union
from pydantic import parse_obj_as
import logging
from datetime import date

from ...lib.models import APIResponse, Error, Meta, Pagination

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class ComponentTestDatabaseAPI:
    """
    API for programmatic access to the NHTSA Component Test Database.
    Base URL: /nhtsa/component/
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the ComponentTestDatabaseAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client
        self.base_path = "/nhtsa/component" # Specific path for this API on the NRD server

    async def find_component_documents_by_test_no(self, test_no: str) -> APIResponse:
        """
        Retrieves component documents by test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-documents/test-no/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_all_test_data(self, page_number: Optional[int] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> APIResponse:
        """
        Retrieves all component test data.

        Args:
            page_number (Optional[int]): The page number for pagination.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results"
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
        Retrieves component test data by test reference number.

        Args:
            test_reference_no (str): The test reference number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/test-reference-no/{test_reference_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_test_data_by_test_no(self, test_no: str) -> APIResponse:
        """
        Retrieves component test data by test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/test-no/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_occupant_types(self) -> APIResponse:
        """
        Retrieves available occupant types for component tests.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/occupant-types"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_json_export_metadata(self, test_no: str) -> APIResponse:
        """
        Retrieves JSON export metadata for a given component test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/metadata/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_vehicle_information(self, test_no: str) -> APIResponse:
        """
        Retrieves vehicle information for a given component test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-vehicle-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_vehicle_detail_information(self, vehicle_no: str, test_no: str) -> APIResponse:
        """
        Retrieves detailed vehicle information for a specific vehicle and component test number.

        Args:
            vehicle_no (str): The vehicle number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-vehicle-detail-info/{vehicle_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_test_details(self, test_no: str) -> APIResponse:
        """
        Retrieves test details for a given component test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-test-detail/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_multimedia_files(self, test_no: str) -> APIResponse:
        """
        Retrieves multimedia files for a given component test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-multimedia-files/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_instrumentation_information(self, test_no: str, page_number: Optional[int] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> APIResponse:
        """
        Retrieves instrumentation information for a given component test number.

        Args:
            test_no (str): The test number.
            page_number (Optional[int]): The page number for pagination.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-instrumentation-info/{test_no}"
        params = {"count": count}
        if page_number is not None:
            params["pageNumber"] = page_number
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_instrumentation_detail_information(self, curve_no: str, test_no: str) -> APIResponse:
        """
        Retrieves detailed instrumentation information for a specific curve and component test number.

        Args:
            curve_no (str): The curve number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-instrumentation-detail-info/{curve_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_configuration_information(self, test_no: str) -> APIResponse:
        """
        Retrieves configuration information for a given component test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-configuration-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_configuration_detail_information(self, conf_no: str, test_no: str) -> APIResponse:
        """
        Retrieves detailed configuration information for a specific configuration and component test number.

        Args:
            conf_no (str): The configuration number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-configuration-detail-info/{conf_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_component_information(self, test_no: str) -> APIResponse:
        """
        Retrieves component information for a given component test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-component-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_component_detail_information(self, comp_no: str, test_no: str) -> APIResponse:
        """
        Retrieves detailed component information for a specific component and test number.

        Args:
            comp_no (str): The component number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/get-component-detail-info/{comp_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def search_test_data(
        self,
        page_number: Optional[int] = None,
        test_no_from: Optional[int] = None,
        test_no_to: Optional[int] = None,
        test_date_from: Optional[date] = None,
        test_date_to: Optional[date] = None,
        occupant_type: Optional[List[str]] = None,
        test_ref_number: Optional[str] = None,
        test_type: Optional[str] = None,
        contract: Optional[str] = None,
        test_performer: Optional[str] = None,
        order_by: Optional[str] = None,
        count: int = 20,
        sort_by: Optional[str] = None
    ) -> APIResponse:
        """
        Searches for component test data based on various criteria.

        Args:
            page_number (Optional[int]): The page number for pagination.
            test_no_from (Optional[int]): Test number from.
            test_no_to (Optional[int]): Test number to.
            test_date_from (Optional[date]): Test date from (YYYY-MM-DD).
            test_date_to (Optional[date]): Test date to (YYYY-MM-DD).
            occupant_type (Optional[List[str]]): List of occupant types.
            test_ref_number (Optional[str]): Test reference number (supports pattern search).
            test_type (Optional[str]): Test type.
            contract (Optional[str]): Contract (supports pattern search).
            test_performer (Optional[str]): Test performer.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/component-database-test-results/by-search"
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
        if occupant_type:
            params["occupantType"] = occupant_type
        if test_ref_number:
            params["testRefNumber"] = test_ref_number
        if test_type:
            params["testType"] = test_type
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
