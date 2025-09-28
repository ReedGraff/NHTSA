from typing import TYPE_CHECKING, List, Optional, Union
from pydantic import parse_obj_as
import logging
from datetime import date, datetime

from .models import (
    VehicleByYmmtResult, VehicleDetailsResult, VehicleByVinProxyResult,
    VehicleSearchResult, TireSearchResult, EquipmentSearchResult,
    ChildSeatsResult, ChildSeatModesResult, ChildSeatBySearchResult
)

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class ProductsAPI:
    """
    API for querying various NHTSA product information, including vehicles, tires,
    equipment, and child seats. This consolidates data from multiple product-focused
    endpoints within the main NHTSA API.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the ProductsAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    # --- Vehicle Endpoints ---

    async def get_vehicle_by_ymmt(
        self,
        model_year: int,
        make: str,
        model: str,
        trim: Optional[str] = None,
        series: Optional[str] = None,
        name: Optional[str] = None, # Unclear what 'name' refers to in byYmmt, often empty
        data: Optional[str] = "crashtestratings,safetyfeatures,recommendedfeatures", # Comma-separated list of data to include, unclear all options
        product_detail: Optional[str] = "all" # 'minimal' or 'all'
    ) -> VehicleByYmmtResult:
        """
        Retrieves vehicle information and safety details by Year, Make, Model, Trim.

        Args:
            model_year (int): The model year of the vehicle.
            make (str): The make of the vehicle.
            model (str): The model of the vehicle.
            trim (Optional[str]): The trim level of the vehicle.
            series (Optional[str]): The series of the vehicle.
            name (Optional[str]): Additional name component.
            data (Optional[str]): Comma-separated list of data to include (e.g., "crashtestratings,safetyfeatures,recommendedfeatures").
            product_detail (Optional[str]): Level of product detail ("minimal" or "all").

        Returns:
            VehicleByYmmtResult: A Pydantic model representing the vehicle details.
        """
        url = f"/vehicles/byYmmt"
        params = {
            "modelYear": model_year,
            "make": make,
            "model": model,
            "data": data,
            "productDetail": product_detail
        }
        if trim:
            params["trim"] = trim
        if series:
            params["series"] = series
        if name: # The example showed 'name=' empty, so it might be optional and sometimes passed.
            params["name"] = name
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(VehicleByYmmtResult, response.json())

    async def get_vehicle_details_by_id(
        self,
        vehicle_id: int,
        data: Optional[str] = "complaints,recalls,investigations,manufacturercommunications",
        product_detail: Optional[str] = "minimal", # 'minimal' or 'all'
        name: Optional[str] = None # Unclear what 'name' refers to here.
    ) -> VehicleDetailsResult:
        """
        Retrieves detailed information (including safety issues) for a specific vehicle ID.

        Args:
            vehicle_id (int): The unique ID of the vehicle.
            data (Optional[str]): Comma-separated list of safety issues to include.
            product_detail (Optional[str]): Level of product detail ("minimal" or "all").
            name (Optional[str]): Additional name component.

        Returns:
            VehicleDetailsResult: A Pydantic model representing the vehicle's safety issue details.
        """
        url = f"/vehicles/{vehicle_id}/details"
        params = {
            "data": data,
            "productDetail": product_detail
        }
        if name:
            params["name"] = name
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(VehicleDetailsResult, response.json())

    async def get_vehicle_by_vin_proxy(
        self,
        vin: str,
        timestamp: int,
        key: int,
        # token: str, # This requires a captcha token, handled by raising NotImplementedError
        product_detail: Optional[str] = "all",
        data: Optional[str] = "none" # Default to 'none' as per example
    ) -> VehicleByVinProxyResult:
        """
        Retrieves vehicle information by VIN using a proxy endpoint that typically
        requires a captcha token. This method will raise NotImplementedError.

        Args:
            vin (str): The VIN to look up.
            timestamp (int): A timestamp required by the API.
            key (int): A key required by the API.
            # token (str): The captcha token.
            product_detail (Optional[str]): Level of product detail ("minimal" or "all").
            data (Optional[str]): Comma-separated list of data to include.

        Returns:
            VehicleByVinProxyResult: A Pydantic model representing the vehicle information.

        Raises:
            NotImplementedError: This endpoint currently requires a captcha token
                                 which is not handled by the SDK.
        """
        # Construct URL for demonstration/error raising
        url = f"/vehicles/byVinProxy"
        params = {
            "vin": vin,
            "timestamp": timestamp,
            "key": key,
            "productDetail": product_detail,
            "data": data
        }
        # if token:
        #     params["token"] = token # Add token if available, but we'll raise anyway
        
        # This endpoint uses a CAPTCHA. Raising an error as per instructions.
        # In a real-world scenario, you would integrate a CAPTCHA solver here.
        raise NotImplementedError(
            "The 'byVinProxy' endpoint requires a Google reCAPTCHA token "
            "which is not currently handled by this SDK. "
            "URL built: https://api.nhtsa.gov" + url + "?" + "&".join([f"{k}={v}" for k,v in params.items()])
        )
        # response = await self.client._request("GET", url, params=params)
        # return parse_obj_as(VehicleByVinProxyResult, response.json())

    async def search_vehicles(
        self,
        query: str,
        offset: int = 0,
        max_results: int = 10,
        sort_by: Optional[str] = "overallRating",
        order: Optional[str] = "desc", # 'asc' or 'desc'
        data: Optional[str] = "crashtestratings,recommendedfeatures,safetyfeatures",
        date_start: Optional[Union[str, date, datetime]] = None,
        date_end: Optional[Union[str, date, datetime]] = None,
        product_detail: Optional[str] = "all", # 'minimal' or 'all'
        vehicle_class: Optional[str] = None, # Filter from 'filters' in response, e.g., 'TRUCK'
    ) -> VehicleSearchResult:
        """
        Searches for vehicles based on a query string and various filters, including safety data.

        Args:
            query (str): The search query (e.g., "chevrolet colorado").
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 10).
            sort_by (Optional[str]): Field to sort the results by (e.g., "overallRating", "make").
            order (Optional[str]): Sort order ("asc" or "desc").
            data (Optional[str]): Comma-separated list of data to include (e.g., "crashtestratings,safetyfeatures,recommendedfeatures").
            date_start (Optional[Union[str, date, datetime]]): Start date for filtering (YYYY-MM-DD).
            date_end (Optional[Union[str, date, datetime]]): End date for filtering (YYYY-MM-DD).
            product_detail (Optional[str]): Level of product detail ("minimal" or "all").
            vehicle_class (Optional[str]): Filter by vehicle class (e.g., "TRUCK", "PASSENGER CAR").

        Returns:
            VehicleSearchResult: A Pydantic model representing the search results.
        """
        url = f"/vehicles/bySearch"
        params = {
            "query": query,
            "offset": offset,
            "max": max_results,
            "sort": sort_by,
            "order": order,
            "data": data,
            "productDetail": product_detail
        }
        if date_start:
            if isinstance(date_start, date) or isinstance(date_start, datetime):
                params["dateStart"] = date_start.isoformat()
            else:
                params["dateStart"] = date_start
        if date_end:
            if isinstance(date_end, date) or isinstance(date_end, datetime):
                params["dateEnd"] = date_end.isoformat()
            else:
                params["dateEnd"] = date_end
        if vehicle_class:
            params["vehicleClass"] = vehicle_class
        
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(VehicleSearchResult, response.json())


    # --- Tire Endpoints ---

    async def search_tires(
        self,
        query: str,
        data_set: Optional[str] = "safetyIssues", # "ratings" or "safetyIssues"
        offset: int = 0,
        max_results: int = 10,
        sort_by: Optional[str] = "productName",
        order: Optional[str] = "asc", # 'asc' or 'desc'
        data: Optional[str] = "none" # "modes" etc.
    ) -> TireSearchResult:
        """
        Searches for tires based on a query string.

        Args:
            query (str): The search query (e.g., "goodyear wrangler").
            data_set (Optional[str]): The dataset to query ("ratings" or "safetyIssues").
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 10).
            sort_by (Optional[str]): Field to sort the results by (e.g., "productName").
            order (Optional[str]): Sort order ("asc" or "desc").
            data (Optional[str]): Additional data to include (e.g., "modes" for child seats, "none" for tires if not specified).

        Returns:
            TireSearchResult: A Pydantic model representing the tire search results.
        """
        url = f"/tires/bySearch"
        params = {
            "query": query,
            "dataSet": data_set,
            "offset": offset,
            "max": max_results,
            "sort": sort_by,
            "order": order,
            "data": data
        }
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(TireSearchResult, response.json())

    # --- Equipment Endpoints ---

    async def search_equipment(
        self,
        query: str,
        offset: int = 0,
        max_results: int = 10,
        sort_by: Optional[str] = "productName",
        order: Optional[str] = "asc", # 'asc' or 'desc'
        data: Optional[str] = "all" # e.g. "all" or specific fields
    ) -> EquipmentSearchResult:
        """
        Searches for equipment based on a query string.

        Args:
            query (str): The search query (e.g., "seatbelts").
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 10).
            sort_by (Optional[str]): Field to sort the results by (e.g., "productName").
            order (Optional[str]): Sort order ("asc" or "desc").
            data (Optional[str]): Additional data to include (e.g., "all").

        Returns:
            EquipmentSearchResult: A Pydantic model representing the equipment search results.
        """
        url = f"/equipment/bySearch"
        params = {
            "query": query,
            "offset": offset,
            "max": max_results,
            "sort": sort_by,
            "order": order,
            "data": data
        }
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(EquipmentSearchResult, response.json())


    # --- Child Seat Endpoints ---

    async def get_child_seats(
        self,
        data: Optional[str] = "modes", # e.g., "modes"
        data_set: Optional[str] = "ratings", # e.g., "ratings"
        weight: Optional[int] = None,
        height: Optional[int] = None,
        offset: int = 0,
        max_results: int = 10,
        sort_by: Optional[str] = "make",
        order: Optional[str] = "asc", # 'asc' or 'desc'
    ) -> ChildSeatsResult:
        """
        Retrieves child seat information, optionally filtered by weight and height.

        Args:
            data (Optional[str]): Data to include (e.g., "modes").
            data_set (Optional[str]): Dataset to query (e.g., "ratings").
            weight (Optional[int]): Child's weight in pounds.
            height (Optional[int]): Child's height in inches.
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 10).
            sort_by (Optional[str]): Field to sort the results by (e.g., "make").
            order (Optional[str]): Sort order ("asc" or "desc").

        Returns:
            ChildSeatsResult: A Pydantic model representing the child seat information.
        """
        url = f"/childSeats"
        params = {
            "offset": offset,
            "max": max_results,
            "sort": sort_by,
            "order": order,
            "data": data,
            "dataSet": data_set
        }
        if weight is not None:
            params["weight"] = weight
        if height is not None:
            params["height"] = height
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(ChildSeatsResult, response.json())

    async def get_child_seat_modes(
        self,
        offset: int = 0,
        max_results: int = 20,
        sort_by: Optional[str] = "id",
        order: Optional[str] = None # 'asc' or 'desc'
    ) -> ChildSeatModesResult:
        """
        Retrieves a list of available child seat modes.

        Args:
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 20).
            sort_by (Optional[str]): Field to sort the results by (e.g., "id").
            order (Optional[str]): Sort order ("asc" or "desc").

        Returns:
            ChildSeatModesResult: A Pydantic model representing the list of child seat modes.
        """
        url = f"/childSeats/modes"
        params = {
            "offset": offset,
            "max": max_results,
            "sort": sort_by
        }
        if order:
            params["order"] = order
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(ChildSeatModesResult, response.json())

    async def search_child_seats(
        self,
        query: str,
        data: Optional[str] = "modes", # e.g., "modes"
        data_set: Optional[str] = "ratings", # e.g., "ratings"
        offset: int = 0,
        max_results: int = 10,
        sort_by: Optional[str] = "make",
        order: Optional[str] = "asc", # 'asc' or 'desc'
    ) -> ChildSeatBySearchResult:
        """
        Searches for child seats based on a query string.

        Args:
            query (str): The search query (e.g., "chicco").
            data (Optional[str]): Data to include (e.g., "modes").
            data_set (Optional[str]): Dataset to query (e.g., "ratings").
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 10).
            sort_by (Optional[str]): Field to sort the results by (e.g., "make").
            order (Optional[str]): Sort order ("asc" or "desc").

        Returns:
            ChildSeatBySearchResult: A Pydantic model representing the child seat search results.
        """
        url = f"/childSeats/bySearch"
        params = {
            "query": query,
            "offset": offset,
            "max": max_results,
            "sort": sort_by,
            "order": order,
            "data": data,
            "dataSet": data_set
        }
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(ChildSeatBySearchResult, response.json())
