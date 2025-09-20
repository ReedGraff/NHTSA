from typing import TYPE_CHECKING, List, Optional, Union
from pydantic import parse_obj_as
import logging
from datetime import date

from ...lib.models import APIResponse, Error, Meta, Pagination
from .models import (
    VehicleDocument, VehicleTestData, VehicleModel, OccupantType, VehicleMetadata,
    VehicleInformation, VehicleDetailInformation, TestDetail, RestraintInformation,
    OccupantInformation, OccupantDetailInformation, MultimediaFile, IntrusionInformation,
    InstrumentationInformation, InstrumentationDetailInformation, BarrierInformation,
    VehicleInformationResponse, BarrierInformationResponse
)

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class VehicleCrashTestDatabaseAPI:
    """
    API for programmatic access to the NHTSA Vehicle Crash Test Database.
    Base URL: /nhtsa/vehicle/
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the VehicleCrashTestDatabaseAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client
        self.base_path = "/nhtsa/vehicle" # Specific path for this API on the NRD server

    async def find_vehicle_documents_by_test_no(self, test_no: str) -> APIResponse:
        """
        Retrieves vehicle documents by test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-documents/test-no/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_all_test_data(self, page_number: Optional[int] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> APIResponse:
        """
        Retrieves all vehicle test data.

        Args:
            page_number (Optional[int]): The page number for pagination.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results"
        params = {"count": count}
        if page_number is not None:
            params["pageNumber"] = page_number
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_distinct_vehicle_models(self, vehicle_make: Optional[str] = None) -> APIResponse:
        """
        Retrieves distinct vehicle models.

        Args:
            vehicle_make (Optional[str]): Filter by vehicle make.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/vehicleModels"
        params = {}
        if vehicle_make:
            params["vehicleMake"] = vehicle_make
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_test_data_by_test_reference_no(self, test_reference_no: str) -> APIResponse:
        """
        Retrieves test data by test reference number.

        Args:
            test_reference_no (str): The test reference number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/test-reference-no/{test_reference_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def find_test_data_by_test_no(self, test_no: str) -> APIResponse:
        """
        Retrieves test data by test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/test-no/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_occupant_types(self) -> APIResponse:
        """
        Retrieves available occupant types.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/occupant-types"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_json_export_metadata(self, test_no: str) -> APIResponse:
        """
        Retrieves JSON export metadata for a given test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/metadata/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_vehicle_information(self, test_no: str) -> APIResponse:
        """
        Retrieves vehicle information for a given test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-vehicle-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_vehicle_detail_information(self, vehicle_no: str, test_no: str) -> APIResponse:
        """
        Retrieves detailed vehicle information for a given vehicle and test number.

        Args:
            vehicle_no (str): The vehicle number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-vehicle-detail-info/{vehicle_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_test_details(self, test_no: str) -> APIResponse:
        """
        Retrieves test details for a given test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-test-detail/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_restraint_information(self, vehicle_no: str, test_no: str, occupant_location: str) -> APIResponse:
        """
        Retrieves restraint information for a specific vehicle, test, and occupant location.

        Args:
            vehicle_no (str): The vehicle number.
            test_no (str): The test number.
            occupant_location (str): The occupant location.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-restraint-info/{vehicle_no}/{test_no}/{occupant_location}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_occupant_information(self, veh_no: str, test_no: str) -> APIResponse:
        """
        Retrieves occupant information for a specific vehicle and test number.

        Args:
            veh_no (str): The vehicle number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-occupant-info/{veh_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_all_occupant_information_for_vehicle(self, test_no: str) -> APIResponse:
        """
        Retrieves all occupant information for a given vehicle test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-occupant-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_occupant_detail_information(self, veh_no: str, test_no: str, occ_loc: str) -> APIResponse:
        """
        Retrieves detailed occupant information for a specific vehicle, test, and occupant location.

        Args:
            veh_no (str): The vehicle number.
            test_no (str): The test number.
            occ_loc (str): The occupant location.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-occupant-detail-information/{veh_no}/{test_no}/{occ_loc}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_multimedia_files(self, test_no: str) -> APIResponse:
        """
        Retrieves multimedia files for a given test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-multimedia-files/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_intrusion_info(self, veh_no: str, test_no: str) -> APIResponse:
        """
        Retrieves intrusion information for a specific vehicle and test number.

        Args:
            veh_no (str): The vehicle number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-intrusion-info/{veh_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_instrumentation_information(self, test_no: str, page_number: Optional[int] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> APIResponse:
        """
        Retrieves instrumentation information for a given test number.

        Args:
            test_no (str): The test number.
            page_number (Optional[int]): The page number for pagination.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-instrumentation-info/{test_no}"
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
        Retrieves detailed instrumentation information for a specific curve and test number.

        Args:
            curve_no (str): The curve number.
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-instrumentation-detail-info/{curve_no}/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def get_barrier_information(self, test_no: str) -> APIResponse:
        """
        Retrieves barrier information for a given test number.

        Args:
            test_no (str): The test number.

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/get-barrier-info/{test_no}"
        response = await self.client._request("GET", url, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def search_test_data(
        self,
        page_number: Optional[int] = None,
        test_date_from: Optional[date] = None,
        test_date_to: Optional[date] = None,
        model_year_from: Optional[int] = None,
        model_year_to: Optional[int] = None,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        test_no_from: Optional[int] = None,
        test_no_to: Optional[int] = None,
        impact_angle_from: Optional[int] = None,
        impact_angle_to: Optional[int] = None,
        offset_distance_from: Optional[int] = None,
        offset_distance_to: Optional[int] = None,
        closing_speed_from: Optional[float] = None,
        closing_speed_to: Optional[float] = None,
        test_configuration: Optional[str] = None,
        occupant_type: Optional[List[str]] = None,
        test_ref_number: Optional[str] = None,
        test_type: Optional[str] = None,
        contract: Optional[str] = None,
        test_performer: Optional[str] = None,
        exclude_nhtsa_vehicles: Optional[bool] = None,
        order_by: Optional[str] = None,
        count: int = 20,
        sort_by: Optional[str] = None
    ) -> APIResponse:
        """
        Searches for vehicle test data based on various criteria.

        Args:
            page_number (Optional[int]): The page number for pagination.
            test_date_from (Optional[date]): Test date from (YYYY-MM-DD).
            test_date_to (Optional[date]): Test date to (YYYY-MM-DD).
            model_year_from (Optional[int]): Model year from.
            model_year_to (Optional[int]): Model year to.
            vehicle_make (Optional[str]): Vehicle make.
            vehicle_model (Optional[str]): Vehicle model.
            test_no_from (Optional[int]): Test number from.
            test_no_to (Optional[int]): Test number to.
            impact_angle_from (Optional[int]): Impact angle from.
            impact_angle_to (Optional[int]): Impact angle to.
            offset_distance_from (Optional[int]): Offset distance from.
            offset_distance_to (Optional[int]): Offset distance to.
            closing_speed_from (Optional[float]): Closing speed from.
            closing_speed_to (Optional[float]): Closing speed to.
            test_configuration (Optional[str]): Test configuration.
            occupant_type (Optional[List[str]]): List of occupant types (supports pattern search).
            test_ref_number (Optional[str]): Test reference number (supports pattern search).
            test_type (Optional[str]): Test type.
            contract (Optional[str]): Contract (supports pattern search).
            test_performer (Optional[str]): Test performer.
            exclude_nhtsa_vehicles (Optional[bool]): Exclude NHTSA vehicles.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            APIResponse: A Pydantic model representing the API response.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/by-search"
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
        if impact_angle_from is not None:
            params["impactAngleFrom"] = impact_angle_from
        if impact_angle_to is not None:
            params["impactAngleTo"] = impact_angle_to
        if offset_distance_from is not None:
            params["offsetDistanceFrom"] = offset_distance_from
        if offset_distance_to is not None:
            params["offsetDistanceTo"] = offset_distance_to
        if closing_speed_from is not None:
            params["closingSpeedFrom"] = closing_speed_from
        if closing_speed_to is not None:
            params["closingSpeedTo"] = closing_speed_to
        if test_configuration:
            params["testConfiguration"] = test_configuration
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
        if exclude_nhtsa_vehicles is not None:
            params["excludeNhtsaVehicles"] = exclude_nhtsa_vehicles
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by

        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(APIResponse, response.json())

    async def search_vehicle_information(self, model_year_from: Optional[int] = None, model_year_to: Optional[int] = None, vehicle_make: Optional[str] = None, vehicle_model: Optional[str] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> List[VehicleInformationResponse]:
        """
        Searches for vehicle information based on model year, make, and model.

        Args:
            model_year_from (Optional[int]): Model year from.
            model_year_to (Optional[int]): Model year to.
            vehicle_make (Optional[str]): Vehicle make.
            vehicle_model (Optional[str]): Vehicle model.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            List[VehicleInformationResponse]: A list of Pydantic models representing vehicle information.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/by-search-vehicle"
        params = {"count": count}
        if model_year_from is not None:
            params["modelYearFrom"] = model_year_from
        if model_year_to is not None:
            params["modelYearTo"] = model_year_to
        if vehicle_make:
            params["vehicleMake"] = vehicle_make
        if vehicle_model:
            params["vehicleModel"] = vehicle_model
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(List[VehicleInformationResponse], response.json())

    async def search_barrier_information(self, barrier_angle_from: Optional[int] = None, barrier_angle_to: Optional[int] = None, rigid_or_deformable: Optional[str] = None, barrier_shape: Optional[str] = None, order_by: Optional[str] = None, count: int = 20, sort_by: Optional[str] = None) -> List[BarrierInformationResponse]:
        """
        Searches for barrier information based on various criteria.

        Args:
            barrier_angle_from (Optional[int]): Barrier angle from.
            barrier_angle_to (Optional[int]): Barrier angle to.
            rigid_or_deformable (Optional[str]): Rigid or deformable barrier.
            barrier_shape (Optional[str]): Barrier shape.
            order_by (Optional[str]): Field to order the results by.
            count (int): Number of rows to return.
            sort_by (Optional[str]): Sort order ("ASC" or "DESC").

        Returns:
            List[BarrierInformationResponse]: A list of Pydantic models representing barrier information.
        """
        url = f"{self.base_path}/api/v1/vehicle-database-test-results/by-search-barrier"
        params = {"count": count}
        if barrier_angle_from is not None:
            params["barrierAngleFrom"] = barrier_angle_from
        if barrier_angle_to is not None:
            params["barrierAngleTo"] = barrier_angle_to
        if rigid_or_deformable:
            params["rigidOrDeformable"] = rigid_or_deformable
        if barrier_shape:
            params["barrierShape"] = barrier_shape
        if order_by:
            params["orderBy"] = order_by
        if sort_by:
            params["sortBy"] = sort_by
        response = await self.client._request("GET", url, params=params, use_nrd_client=True)
        return parse_obj_as(List[BarrierInformationResponse], response.json())
