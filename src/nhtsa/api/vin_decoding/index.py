from typing import TYPE_CHECKING, List, Optional, Union
from pydantic import parse_obj_as
import logging

from .models import (
    VinDecodeResult, VinDecodeFlatResult, VinDecodeExtendedResult,
    VinDecodeExtendedFlatResult, WmiDecodeResult, WmiForManufacturerResult,
    AllMakesResult, PartsResult, AllManufacturersResult, ManufacturerDetailsResult,
    MakeForManufacturerResult, MakesForManufacturerAndYearResult, MakesForVehicleTypeResult,
    VehicleTypesForMakeResult, VehicleTypesForMakeIdResult, EquipmentPlantCodeResult,
    ModelsForMakeResult, ModelsForMakeIdResult, ModelsForMakeYearResult,
    VehicleVariableListResult, VehicleVariableValuesListResult, DecodeVinBatchResult,
    CanadianVehicleSpecificationsResult, BaseNHTSAResponse
)

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class VinDecodingAPI:
    """
    API for decoding Vehicle Identification Numbers (VINs) and related vehicle information.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the VinDecodingAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def decode_vin(self, vin: str, model_year: Optional[int] = None) -> VinDecodeResult:
        """
        Decodes the VIN and returns the output as Key-value pairs.

        Args:
            vin (str): The VIN to decode. Supports partial VINs (less than 17 characters).
            model_year (Optional[int]): The vehicle's model year (recommended for accuracy).

        Returns:
            VinDecodeResult: A Pydantic model representing the decoded VIN in key-value pairs.
        """
        params = {"format": "json"}
        if model_year:
            params["modelyear"] = model_year
        url = f"/vehicles/DecodeVin/{vin}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VinDecodeResult, response.json())

    async def decode_vin_flat_format(self, vin: str, model_year: Optional[int] = None) -> VinDecodeFlatResult:
        """
        Decodes the VIN and returns the output in a flat file format.

        Args:
            vin (str): The VIN to decode. Supports partial VINs.
            model_year (Optional[int]): The vehicle's model year (recommended for accuracy).

        Returns:
            VinDecodeFlatResult: A Pydantic model representing the decoded VIN in a flat format.
        """
        params = {"format": "json"}
        if model_year:
            params["modelyear"] = model_year
        url = f"/vehicles/DecodeVinValues/{vin}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VinDecodeFlatResult, response.json())

    async def decode_vin_extended(self, vin: str, model_year: Optional[int] = None) -> VinDecodeExtendedResult:
        """
        Decodes the VIN and provides additional information on variables related to other NHTSA programs.

        Args:
            vin (str): The VIN to decode. Supports partial VINs.
            model_year (Optional[int]): The vehicle's model year (recommended for accuracy).

        Returns:
            VinDecodeExtendedResult: A Pydantic model representing the decoded VIN with extended information.
        """
        params = {"format": "json"}
        if model_year:
            params["modelyear"] = model_year
        url = f"/vehicles/DecodeVinExtended/{vin}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VinDecodeExtendedResult, response.json())

    async def decode_vin_extended_flat_format(self, vin: str, model_year: Optional[int] = None) -> VinDecodeExtendedFlatResult:
        """
        Decodes the VIN with extended information and returns the output in a flat format.

        Args:
            vin (str): The VIN to decode. Supports partial VINs.
            model_year (Optional[int]): The vehicle's model year (recommended for accuracy).

        Returns:
            VinDecodeExtendedFlatResult: A Pydantic model representing the decoded VIN with extended information in a flat format.
        """
        params = {"format": "json"}
        if model_year:
            params["modelyear"] = model_year
        url = f"/vehicles/DecodeVinValuesExtended/{vin}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VinDecodeExtendedFlatResult, response.json())

    async def decode_wmi(self, wmi: str) -> WmiDecodeResult:
        """
        Provides information on the World Manufacturer Identifier (WMI) for a specific WMI code.

        Args:
            wmi (str): The WMI code (3 or 6 characters).

        Returns:
            WmiDecodeResult: A Pydantic model representing the decoded WMI information.
        """
        params = {"format": "json"}
        url = f"/vehicles/DecodeWMI/{wmi}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(WmiDecodeResult, response.json())

    async def get_wmis_for_manufacturer(self, manufacturer: str, vehicle_type: Optional[str] = None) -> WmiForManufacturerResult:
        """
        Provides information on all World Manufacturer Identifiers (WMI) for a specified Manufacturer.

        Args:
            manufacturer (str): Manufacturer's name (partial or full) or ID.
            vehicle_type (Optional[str]): Vehicle type name (partial or full) or ID to filter by.

        Returns:
            WmiForManufacturerResult: A Pydantic model representing a list of WMIs for the manufacturer.
        """
        params = {"format": "json"}
        if vehicle_type:
            params["vehicleType"] = vehicle_type
        url = f"/vehicles/GetWMIsForManufacturer/{manufacturer}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(WmiForManufacturerResult, response.json())

    async def get_all_makes(self) -> AllMakesResult:
        """
        Provides a list of all the Makes available in the vPIC Dataset.

        Returns:
            AllMakesResult: A Pydantic model representing a list of all makes.
        """
        params = {"format": "json"}
        url = "/vehicles/GetAllMakes"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(AllMakesResult, response.json())

    async def get_parts(self, type: int, from_date: Optional[str] = None, to_date: Optional[str] = None, manufacturer: Optional[str] = None, page: int = 1) -> PartsResult:
        """
        Provides a list of ORGs with letter date in the given range of the dates and with specified Type of ORG.

        Args:
            type (int): 565 (VIN Guidance) or 566 (Manufacturer Identification).
            from_date (Optional[str]): ORG's Letter Date should be on or after this date (MM/DD/YYYY).
            to_date (Optional[str]): ORG's Letter Date should be on or before this date (MM/DD/YYYY).
            manufacturer (Optional[str]): Manufacturer's name (partial or full) or ID.
            page (int): Page number for results (default 1, 1000 records per page).

        Returns:
            PartsResult: A Pydantic model representing a list of parts information.
        """
        params = {"type": type, "format": "json", "page": page}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if manufacturer:
            params["manufacturer"] = manufacturer
        url = "/vehicles/GetParts"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(PartsResult, response.json())

    async def get_all_manufacturers(self, manufacturer_type: Optional[Union[str, int]] = None, page: int = 1) -> AllManufacturersResult:
        """
        Returns a list of all the Manufacturers available in vPIC Dataset.

        Args:
            manufacturer_type (Optional[Union[str, int]]): Manufacturer Type to filter by (e.g., "Intermediate" or ID).
            page (int): Page number for results (default 1, 100 items per page).

        Returns:
            AllManufacturersResult: A Pydantic model representing a list of manufacturers.
        """
        params = {"format": "json", "page": page}
        if manufacturer_type:
            params["ManufacturerType"] = manufacturer_type
        url = "/vehicles/GetAllManufacturers"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(AllManufacturersResult, response.json())

    async def get_manufacturer_details(self, manufacturer: Union[str, int], page: int = 1) -> ManufacturerDetailsResult:
        """
        Provides the details for a specific manufacturer(s).

        Args:
            manufacturer (Union[str, int]): Manufacturer's name (partial or full) or ID.
            page (int): Page number for results (default 1, 100 items per page if manufacturer is a string).

        Returns:
            ManufacturerDetailsResult: A Pydantic model representing the manufacturer details.
        """
        params = {"format": "json"}
        if isinstance(manufacturer, str) and not manufacturer.isdigit():
            params["page"] = page
        url = f"/vehicles/GetManufacturerDetails/{manufacturer}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(ManufacturerDetailsResult, response.json())

    async def get_makes_for_manufacturer(self, manufacturer: Union[str, int]) -> MakeForManufacturerResult:
        """
        Returns all the Makes in the vPIC dataset for a specified manufacturer.

        Args:
            manufacturer (Union[str, int]): Manufacturer's name (partial or full) or ID.

        Returns:
            MakeForManufacturerResult: A Pydantic model representing a list of makes for the manufacturer.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetMakeForManufacturer/{manufacturer}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(MakeForManufacturerResult, response.json())

    async def get_makes_for_manufacturer_and_year(self, manufacturer: Union[str, int], year: int) -> MakesForManufacturerAndYearResult:
        """
        Returns all the Makes in the vPIC dataset for a specified manufacturer and
        whose Year From and Year To range cover the specified year.

        Args:
            manufacturer (Union[str, int]): Manufacturer's name (partial or full) or ID.
            year (int): The year to filter by.

        Returns:
            MakesForManufacturerAndYearResult: A Pydantic model representing a list of makes for the manufacturer and year.
        """
        params = {"format": "json", "year": year}
        url = f"/vehicles/GetMakesForManufacturerAndYear/{manufacturer}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(MakesForManufacturerAndYearResult, response.json())

    async def get_makes_for_vehicle_type(self, vehicle_type_name: str) -> MakesForVehicleTypeResult:
        """
        Returns all the Makes in the vPIC dataset for a specified vehicle type whose name is LIKE the vehicle type name.

        Args:
            vehicle_type_name (str): Vehicle type name (partial or full).

        Returns:
            MakesForVehicleTypeResult: A Pydantic model representing a list of makes for the vehicle type.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetMakesForVehicleType/{vehicle_type_name}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(MakesForVehicleTypeResult, response.json())

    async def get_vehicle_types_for_make(self, make_name: str) -> VehicleTypesForMakeResult:
        """
        Returns all the Vehicle Types in the vPIC dataset for a specified Make whose name is LIKE the make name.

        Args:
            make_name (str): Make name (partial or full).

        Returns:
            VehicleTypesForMakeResult: A Pydantic model representing a list of vehicle types for the make.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetVehicleTypesForMake/{make_name}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VehicleTypesForMakeResult, response.json())

    async def get_vehicle_types_for_make_id(self, make_id: int) -> VehicleTypesForMakeIdResult:
        """
        Returns all the Vehicle Types in the vPIC dataset for a specified Make whose ID equals the make ID.

        Args:
            make_id (int): The ID of the make.

        Returns:
            VehicleTypesForMakeIdResult: A Pydantic model representing a list of vehicle types for the make ID.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetVehicleTypesForMakeId/{make_id}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VehicleTypesForMakeIdResult, response.json())

    async def get_equipment_plant_codes(self, year: int, equipment_type: Optional[int] = None, report_type: Optional[str] = None) -> EquipmentPlantCodeResult:
        """
        Returns assigned Equipment Plant Codes. Can be filtered by Year, Equipment Type and Report Type.

        Args:
            year (int): Only years 2016 and above are supported.
            equipment_type (Optional[int]): Equipment type (e.g., 1 for Tires).
            report_type (Optional[str]): Report type (e.g., "New", "Updated", "Closed", "All").

        Returns:
            EquipmentPlantCodeResult: A Pydantic model representing a list of equipment plant codes.
        """
        params = {"format": "json", "year": year}
        if equipment_type:
            params["equipmentType"] = equipment_type
        if report_type:
            params["reportType"] = report_type
        url = "/vehicles/GetEquipmentPlantCodes"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(EquipmentPlantCodeResult, response.json())

    async def get_models_for_make(self, make_name: str) -> ModelsForMakeResult:
        """
        Returns the Models in the vPIC dataset for a specified Make whose name is LIKE the Make.

        Args:
            make_name (str): Make name (partial or full, or "*" for all makes).

        Returns:
            ModelsForMakeResult: A Pydantic model representing a list of models for the make.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetModelsForMake/{make_name}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(ModelsForMakeResult, response.json())

    async def get_models_for_make_id(self, make_id: int) -> ModelsForMakeIdResult:
        """
        Returns the Models in the vPIC dataset for a specified Make whose Id is EQUAL the MakeId.

        Args:
            make_id (int): The ID of the make (or 0 for all makes).

        Returns:
            ModelsForMakeIdResult: A Pydantic model representing a list of models for the make ID.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetModelsForMakeId/{make_id}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(ModelsForMakeIdResult, response.json())

    async def get_models_for_make_year(self, make_name: str, model_year: Optional[int] = None, vehicle_type: Optional[str] = None) -> ModelsForMakeYearResult:
        """
        Returns the Models in the vPIC dataset for a specified year and Make.

        Args:
            make_name (str): Make name (partial or full).
            model_year (Optional[int]): Model year (greater than 1995).
            vehicle_type (Optional[str]): Vehicle type name (partial or full).

        Returns:
            ModelsForMakeYearResult: A Pydantic model representing a list of models.
        """
        params = {"format": "json"}
        url_segments = []
        if make_name:
            url_segments.append(f"make/{make_name}")
        if model_year:
            url_segments.append(f"modelyear/{model_year}")
        if vehicle_type:
            url_segments.append(f"vehicletype/{vehicle_type}")

        url = f"/vehicles/GetModelsForMakeYear/{'/'.join(url_segments)}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(ModelsForMakeYearResult, response.json())

    async def get_models_for_make_id_year(self, make_id: int, model_year: Optional[int] = None, vehicle_type: Optional[str] = None) -> ModelsForMakeYearResult:
        """
        Returns the Models in the vPIC dataset for a specified year and Make ID.

        Args:
            make_id (int): The ID of the make.
            model_year (Optional[int]): Model year (greater than 1995).
            vehicle_type (Optional[str]): Vehicle type name (partial or full).

        Returns:
            ModelsForMakeYearResult: A Pydantic model representing a list of models.
        """
        params = {"format": "json"}
        url_segments = []
        url_segments.append(f"makeId/{make_id}")
        if model_year:
            url_segments.append(f"modelyear/{model_year}")
        if vehicle_type:
            url_segments.append(f"vehicletype/{vehicle_type}")

        url = f"/vehicles/GetModelsForMakeIdYear/{'/'.join(url_segments)}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(ModelsForMakeYearResult, response.json())

    async def get_vehicle_variable_list(self) -> VehicleVariableListResult:
        """
        Provides a list of all the Vehicle related variables that are in vPIC dataset.

        Returns:
            VehicleVariableListResult: A Pydantic model representing a list of vehicle variables.
        """
        params = {"format": "json"}
        url = "/vehicles/GetVehicleVariableList"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VehicleVariableListResult, response.json())

    async def get_vehicle_variable_values_list(self, variable_search_param: Union[str, int]) -> VehicleVariableValuesListResult:
        """
        Provides a list of all the accepted values for a given variable that are stored in vPIC dataset.

        Args:
            variable_search_param (Union[str, int]): Variable Name (full name) or Variable ID.

        Returns:
            VehicleVariableValuesListResult: A Pydantic model representing a list of variable values.
        """
        params = {"format": "json"}
        url = f"/vehicles/GetVehicleVariableValuesList/{variable_search_param}"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(VehicleVariableValuesListResult, response.json())

    async def decode_vin_batch(self, data: str) -> DecodeVinBatchResult:
        """
        Decodes a batch of VINs that are submitted in a standardized format in a string to return multiple decodes.

        Args:
            data (str): The input string in the format "vin,modelYear;vin,modelYear;...".

        Returns:
            DecodeVinBatchResult: A Pydantic model representing the decoded VINs in a batch.
        """
        post_fields = {'format': 'json', 'data': data}
        url = "/vehicles/DecodeVINValuesBatch/"
        response = await self.client._request("POST", url, data=post_fields, use_vpic_client=True)
        return parse_obj_as(DecodeVinBatchResult, response.json())

    async def get_canadian_vehicle_specifications(self, year: int, make: str, model: Optional[str] = None, units: Optional[str] = None) -> CanadianVehicleSpecificationsResult:
        """
        The Canadian Vehicle Specifications (CVS) consists of a database of original vehicle dimensions.

        Args:
            year (int): Number, >= 1971.
            make (str): Vehicle's make, like "Honda", "Toyota".
            model (Optional[str]): Vehicle's model, like "Pilot", "Focus".
            units (Optional[str]): "Metric" (default), or "US" for United States customary units.

        Returns:
            CanadianVehicleSpecificationsResult: A Pydantic model representing Canadian vehicle specifications.
        """
        params = {"format": "json", "Year": year, "Make": make}
        if model:
            params["Model"] = model
        if units:
            params["units"] = units
        url = "/vehicles/GetCanadianVehicleSpecifications/"
        response = await self.client._request("GET", url, params=params, use_vpic_client=True)
        return parse_obj_as(CanadianVehicleSpecificationsResult, response.json())
